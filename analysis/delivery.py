from analysis.pre_process import *


def delivery_analysis(orders, customers, sellers, items, products, gelocation):
    # Merge multiple tables together by needs
    orders = order_data(orders)
    orders_customers = pd.merge(orders, customers, on='customer_id', how='inner')
    del orders
    del customers

    # Customer Info
    orders_customers = pd.merge(orders_customers, gelocation, left_on='customer_zip_code_prefix',
                                right_on='geolocation_zip_code_prefix')
    orders_customers.rename(
        columns={'geolocation_lat': 'geolocation_lat_cust', 'geolocation_lng': 'geolocation_lng_cust'}, inplace=True)
    orders_customers.drop(
        columns=['geolocation_zip_code_prefix', 'geolocation_city', 'geolocation_state', 'customer_zip_code_prefix'],
        axis=1, inplace=True)

    orders_customers_items = pd.merge(orders_customers, items[
        ['order_id', 'product_id', 'seller_id', 'price', 'freight_value', 'shipping_limit_date']],
                                      on='order_id', how='left')
    del orders_customers
    del items

    # Seller Info
    orders_customers_sellers = pd.merge(orders_customers_items, sellers, on='seller_id', how='inner')
    orders_customers_sellers = pd.merge(orders_customers_sellers, gelocation, left_on='seller_zip_code_prefix',
                                        right_on='geolocation_zip_code_prefix')
    orders_customers_sellers.rename(
        columns={'geolocation_lat': 'geolocation_lat_seller', 'geolocation_lng': 'geolocation_lng_seller'},
        inplace=True)

    orders_customers_sellers.drop(
        columns=['geolocation_zip_code_prefix', 'geolocation_state', 'seller_zip_code_prefix', 'geolocation_city'],
        axis=1, inplace=True)
    del sellers

    orders_customers_sellers = orders_customers_sellers.merge(products, how='inner', on='product_id')
    del products
    return orders_customers_sellers
    # output
    orders_customers_sellers.to_csv('test2.csv')
    # orders_customers_sellers = delivery_performance(orders_customers_sellers)

    # orders_customers_sellers = delivery_prediction(orders_customers_sellers)

    # gc.collect()


def delivery_performance(df):
    # 1. Order purchase timestamp vs oder approved at
    df['purchase_approved_delta'] = np.ceil(
        (df['order_approved_at'] - df['order_purchase_timestamp']) / pd.Timedelta(hours=1))

    # 2. order_estimated delivery vs order delivered customer date
    df['delivery_status'] = np.where(df['order_delivered_customer_date'] < df['order_estimated_delivery_date'],
                                     'in_time', 'late')

    # 3. dates between order_approved_at vs order_delivered_carrier_date
    df['carrier_response'] = np.ceil((df['order_delivered_carrier_date'] - df['order_approved_at'])/pd.Timedelta(hours= 1))

    # Visualisation for these results
    # Normal distribution of delta and gap
    hist_plot(df, 'purchase_approved_delta', 'Count', 'purchase_approved_delta',path=f'output/visualisations/delivery/purchase_approved_delta.png')

    hist_plot(df, 'carrier_response', 'Count', 'carrier_response',
              path=f'output/visualisations/delivery/carrier_response.png')

    # Delivery Status
    pie_chart(df,'delivery_status','order_id',sns.color_palette('Set2'), 'Delivery Status',path=f'output/visualisations/delivery/delivery status.png')

    return df


def delivery_prediction(df):
    delivered = df[df['order_status'] == "delivered"].copy(deep=True)
    delivered = delivered.dropna().reset_inde()

    delivered['cities differences'] = np.where(delivered['customer_city'] == delivered['seller_city'], 1, 0)

    return delivered
