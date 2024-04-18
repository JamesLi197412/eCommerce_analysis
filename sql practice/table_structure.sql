USE e_commerce;

DESCRIBE order_reviews;

SHOW TABLES;

DESCRIBE customers;

## Generate primary key for each tables
SELECT * FROM customers LIMIT 10;

ALTER TABLE customers
MODIFY customer_id VARCHAR(50);

ALTER TABLE customers
ADD PRIMARY KEY (customer_id);

SELECT * FROM geolocation LIMIT 500;

SELECT * FROM geolocation
WHERE geolocation_zip_code_prefix = 1046;

DESCRIBE orders;

ALTER TABLE orders
MODIFY order_id VARCHAR(50),
ADD PRIMARY KEY (order_id);


SELECT * FROM order_reviews
LIMIT 10;

DESCRIBE order_reviews;

ALTER TABLE order_reviews
MODIFY review_id VARCHAR(50);

DESCRIBE products;

SELECT * FROM sellers
LIMIT 20;

ALTER TABLE products
MODIFY product_id VARCHAR(50),
ADD PRIMARY KEY (product_id);

ALTER TABLE sellers
MODIFY seller_id VARCHAR(50),
ADD PRIMARY KEY (seller_id);

SELECT * FROM order_reviews
LIMIT 10;

SELECT * FROM order_reviews
WHERE review_comment_title is NULL
AND review_score = 5;

SELECT * FROM orders
WHERE order_delivered_carrier_date is NULL;

commit;

DESCRIBE orders;

DESCRIBE order_reviews;
ALTER TABLE order_reviews
MODIFY order_id VARCHAR(50);

DESCRIBE order_payments;
ALTER TABLE order_payments
MODIFY order_id VARCHAR(50);

DESCRIBE customers;
DESCRIBE orders;
ALTER TABLE orders
MODIFY customer_id VARCHAR(50);

# Add Foreign key between tables to establish relationship between them
ALTER TABLE order_reviews ADD CONSTRAINT fk_reviews_id FOREIGN KEY (order_id) REFERENCES orders(order_id);

ALTER TABLE order_payments ADD CONSTRAINT fk_order_id FOREIGN KEY (order_id) REFERENCES orders(order_id);

ALTER TABLE orders ADD CONSTRAINT fk_customer_id FOREIGN KEY (customer_id) REFERENCES customers(customer_id);

DESCRIBE sellers;


DESCRIBE order_items;
ALTER TABLE order_items
MODIFY order_id VARCHAR(50),
MODIFY product_id VARCHAR(50),
MODIFY seller_id VARCHAR(50);

ALTER TABLE order_items ADD CONSTRAINT fk_order_item_id FOREIGN KEY (order_id) REFERENCES orders(order_id);
ALTER TABLE order_items ADD CONSTRAINT fk_order_product_id FOREIGN KEY (product_id) REFERENCES products(product_id);
ALTER TABLE order_items ADD CONSTRAINT fk_order_seller_id FOREIGN KEY (seller_id) REFERENCES sellers(seller_id);
COMMIT;

# Insert values into product_category_name table and check it
SELECT * FROM product_category_name_translation;
INSERT INTO product_category_name_translation(
         product_category_name,
         product_category_name_english
)VALUES(
        'Elektroauto',
        'electric auto'
);

SELECT * FROM product_category_name_translation
WHERE product_category_name_english = 'electric auto'

