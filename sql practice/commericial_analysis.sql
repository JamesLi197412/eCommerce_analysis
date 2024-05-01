USE e_commerce;

# Q1 Find out total sales and total orders
SELECT c.product_category_name, COUNT(a.order_id) AS Total_Orders, SUM(b.price + b.freight_value) AS Total_Sales
FROM orders AS a
INNER JOIN order_items b
ON a.order_id = b.order_id
LEFT JOIN products c
ON c.product_id = b.product_id
GROUP BY product_category_name
ORDER BY Total_Orders DESC;

# Q2 Find out # of Orders and Sales by Purchase timestamp
# EXPLAIN Query
SELECT DATE_FORMAT(order_purchase_timestamp, "%Y-%m") as date, c.customer_state AS buyer_state,
       COUNT(o.order_id) AS order_qty, SUM(i.price + i.freight_value) AS order_sales
FROM orders o
INNER JOIN order_items i
ON o.order_id = i.order_id
INNER JOIN customers c
ON o.customer_id = c.customer_id
GROUP BY date, buyer_state
ORDER BY date;

# Q3 Selling # of product by Category
SELECT a.product_category_name_english AS product, COUNT(b.product_category_name) AS qty
FROM product_category_name_translation AS a
INNER JOIN products as b
ON a.product_category_name = b.product_category_name
GROUP BY product
ORDER BY qty DESC;


# Q4 Sellers / Customer by City -- Generate Temp Table
WITH temp_sellers AS (
    SELECT a.seller_city AS seller_city,
           COUNT(b.order_id) AS sales_qty,
           COUNT(b.order_id) * 100 / SUM(COUNT(b.order_id)) OVER() AS temp_sales_percentage
    FROM sellers AS a
    LEFT JOIN order_items AS b
    ON a.seller_id = b.seller_id
    GROUP BY seller_city
    ORDER BY sales_qty DESC
)
SELECT seller_city, sales_qty, temp_sales_percentage
FROM temp_sellers;

WITH temp_customer AS(
    SELECT a.customer_city AS customer_city,
            COUNT(b.order_id) AS order_qty,
            COUNT(b.order_id) * 100 / SUM(COUNT(b.order_id)) OVER() AS temp_order_percentage
    FROM customers AS a
    LEFT JOIN orders AS b
    ON a.customer_id = b.customer_id
    GROUP BY customer_city
    ORDER BY order_qty
)
SELECT customer_city, order_qty, temp_order_percentage
FROM temp_customer;

# Q5 Find out product price (MAX, Min, AVG and Median)
SELECT AVG(order_items.price) AS Average_price,
       MAX(order_items.price) AS Max_Price,
       MIN(order_items.price) AS Min_Price
FROM order_items;

SELECT AVG(data.price) AS "Median_price"
FROM (
        SELECT order_items.price,
               ROW_NUMBER() OVER (ORDER BY price ASC, order_id ASC) RowAsc,
               ROW_NUMBER() OVER (ORDER BY price DESC, order_id DESC) AS RowDesc
        FROM order_items
     ) AS data
WHERE RowAsc IN (RowDesc, RowDesc - 1, RowDesc + 1);

# Q6. Delivery Interval (Estimate vs Actual) per Month
SELECT temp.date, temp.delivery_time as gap_estimated_actual, temp.order_qty
FROM (
    SELECT DATE_FORMAT(orders.order_purchase_timestamp, "%Y-%m") AS date,
           AVG(DATEDIFF(orders.order_estimated_delivery_date, orders.order_delivered_customer_date)) As delivery_time,
           COUNT(order_id) AS order_qty
    FROM orders
    WHERE order_status = 'delivered'
    GROUP BY date
    ORDER BY date
) temp;

# Q7. Payment Type
SELECT a.payment_type,
       COUNT(a.payment_type) AS count_pay_type,
       ROUND(SUM(a.payment_value)/ 1000000,2) AS 'value_pay_type(M)'
FROM order_payments AS a
LEFT JOIN orders As b
ON a.order_id = b.order_id
WHERE b.order_status != 'canceled'
GROUP BY a.payment_type
ORDER BY count_pay_type DESC;


