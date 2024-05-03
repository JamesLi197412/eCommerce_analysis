import pandas as pd
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import seaborn as sns

def order_data(df):
    """to adjust order date column in orders dataset"""
    df['order_delivered_customer_date'] = pd.to_datetime(df['order_delivered_customer_date'],errors='coerce')
    df['order_delivered_carrier_date'] = pd.to_datetime(df['order_delivered_carrier_date'],errors='coerce')
    df['order_approved_at'] = pd.to_datetime(df['order_approved_at'],errors='coerce')
    df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'],errors='coerce')
    df['order_estimated_delivery_date'] = pd.to_datetime(df['order_estimated_delivery_date'],errors='coerce')
    return df


def order_customer(orders,customers,payment):
    # One customer could have multiple orders
    orders = order_data(orders)
    orders['order_date'] = orders['order_purchase_timestamp'].dt.date
    orders_customers = orders.merge(customers, on = 'customer_id', how = 'left')
    orders_customers_payment = orders_customers.merge(payment, on = 'order_id', how = 'inner')

    # year-date-state-sales values
    date_state_sales = orders_customers_payment.groupby(['order_date','customer_state'])['payment_value'].agg(['count', 'sum']).reset_index()
    plt.figure(figsize=(12, 6))
    sns.lineplot(data = date_state_sales,x='order_date', y='sum', hue='customer_state')
    plt.title('Sales by State Over Time')
    plt.xlabel('order_date')
    plt.ylabel('Sales')
    plt.legend(title='order_date')
    plt.savefig('output/visualisation/sales_state_date.png')

    # plt.show()

    print(date_state_sales.head(10))

    # customer-city-state :: where they are from
    return date_state_sales


def rfm_analysis(df):
    df_recency = df.groupby(by='customer_unique_id')['order_purchase_timestamp'].max().reset_index()
    df_recency.columns = ['customer_unique_id', 'Last Purchase Date']
    recent_date = df_recency['Last Purchase Date'].max()

    df_recency['Recency'] = df_recency['Last Purchase Date'].apply(lambda x: (recent_date - x).days)

    frequency_df = df.drop_duplicates().groupby(by=['customer_unique_id'], as_index=False)[
        'order_purchase_timestamp'].count().reset_index()
    frequency_df.columns = ['customer_unique_id', 'Frequency']

    monetary_df = df.groupby(by=['customer_unique_id'], as_index=False)['payment_value'].sum().reset_index()
    monetary_df.columns = ['customer_unique_id', 'monetary']

    rf_df = df_recency.merge(frequency_df, on='customer_unique_id', how='inner')
    rfm_df = rf_df.merge(monetary_df, on='customer_unique_id', how='inner').drop(columns='Last Purchase Date')

    return rfm_df

def yearly_new_client(df):
    return df

def customer_lifetime(df):
    return df

