import pandas as pd
from pre_process import order_data

# 3. Delivery Estimation vs Delivery Actual
def delivery_analysis(orders,customers, sellers, items):
    # Merge multiple tables together
    orders = order_data(orders)
    orders['order_date'] = orders['order_purchase_timestamp'].dt.date
    orders['order_month'] = orders['order_purchase_timestamp'].dt.month
    orders_customers = orders.merge(customers, on='customer_id', how='left')
    orders_customers_items = orders_customers.merge(items, on='order_id', how='left')
    orders_customers_sellers = orders_customers_items.merge(sellers, how='inner', on='seller_id')

    orders_customers_sellers = delivery_performance(orders_customers_sellers)

    orders_customers_sellers = delivery_prediction(orders_customers_sellers)


    return orders_customers_sellers

def delivery_performance(df):
    # 1. Order purchase timestamp vs oder approved at
    df['purchase_approved_delta'] = (df['order_approved_at'] - df['order_purchase_timestamp']).dt.hr

    # 2. order_estimated delivery vs order delivered customer date
    # df['delivery result'] =

    # 3. dates between order_approved_at vs order_delivered_carrier_date

    return df


def delivery_prediction(df):

    return df