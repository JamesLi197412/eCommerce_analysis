from analysis.pre_process import *
from model.XGBoost import *

def delivery_analysis(orders_customers_items,sellers,geolocation):
    # Merge multiple tables together by needs
    geolocation = geolocation.groupby("geolocation_zip_code_prefix").agg({"geolocation_lat":"mean", "geolocation_lng":"mean"}).reset_index()

    orders_customers_items = pd.merge(orders_customers_items, geolocation, left_on='customer_zip_code_prefix',
                                right_on='geolocation_zip_code_prefix')
    orders_customers_items.rename(
        columns={'geolocation_lat': 'geolocation_lat_cust', 'geolocation_lng': 'geolocation_lng_cust'}, inplace=True)

    # Seller Info
    orders_customers_sellers = pd.merge(orders_customers_items, sellers, on='seller_id', how='inner')
    orders_customers_sellers = pd.merge(orders_customers_sellers, geolocation, left_on='seller_zip_code_prefix',
                                        right_on='geolocation_zip_code_prefix')
    orders_customers_sellers.rename(
        columns={'geolocation_lat': 'geolocation_lat_seller', 'geolocation_lng': 'geolocation_lng_seller'},
        inplace=True)

    orders_customers_sellers = delivery_performance(orders_customers_sellers)

    orders_customers_sellers = delivery_prediction(orders_customers_sellers)


def delivery_performance(df):
    # 1. Order purchase timestamp vs oder approved at
    df['purchase_approved_delta'] = np.ceil(
        (df['order_approved_at'] - df['order_purchase_timestamp']) / pd.Timedelta(hours=1))

    # 2. order_estimated delivery vs order delivered customer date
    df['delivery_status'] = np.where(df['order_delivered_customer_date'] < df['order_estimated_delivery_date'],
                                     1, 0)

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
    delivered = delivered.dropna().reset_index()

    delivered['cities differences'] = np.where(delivered['customer_city'] == delivered['seller_city'], 1, 0)
    delivered['cities distances'] = (np.sqrt(((delivered["geolocation_lat_cust"] - delivered["geolocation_lat_seller"]) ** 2) +
                                          ((delivered["geolocation_lng_cust"] - delivered["geolocation_lng_seller"]) ** 2)))

    delivered['product volumn'] = delivered['product_length_cm'] * delivered['product_height_cm'] * delivered['product_width_cm']

    # Extract features
    features = ['cities distances', 'cities differences','delivery_status','purchase_approved_delta','customer_city','seller_city','product volumn','product_weight_g']
    target = ['carrier_response']

    encode_features = ['customer_city','seller_city']
    numerical_features = ['cities distances', 'cities differences','delivery_status','purchase_approved_delta','product volumn','product_weight_g']
    xgboost = XGBoostDelivery(df = delivered, features = features, target_col = target)
    pred = xgboost.model_run(encode_features, numerical_features)


    return delivered
