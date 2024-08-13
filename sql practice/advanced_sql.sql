USE e_commerce;

# Find out yearly,monthly new clients vs regular customer
WITH first_visit AS (
    SELECT customer_id, MIN(order_purchase_timestamp) OVER (PARTITION BY customer_id) AS first_purchase_date
    FROM orders
    GROUP BY customer_id
)

SELECT YEAR(o.order_purchase_timestamp)                                                        AS order_date,
       sum(CASE WHEN (o.order_purchase_timestamp) = fv.first_purchase_date then 1 else 0 end)  as first_visit_flag,
       sum(case when (o.order_purchase_timestamp) != fv.first_purchase_date then 1 else 0 end) as repeated_visit
FROM first_visit fv
         INNER join orders o
                    ON fv.customer_id = o.customer_id
GROUP BY YEAR(o.order_purchase_timestamp);

### YoY sales comparison with Lag
WITH yearly_sales AS (
    SELECT YEAR(o.order_purchase_timestamp) AS Years,
           SUM(p.payment_value)             AS revenue
    FROM orders o
             INNER JOIN order_payments p
                        ON o.order_id = p.order_id
    GROUP BY YEAR(o.order_purchase_timestamp)
)

SELECT Years,
       revenue,
       LAG(revenue) OVER (ORDER BY Years)           AS Revenue_Previous_Year,
       revenue - LAG(revenue) OVER (ORDER BY Years) AS YOY_Difference
FROM yearly_sales;

### Monthly Sales Comparison with Lag
WITH monthly_metrics AS (
    SELECT YEAR(o.order_purchase_timestamp)          AS years,
           MONTH(o.order_purchase_timestamp)         AS months,
           SUM(payment_value + payment_installments) AS reveune
    FROM orders o
             INNER JOIN order_payments p
                        ON o.order_id = p.order_id
    GROUP BY 1, 2
)
SELECT years                                                    AS current_year,
       months                                                   AS current_month,
       reveune                                                  AS revenue_current_month,
       LAG(years, 12) OVER ( ORDER BY years, months)            AS previous_year,
       LAG(months, 12) OVER ( ORDER BY years, months)           AS month_comparing_with,
       LAG(reveune, 12) OVER ( ORDER BY years, months)          AS revenue_12_months_ago,
       reveune - LAG(reveune, 12) OVER (ORDER BY years, months) AS month_to_month_difference
FROM monthly_metrics
ORDER BY 1, 2;


# Find out daily active customer (DAU)
SELECT t.day AS DAY, count(t.customer_unique_id) AS DAU
FROM (
         SELECT date_format(o.order_purchase_timestamp, "%d") AS day,
                c.customer_unique_id
         FROM orders as o
                  LEFT JOIN customers as c
                            ON c.customer_id = o.customer_id
         WHERE o.order_status = 'delivered'
           AND DATE_FORMAT(o.order_purchase_timestamp, "%Y-m") = '2017-09'
         GROUP BY day, c.customer_unique_id
     ) AS t
GROUP BY DAY
ORDER BY DAY;

# Medium Selling Price
SELECT AVG(order_items.price) AS Average_price,
       MAX(order_items.price) AS Max_Price,
       MIN(order_items.price) AS Min_Price
FROM order_items;

SELECT AVG(data.price) AS "Median_price"
FROM (
         SELECT order_items.price,
                ROW_NUMBER() OVER (ORDER BY price ASC, order_id ASC)      RowAsc,
                ROW_NUMBER() OVER (ORDER BY price DESC, order_id DESC) AS RowDesc
         FROM order_items
     ) AS data
WHERE RowAsc IN (RowDesc, RowDesc - 1, RowDesc + 1);
