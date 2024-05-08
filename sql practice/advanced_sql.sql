USE e_commerce;
# Find out yearly,monthly new clients vs regular customer


# Yearly, monthly sales comparison -- Lag/ Lead


# Find out daily active customer (DAU)
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

# Medium Selling Price
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