# Q8. Find out score 5 count and its percentage
SELECT c.date, c.score_5, c.count_all,
        ROUND((c.score_5 ) / (count_all) * 100,2) AS percentage
FROM
    (
        SELECT DATE_FORMAT(b.review_answer_timestamp, "%Y-%m") AS date,
               SUM(CASE WHEN b.review_score = 5 THEN 1 ELSE 0 END) AS score_5,
               COUNT(DISTINCT a.order_id) AS count_all
        FROM orders a
        LEFT JOIN order_reviews b
        ON a.order_id = b.order_id
        WHERE a.order_status = 'delivered'
        GROUP BY date
    )c;

# Q9 Check # of monthly purchase from 2016 - 2018
SELECT Month as Month_no,
       CASE WHEN a.month = '01' THEN 'Jan'
            WHEN a.month = '02' THEN 'Feb'
            WHEN a.month = '03' THEN 'Mar'
            WHEN a.month = '04' THEN 'Apr'
            WHEN a.month = '05' THEN 'May'
            WHEN a.month = '06' THEN 'Jun'
            WHEN a.month = '07' THEN 'Jul'
            WHEN a.month = '08' THEN 'Aug'
            WHEN a.month = '09' THEN 'Sep'
            WHEN a.month = '10' THEN 'Oct'
            WHEN a.month = '11' THEN 'Nov'
            WHEN a.month = '12' THEN 'Feb'
            ELSE 0 END AS Month,
        SUM(CASE WHEN a.Year = 2016 THEN 1 ELSE 0 END) AS Year2016,
        SUM(CASE WHEN a.Year = 2017 THEN 1 ELSE 0 END) AS Year2017,
        SUM(CASE WHEN a.Year = 2018 THEN 1 ELSE 0 END) AS Year2018
FROM (
    SELECT customer_id, order_id, order_status, orders.order_purchase_timestamp,
           DATE_FORMAT(orders.order_purchase_timestamp, "%Y") AS YEAR,
           DATE_FORMAT(orders.order_purchase_timestamp, "%m") AS Month
    FROM orders
    WHERE order_status != 'unavailable' AND order_status != 'canceled'
    GROUP BY customer_id, order_id
    ORDER BY order_purchase_timestamp
     ) AS a
GROUP BY Month
ORDER BY Month_no ASC;

# Q10. Sales by Customer State, its product_category and order table by sales DESC
SELECT S.customer_state,
       (S.product_category_name),
       ROUND(sum(S.payment_value)/1000,2) AS 'sales(k)'
FROM (
        SELECT a.customer_id, customer_state, c.payment_value, product_category_name
        FROM customers AS a
        LEFT JOIN orders AS b
        ON a.customer_id = b.customer_id
        LEFT JOIN order_payments AS c
        ON b.order_id = c.order_id
        LEFT JOIN order_items AS d
        ON d.order_id = b.order_id
        LEFT JOIN products AS e
        ON d.product_id = e.product_id
        WHERE order_status != 'canceled' AND order_delivered_customer_date IS NOT NULL
        AND product_category_name IS NOT NULL
     ) AS S
GROUP BY customer_state, product_category_name
ORDER BY 'sales(k)' DESC;

# Q11  RFM characteristics by customer unique ID
SELECT c.customer_unique_id, MAX(DATE(a.order_purchase_timestamp)) AS R,
       COUNT(DISTINCT a.order_id) AS F,
       IFNULL(ROUND(SUM(b.payment_value),1),0) AS M
FROM orders AS a
LEFT JOIN order_payments b
ON a.order_id = b.order_id
LEFT JOIN customers AS c
ON c.customer_id = a.customer_id
WHERE order_status NOT IN('unavailable','canceled')
GROUP BY customer_unique_id
ORDER BY M,R DESC;

# Q12 Find out daily active customer (DAU)
SELECT t.day AS DAY, count(t.customer_unique_id) AS DAU
FROM
    (
        SELECT date_format(o.order_purchase_timestamp, "%Y-%M-%d") AS day,
               c.customer_unique_id
        FROM orders as o
        LEFT JOIN customers as c
        ON c.customer_id = o.customer_id
        WHERE o.order_status = 'delivered' AND DATE_FORMAT(o.order_purchase_timestamp,"%Y-m") = '2017-09'
        GROUP BY day, c.customer_unique_id
    ) AS t
