
import pandas as pd
def data_process(df):
    # adjust column _date from object to datetime
    cols = ['order_delivered_carrier_date','order_delivered_customer_date',
            'order_estimated_delivery_date','shipping_limit_date',
            'review_creation_date','order_purchase_timestamp']
    for col in cols:
        df[col] = pd.to_datetime(df[col])

    # cleaning up name columns
    # engineering new/essential columns
    df['delivery_against_estimated'] = (df['order_estimated_delivery_date'] - df['order_delivered_customer_date']).dt.days
    df['order_purchase_year'] = df['order_purchase_timestamp'].dt.year
    df['order_purchase_month'] = df['order_purchase_timestamp'].dt.month
    df['order_purchase_day'] = df['order_purchase_timestamp'].dt.day
    df['order_purchase_dayofweek'] = df['order_purchase_timestamp'].dt.dayofweek
    df['order_purchase_hr'] = df['order_purchase_timestamp'].dt.hour

    return df

def local_access_df():
    # access files
    path = 'dataset/'
    customers = pd.read_csv(path + 'olist_customers_dataset.csv')
    geolocation = pd.read_csv(path + 'olist_geolocation_dataset.csv')
    order_items = pd.read_csv(path + 'olist_order_items_dataset.csv')
    order_payment = pd.read_csv(path + 'olist_order_payments_dataset.csv')
    order_reviews = pd.read_csv(path + 'olist_order_reviews_dataset.csv')
    order_dataset = pd.read_csv(path + 'olist_orders_dataset.csv')
    products = pd.read_csv(path + 'olist_products_dataset.csv')
    sellers = pd.read_csv(path + 'olist_sellers_dataset.csv')
    product_category = pd.read_csv(path + 'product_category_name_translation.csv')

    '''
    # Data Merge by relationship chart
    # rename geolocation column geolocation_zip_code - > customer_zip_code
    temp = geolocation.copy(deep = True)
    temp.rename(columns = {'geolocation_zip_code_prefix':'customer_zip_code_prefix'},inplace = True)
    customers_loc = customers.merge(temp, how ='inner', on = 'customer_zip_code_prefix')
    del temp

    orders = order_dataset.merge(order_items, on = 'order_id', how = 'left')  # 1 to many relationship because 1 order might have multiple items.
    orders = orders.merge(order_payment, how = 'inner', on = 'order_id')
    orders = orders.merge(order_reviews, how = 'inner', on = 'order_id')
    orders = orders.merge(products, how = 'inner', on = 'product_id')
    orders = orders.merge(product_category, how = 'inner', on = 'product_category_name')

    # drop columns
    orders = orders.drop(['product_category_name'], axis = 1, errors = 'ignore')

    # Except geolocation dataset
    customers_order = customers_loc.merge(orders, how = 'left', on = 'customer_id')
    customers_order = data_process(customers_order)
    '''

    return customers,geolocation,order_items,order_payment, order_reviews,order_dataset,products, sellers,product_category