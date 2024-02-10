
import pandas as pd

def data_process():
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

    # Data Merge by relationship chart
    orders = order_dataset.merge(order_items, on = 'order_id', how = 'left')  # 1 to many relationship because 1 order might have multiple items.
    orders = orders.merge(order_payment, how = 'inner', on = 'order_id')
    orders = orders.merge(order_reviews, how = 'inner', on = 'order_id')
    orders = orders.merge(products, how = 'inner', on = 'product_id')
    orders = orders.merge(sellers, how = 'inner', on = 'seller_id')


    geolocation.rename(columns = {'geolocation_zip_code_prefix':'customer_zip_code_prefix'},inplace = True)
    customers_loc = customers.merge(geolocation, how ='inner', on = 'customer_zip_code_prefix')
    customers_order = customers_loc.merge(orders, how = 'left', on = 'customer_id')

    customers_order = customers_order.merge(product_category, how = 'inner', on = 'product_category_name')


    return customers_order