GROUP BY DAY
ORDER BY DAY;

# Q15 Find out daily New User in Specific month/year e.g. 09/2017
select DATE_FORMAT(temp.september,'%m-%d') as day, count(temp.new_customer) as daily_new_user
from
    (select c.customer_unique_id as new_customer, min(DATE_FORMAT(order_purchase_timestamp,'%Y-%m-%d')) as september
     from orders as o
     left join customers as c
     on c.customer_id=o.customer_id
     where DATE_FORMAT(order_purchase_timestamp,'%Y-%m')='2017-09'
    group by c.customer_unique_id) as temp
group by temp.september
order by temp.september;

# Q16 Re-Purchase
select c.customer_unique_id as customer, min(DATE_FORMAT( o.order_purchase_timestamp,'%Y-%m-%d')) as first_purchase,
       max(DATE_FORMAT(o.order_purchase_timestamp,'%Y-%m-%d')) as latest_purchase,
       temp1.order_cnt as count_of_purchase, case when temp1.order_cnt<2 then 'N' else 'Y' end as repurchased,
       coalesce(cast(avg_repurchase_cycle as integer), 'There was no repurchase') as average_rapurchase_cycle

from orders as o

        left join customers as c
            on o.customer_id=c.customer_id
        left join (
                select cid, count(oid) as order_cnt
                from (select c1.customer_unique_id as cid, o1.order_id as oid
                    from orders as o1
                    left join customers as c1
                        on o1.customer_id=c1.customer_id
                    where o1.order_status<> 'canceled'
                    group by c1.customer_unique_id, o1.order_id) as t
                group by cid) as temp1
            on temp1.cid=c.customer_unique_id

        left join order_items as i
            on o.order_id=i.order_id

        left join products as p
            on p.product_id=i.product_id

        left join product_category_name_translation as translate
            on p.product_category_name=translate.product_category_name

        left join (
                select customer_unique_id, avg((order_purchase_timestamp)-(prev_purchase)) as avg_repurchase_cycle
                from (select c2.customer_unique_id, o2.order_purchase_timestamp,
                        lag(o2.order_purchase_timestamp) over(partition by c2.customer_unique_id order by o2.order_purchase_timestamp) as prev_purchase
                    from orders as o2
                    left join customers as c2
                        on c2.customer_id=o2.customer_id
                    where o2.order_status<> 'canceled')
                where prev_purchase <> 'None'
                group by customer_unique_id) as temp2
            on temp2.customer_unique_id=c.customer_unique_id

        where o.order_status<> 'canceled'
        group by customer
        order by count_of_purchase desc;

# Q17 Growth rate by category
        select
            category,
            coalesce(sum(case when period='2017_1st' then revenue end),'No record') as '2017_1st',
            coalesce(sum(case when period='2018_1st' then revenue end),'No record') as '2018_1st',
            round(sum(case when period='2018_1st' then revenue end)/sum(case when period='2017_1st' then revenue end)*100,2) as "growth_rate(%)"
        from
            (select ce.product_category_name_english as category,
                case when DATE_FORMAT(o.order_purchase_timestamp,'%Y-%m') between '2017-01' and '2017-06' then '2017_1st'
                    when DATE_FORMAT(o.order_purchase_timestamp,'%Y-%m') between '2018-01' and '2018-06' then '2018_1st' end as period,
                    pay.payment_value as revenue
            from order_payments as pay
            left join orders as o
                on pay.order_id=o.order_id
            left join order_items as i
                on i.order_id=o.order_id
            left join products as p
                on p.product_id=i.product_id
            left join product_category_name_translation as ce
                on p.product_category_name=ce.product_category_name

            where
                DATE_FORMAT( o.order_purchase_timestamp,'%Y-%m') between '2017-01' and '2017-06' or
                DATE_FORMAT(o.order_purchase_timestamp,'%Y-%m') between '2018-01' and '2018-06' and
                o.order_status not in ('canceled','unavailable')) as temp
        group by category
        order by "growth_rate(%)" desc;