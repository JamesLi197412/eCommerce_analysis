USE e_commerce;

CREATE TABLE  IF NOT EXISTS customers
(
    customer_id              varchar(50)        not null ,
    customer_unique_id       varchar(50)        not null,
    customer_zip_code_prefix int                null,
    customer_city            varchar(50)        null,
    customer_state           varchar(10)        null,
    PRIMARY KEY (customer_id)
)ENGINE = InnoDB;

CREATE TABLE  IF NOT EXISTS geolocation
(
    geolocation_zip_code_prefix int    null,
    geolocation_lat             double null,
    geolocation_lng             double null,
    geolocation_city            varchar(50)   null,
    geolocation_state           varchar(10)   null
)ENGINE = InnoDB;

CREATE TABLE IF NOT EXISTS sellers
(
    seller_id              varchar(50)       not null,
    seller_zip_code_prefix int                null,
    seller_city            varchar(50)        null,
    seller_state           varchar(10)        null,
    PRIMARY KEY (seller_id)
)ENGINE = 'InnoDB';

CREATE TABLE  IF NOT EXISTS product_category_name_translation
(
    product_category_name         varchar(50) null,
    product_category_name_english varchar(50) null
)ENGINE = InnoDB;

CREATE TABLE  IF NOT EXISTS orders
(
    order_id                      varchar(50) not null primary key,
    customer_id                   varchar(50) not null,
    order_status                  varchar(20)        null,
    order_purchase_timestamp      datetime    null,
    order_approved_at             datetime    null,
    order_delivered_carrier_date  datetime    null,
    order_delivered_customer_date datetime    null,
    order_estimated_delivery_date datetime    null,
    PRIMARY KEY (order_id)
)ENGINE = InnoDB;

ALTER TABLE orders
ADD CONSTRAINT fk_order_customer_id
FOREIGN KEY (customer_id) REFERENCES customers(customer_id);

CREATE TABLE  IF NOT EXISTS order_payments
(
    order_id             varchar(50) not null,
    payment_sequential   int         null,
    payment_type         varchar(20) null,
    payment_installments int         null,
    payment_value        double      null
) ENGINE = InnoDB;

ALTER TABLE order_payments
ADD CONSTRAINT fk_payment_order_id
FOREIGN KEY (order_id) REFERENCES orders(order_id);

CREATE TABLE  IF NOT EXISTS order_reviews
(
    review_id               varchar(50) not null,
    order_id                varchar(50) not null,
    review_score            int         null,
    review_comment_title    varchar(50) null,
    review_comment_message  varchar(300)null,
    review_creation_date    datetime    null,
    review_answer_timestamp datetime    null,
    PRIMARY KEY (review_id,order_id)
)ENGINE = InnoDB;

ALTER TABLE order_reviews
ADD CONSTRAINT fk_reviews_order_id
FOREIGN KEY (order_id) REFERENCES orders(order_id);


DESCRIBE order_reviews;


CREATE TABLE  IF NOT EXISTS products
(
    product_id                 varchar(50)  not null,
    product_category_name      varchar(50)  null,
    product_name_lenght        int          null,
    product_description_lenght int          null,
    product_photos_qty         int          null,
    product_weight_g           int          null,
    product_length_cm          int          null,
    product_height_cm          int          null,
    product_width_cm           int          null,
    PRIMARY KEY (product_id)
)ENGINE = InnoDB;

DESCRIBE products;

ALTER TABLE product_category_name_translation
ADD CONSTRAINT fk_name_id
FOREIGN KEY (product_category_name) REFERENCES products(product_category_name);


CREATE TABLE  IF NOT EXISTS order_items
(
    order_id            varchar(50) not null,
    order_item_id       int         not null,
    product_id          varchar(50) not null,
    seller_id           varchar(50) not null,
    shipping_limit_date datetime        null,
    price               double      null,
    freight_value       double      null,
    PRIMARY KEY (order_item_id)
)ENGINE = InnoDB;

SELECT * FROM order_items
LIMIT 10;

DESCRIBE order_items;

ALTER TABLE order_items
ADD CONSTRAINT fk_order_items_products_id
FOREIGN KEY (product_id) REFERENCES products(product_id);

ALTER TABLE order_items
ADD CONSTRAINT fk_order_items_sellers_id
FOREIGN KEY (seller_id) REFERENCES sellers(seller_id);

ALTER TABLE order_items
ADD CONSTRAINT fk_orders_items_id
FOREIGN KEY (order_id) REFERENCES orders(order_id);

