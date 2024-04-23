USE e_commerce;

# Q1 Find out total sales and total orders
SELECT COUNT(a.order_id) AS 'Total Orders', SUM(b.price + b.freight_value) AS 'Total Sales'
FROM orders AS a
INNER JOIN order_items b
ON a.order_id = b.order_id;

# Q2 Find out # of Orders and Sales by Purchase timestamp
ALTER TABLE orders
MODIFY order_purchase_timestamp DATETIME;

SELECT YEAR(order_purchase_timestamp) AS 'Purchase_Year', MONTH(order_purchase_timestamp) AS 'Purchase Month',
       COUNT(order_id) AS order_qty
FROM orders
GROUP BY Purchase_Year, `Purchase Month`
ORDER BY Purchase_Year, `Purchase Month`;

SELECT DATE_FORMAT(a.order_approved_at,"%Y-%m") AS date, SUM(b.price) AS sales
FROM orders AS a
INNER JOIN order_items AS b
ON a.order_id = b.order_id
GROUP BY date
ORDER BY date;

# Q3 Selling product by Category
SELECT a.product_category_name_english AS product, COUNT(b.product_category_name) AS qty
FROM product_category_name_translation AS a
INNER JOIN products as b
ON a.product_category_name = b.product_category_name
GROUP BY product
ORDER BY qty DESC;


# Q4 Sellers / Customer by City
WITH temp_sellers AS (
    SELECT a.seller_city AS seller_city,
           COUNT(b.order_id) AS sales_qty,
           COUNT(b.order_id) * 100 / SUM(COUNT(b.order_id)) OVER() AS temp_sales_percentage
    FROM sellers AS a
    INNER JOIN order_items AS b
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
    INNER JOIN orders AS b
    ON a.customer_id = b.customer_id
    GROUP BY customer_city
    ORDER BY order_qty
)
SELECT *
FROM temp_customer;

# Q5 Avg, Min, and Max Products
SELECT AVG(order_items.price) AS Average_price,
       MAX(order_items.price) AS Max_Price,
       MIN(order_items.price) AS Min_Price
FROM order_items;

# Q6. Delivery Interval (Estimate vs Actual) per Month
WITH average_time AS (
    SELECT DATE_FORMAT(orders.order_delivered_customer_date, "%Y-%m") AS date,
           DATEDIFF(orders.order_estimated_delivery_date, orders.order_delivered_customer_date) As delivery_time,
           COUNT(order_id) AS qty
    FROM orders
    WHERE order_status = 'delivered'
    GROUP BY date
    ORDER BY date
)
SELECT date AS Date, delivery_time as Day, qty AS Qty
FROM average_time;



# Q7. Find out score 5 count and its percentage
SELECT c.yearmonth, c.score_5, c.count_all,
        ROUND(CAST(c.score_5 AS float) / CAST(count_all AS float) * 100,2) AS percentage
FROM
    (
        SELECT DATE_FORMAT(a.review_answer_timestamp, "%Y-%m") AS yearmonth,
               SUM(CASE WHEN a.review_score = 5 THEN 1 ELSE 0 END) AS score_5,
             COUNT(DISTINCT a.order_id) AS count_all
        FROM order_reviews a
        LEFT JOIN orders b
        ON a.order_id = b.order_id
        WHERE b.order_status = 'delivered' AND YEAR(a.review_answer_timestamp) =2018
        GROUP BY yearmonth
    )c;


# Q8
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


# Q9. Payment Type count
SELECT a.payment_type,
       COUNT(a.payment_type) AS count_pay_type,
       SUM(a.payment_value)/ 1000 AS 'value_pay_type(K)'
FROM order_payments AS a
LEFT JOIN orders As b
ON a.order_id = b.order_id
WHERE b.order_status != 'canceled' AND b.order_delivered_customer_date IS NOT NULL
GROUP BY a.payment_type
ORDER BY count_pay_type DESC;


# Q10. Category, Seller_ID, Revenue
SELECT S.product_category_name_english AS Category,
       seller_id,
       SUM(S.payment_value) AS Revenue
FROM (
        SELECT *
        FROM sellers AS a
        LEFT JOIN order_items AS b
        on a.seller_city = b.seller_id
        LEFT JOIN products AS c
        ON b.product_id = c.product_id
        LEFT JOIN product_category_name_translation AS d
        ON d.product_category_name = c.product_category_name
        LEFT JOIN order_payments AS e
        ON e.order_id = b.order_id
        LEFT JOIN orders AS f
        ON f.order_id = b.order_id
     ) AS S
WHERE S.product_category_name IS NOT NULL
AND S.order_status != 'canceled' AND S.order_delivered_customer_date IS NOT NULL
GROUP BY Category, S.seller_id
ORDER BY Category, Revenue DESC;

# Q11. Sales by Customer State and its product_category
SELECT S.customer_state,S.product_category_name, sum(S.payment_value) AS Revenue
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
ORDER BY Revenue DESC;

# Q12 # of customer & seller by state
SELECT a.state, a.num_customer, b.num_seller
FROM (
        SELECT customer_state AS state,
               COUNT(DISTINCT(customers.customer_unique_id)) AS num_customer
        FROM customers
        GROUP BY state
     ) AS a
    LEFT JOIN (
        SELECT seller_state AS state,
               COUNT(DISTINCT(seller_id)) AS num_seller
        FROM sellers
        GROUP BY state
    )AS b
    ON a.state = b.state
ORDER BY a.state, a.num_customer DESC;

# Q13 RFM
SELECT c.customer_unique_id, MAX(DATE(a.order_purchase_timestamp)) AS R,
       COUNT(DISTINCT a.order_id) AS F,
       SUM(b.payment_value) AS M
FROM orders AS a
LEFT JOIN order_payments b
ON a.order_id = b.order_id
LEFT JOIN customers AS c
ON c.customer_id = a.customer_id
WHERE order_status != 'available' AND order_status != 'canceled'
GROUP BY customer_unique_id
ORDER BY M DESC;

# Q14 Find out daily active customer (DAU)
SELECT t.day AS DAY, count(t.customer_unique_id) AS DAU
FROM
    (
        SELECT date_format(o.order_purchase_timestamp, "%d") AS day,
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