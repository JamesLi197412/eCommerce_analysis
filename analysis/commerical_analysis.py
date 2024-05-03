import pandas as pd
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import scipy.stats as stats

def order_data(df):
    """to adjust order date column in orders dataset"""
    df['order_delivered_customer_date'] = pd.to_datetime(df['order_delivered_customer_date'],errors='coerce')
    df['order_delivered_carrier_date'] = pd.to_datetime(df['order_delivered_carrier_date'],errors='coerce')
    df['order_approved_at'] = pd.to_datetime(df['order_approved_at'],errors='coerce')
    df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'],errors='coerce')
    df['order_estimated_delivery_date'] = pd.to_datetime(df['order_estimated_delivery_date'],errors='coerce')
    return df

def geolocation_sales(orders_customers_payment,geolocation):
    # geolocation could be state or city by your needs,e.g. customer_state, customer_city
    # Find out top 5 states by accumulated sales
    state_sales = orders_customers_payment.groupby([geolocation])['payment_value'].agg(['sum']).reset_index()
    state_sales = state_sales.sort_values(by = 'sum', ascending= False)
    top_n_states = state_sales[geolocation][:5]

    # sales-state-date values
    date_state_sales = orders_customers_payment.groupby(['order_date',geolocation])['payment_value'].agg(['count', 'sum']).reset_index()
    top_n_sales = date_state_sales[date_state_sales[geolocation].isin(top_n_states)]
    plt.figure(figsize=(12, 6))
    sns.lineplot(data = top_n_sales,x='order_date', y='sum', hue=geolocation)
    plt.title(f'Sales by {geolocation} Over Date')
    plt.xlabel('order_date')
    plt.ylabel('Sales')
    plt.legend(title=geolocation)
    plt.savefig(f'output/visualisation/sales_{geolocation}_date.png')

    # sales-state-month sales
    month_state_sales = orders_customers_payment.groupby(['order_month',geolocation])['payment_value'].agg(['count', 'sum']).reset_index()
    top_n_sales_month = month_state_sales[month_state_sales[geolocation].isin(top_n_states)]
    plt.figure(figsize=(12, 6))
    sns.lineplot(data = top_n_sales_month,x='order_month', y='sum', hue=geolocation)
    plt.title(f'Sales by {geolocation} Over months')
    plt.xlabel('order_month')
    plt.ylabel('Sales')
    plt.legend(title= geolocation)
    plt.savefig(f'output/visualisation/sales_{geolocation}_month.png')

def order_customer(orders,customers,payment,items,products):
    # One customer could have multiple orders
    orders = order_data(orders)
    orders['order_date'] = orders['order_purchase_timestamp'].dt.date
    orders['order_month'] = orders['order_purchase_timestamp'].dt.month
    orders_customers = orders.merge(customers, on = 'customer_id', how = 'left')
    orders_customers_payment = orders_customers.merge(payment, on = 'order_id', how = 'inner')

    # sales-state/city-date/month values
    #geolocation_sales(orders_customers_payment, 'customer_state')
    #geolocation_sales(orders_customers_payment, 'customer_city')

    # payment analysis (portion, price distribution, what products paid by each type)
    orders_customers_items = orders_customers_payment.merge(items, on='order_id', how='left')
    orders_customers_items = orders_customers_items.merge(products, on = 'product_id', how = 'inner')
    #payment_analysis(orders_customers_payment)

    print(orders_customers_items.columns)


    # Customer analysis
    rfm_customer = rfm_analysis(orders_customers_items)
    #rfm_customer['Frequency'].plot(kind='box')
    sns.kdeplot(rfm_customer['Frequency'], bw_adjust= 0.5)
    plt.show()
    #normal_dist(rfm_customer['Frequency'])

    # From the plot, it shows SP has the highest sales over the time.
    # In addition, there is a high spike on one specific point.
    # to find out its speciality, then -- Black Friday
    """
    SP_sales = top_n_sales[top_n_sales['customer_state'] == 'SP'].copy(deep = True)
    SP_point = SP_sales.sort_values(by = 'sum', ascending= False)
    print(SP_point.head())
    """

    print(orders_customers_payment.columns)


    return orders_customers_payment

def payment_distribution(df):

    return None

def normal_dist(df):
    # Calculating mean and Stdev of col


    # Calculating probability density function (PDF)
    df.plot(kind='density')
    plt.show()




def payment_analysis(orders_customers_payment):
    payments = orders_customers_payment.groupby(['payment_type'])['payment_value'].agg(['count', 'sum']).reset_index()
    # print(payments.head(5))
    fig, (ax1, ax2) = plt.subplots(nrows=1, ncols=2, figsize=(20, 15))
    fig.suptitle('Payment Type Count & Sum')
    ax1.pie(payments['count'], labels=payments['payment_type'], autopct='%1.2f%%', startangle=90,
            colors=sns.color_palette('Set2'), labeldistance=0.5, pctdistance=0.6)
    ax1.set_title('Payment Type Count')
    ax2.pie(payments['sum'], labels=payments['payment_type'], autopct='%1.2f%%', startangle=90,
            colors=sns.color_palette('Set1'), labeldistance=0.5, pctdistance=0.6)
    ax2.set_title('Payment Type Sum')
    plt.tight_layout()
    plt.savefig(f'output/visualisation/payment type count & sum in general.png')


def rfm_analysis(df):
    df = df.drop_duplicates()
    df_recency = df.groupby(by='customer_unique_id')['order_purchase_timestamp'].max().reset_index()
    df_recency.columns = ['customer_unique_id', 'Last Purchase Date']
    recent_date = df_recency['Last Purchase Date'].max()

    df_recency['Recency'] = df_recency['Last Purchase Date'].apply(lambda x: (recent_date - x).days)

    frequency_df = df.groupby(by=['customer_unique_id'])['order_purchase_timestamp'].count().reset_index()
    frequency_df.columns = ['customer_unique_id', 'Frequency']

    monetary_df = df.groupby(by=['customer_unique_id'], as_index=True)['payment_value'].sum().reset_index()
    monetary_df.columns = ['customer_unique_id', 'Monetary']

    # merging montery, frequency, recency
    rf_df = df_recency.merge(frequency_df, on='customer_unique_id', how='inner')
    rfm_df = rf_df.merge(monetary_df, on='customer_unique_id', how='inner').drop(columns='Last Purchase Date')
    rfm_df = rfm_df.sort_values(by = ['Frequency','Monetary'], ascending = False)

    return rfm_df

def yearly_new_client(df):
    return df

def customer_lifetime(df):
    return df

