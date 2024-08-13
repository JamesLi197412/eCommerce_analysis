import pandas as pd


def data_process(df):
    # adjust column _date from object to datetime
    cols = ['order_delivered_carrier_date', 'order_delivered_customer_date',
            'order_estimated_delivery_date', 'shipping_limit_date',
            'review_creation_date', 'order_purchase_timestamp']
    for col in cols:
        df[col] = pd.to_datetime(df[col])

    # cleaning up name columns
    # engineering new/essential columns
    df['delivery_against_estimated'] = (
                df['order_estimated_delivery_date'] - df['order_delivered_customer_date']).dt.days
    df['order_purchase_year'] = df['order_purchase_timestamp'].dt.year
    df['order_purchase_month'] = df['order_purchase_timestamp'].dt.month
    df['order_purchase_day'] = df['order_purchase_timestamp'].dt.day
    df['order_purchase_dayofweek'] = df['order_purchase_timestamp'].dt.dayofweek
    df['order_purchase_hr'] = df['order_purchase_timestamp'].dt.hour

    return df


def local_access_df():
    # access files with relative paths
    path = 'datasets/'
    customers = pd.read_csv(path + 'olist_customers_dataset.csv')
    geolocation = pd.read_csv(path + 'olist_geolocation_dataset.csv')
    order_items = pd.read_csv(path + 'olist_order_items_dataset.csv')
    order_payment = pd.read_csv(path + 'olist_order_payments_dataset.csv')
    order_reviews = pd.read_csv(path + 'olist_order_reviews_dataset.csv')
    order_dataset = pd.read_csv(path + 'olist_orders_dataset.csv')
    products = pd.read_csv(path + 'olist_products_dataset.csv')
    sellers = pd.read_csv(path + 'olist_sellers_dataset.csv')
    product_category = pd.read_csv(path + 'product_category_name_translation.csv')

    return customers, geolocation, order_items, order_payment, order_reviews, order_dataset, products, sellers, product_category
