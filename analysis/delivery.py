import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from analysis.pre_process import *

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
    df['purchase_approved_delta'] = np.ceil((df['order_approved_at'] - df['order_purchase_timestamp'])/pd.Timedelta(hours= 1))

    # 2. order_estimated delivery vs order delivered customer date
    df['delivery_status'] = np.where(df['order_delivered_customer_date'] < df['order_estimated_delivery_date'], 'in_time', 'late')

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

    return df

def pie_chart(dataframe, col,target,color,title,path):
    plt.figure(figsize=(10,5), dpi = 100)
    target_df = dataframe.groupby([col])[target].agg(['count']).reset_index()

    plt.pie(target_df['count'],labels = target_df[col],
            autopct='%1.2f%%', startangle=45, colors=sns.color_palette(color),
            labeldistance=0.75, pctdistance=0.4)
    plt.title(title, fontsize = 20)
    plt.axis('off')
    plt.legend()
    plt.savefig(path)

def hist_plot(df, xlabel, ylabel, title,path):
    plt.hist(df[xlabel], color='blue', edgecolor='black',
             bins=int(180 / 5))

    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)

    plt.show()
    plt.savefig(path)
