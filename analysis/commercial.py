import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import squarify
from analysis.pre_process import *


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
    plt.savefig(f'output/visualisation/commercial/sales_{geolocation}_date.png')

    # sales-state-month sales
    month_state_sales = orders_customers_payment.groupby(['order_month',geolocation])['payment_value'].agg(['count', 'sum']).reset_index()
    top_n_sales_month = month_state_sales[month_state_sales[geolocation].isin(top_n_states)]
    plt.figure(figsize=(12, 6))
    sns.lineplot(data = top_n_sales_month,x='order_month', y='sum', hue=geolocation)
    plt.title(f'Sales by {geolocation} Over months')
    plt.xlabel('order_month')
    plt.ylabel('Sales')
    plt.legend(title= geolocation)
    plt.savefig(f'output/visualisation/commercial/sales_{geolocation}_month.png')

def order_customer(orders,customers,payment,items,products,product_category):
    # One customer could have multiple orders
    orders = order_data(orders)
    orders['order_date'] = orders['order_purchase_timestamp'].dt.date
    orders['order_month'] = orders['order_purchase_timestamp'].dt.month
    orders_customers = orders.merge(customers, on = 'customer_id', how = 'left')
    orders_customers_payment = orders_customers.merge(payment, on = 'order_id', how = 'inner')

    # To-do list: 
    # 2. Conversion Rate

    # sales-state/city-date/month values
    #geolocation_sales(orders_customers_payment, 'customer_state')
    #geolocation_sales(orders_customers_payment, 'customer_city')

    # From the plot, it shows SP has the highest sales over the time.
    # In addition, there is a high spike on one specific point.
    # to find out its speciality, then -- Black Friday
    """
        SP_sales = top_n_sales[top_n_sales['customer_state'] == 'SP'].copy(deep = True)
        SP_point = SP_sales.sort_values(by = 'sum', ascending= False)
        print(SP_point.head())
    """

    # payment analysis (portion, price distribution, what products paid by each type)
    orders_customers_items = orders_customers_payment.merge(items, on='order_id', how='left')
    orders_customers_items = orders_customers_items.merge(products, on = 'product_id', how = 'inner')
    orders_customers_items = orders_customers_items.merge(product_category, how = 'inner', on = 'product_category_name')

    # Product category and its treemap
    # popular_category(orders_customers_items,'product_category_name_english')

    # Customer analysis
    rfm_customer = rfm_analysis(orders_customers_items)
    # Pie chart to show portion of customer who bought products on Olist
    # pie_chart(rfm_customer, 'Frequency', 'customer_unique_id', 'Set2', 'Customer Portion in General')

    # Split customer into two parts
    customer_regular = rfm_customer[rfm_customer['Frequency'] >1].copy(deep = True)
    customer_once = rfm_customer[rfm_customer['Frequency'] == 1].copy(deep = True)


    customer_once = customer_once.merge(orders_customers_items, how = 'inner', on = 'customer_unique_id')
    # customer who bought once -- 1. City/State location   2. Product Category Popularity
    # 3.
    # City/ State bar chart
    # customer_once_analysis(customer_once)

    # Regular Customers
    customer_regular = customer_regular.merge(orders_customers_items,how = 'inner', on = 'customer_unique_id')
    customer_regular['RN'] = customer_regular.sort_values(['order_date'], ascending = [True])\
                                 .groupby(['customer_unique_id']).cumcount() + 1
    customer_regular.sort_values(by = ['customer_unique_id','RN'], ascending= [True, True], inplace= True)

    # DAU (Daily Active User)


    return orders_customers_items

def customer_once_analysis(df):
    bar_plot(df)
    product_popularity(df)


def bar_plot(df):
    city_df = df.groupby(['customer_state'])['customer_unique_id'].agg(['count']).reset_index().sort_values(by = 'count', ascending= False)
    sns.barplot(
        city_df, x="count", y="product_category_name",
        errorbar=("pi", 50), capsize=.4,
        err_kws={"color": ".5", "linewidth": 2.5},
        linewidth=2.5, edgecolor=".5", facecolor=(0, 0, 0, 0),
    )
    plt.savefig(f'output/visualisation/commercial/city bar.png')

def product_popularity(df):
    product_df = df.groupby(['product_category_name'])['customer_unique_id'].agg(['count']).reset_index().sort_values(by = 'count', ascending= False)
    sns.barplot(
        product_df, x="count", y="product_category_name",
        errorbar=("pi", 50), capsize=.4,
        err_kws={"color": ".5", "linewidth": 2.5},
        linewidth=2.5, edgecolor=".5", facecolor=(0, 0, 0, 0),
    )
    plt.savefig(f'output/visualisation/commercial/product popularity.png')


def distribution_plt(dataframe,column_name,title,xlabel,ylabel):
    # Distribution of Age of Employees
    sns.distplot(dataframe[column_name], color = 'red')
    plt.title(title, fontsize = 30)
    plt.xlabel(xlabel, fontsize = 15)
    plt.ylabel(ylabel)
    plt.axvline(np.median(dataframe[column_name]), 0, linestyle='--', linewidth=1.5, color='b')
    # plt.savefig(f'output/visualisations/commercial/customer buying frequency distribution.png')
    #plt.show()

def popular_category(df,col):
    category_df = df.groupby(col)['order_id'].agg(['count']).reset_index().sort_values(by = 'count', ascending = False)
    labels = category_df[col].unique()
    sizes = category_df['count'].values.tolist()
    colors = [plt.cm.Spectral(i / float(len(labels))) for i in range(len(labels))]

    # Draw Plot
    plt.figure(figsize=(15, 10), dpi=120)
    squarify.plot(sizes=sizes, label=labels, color=colors, alpha=.8)

    # Decorate
    plt.title('Treemap of product category')
    plt.axis('off')
    plt.tight_layout()
    plt.savefig(f'output/visualisation/commercial/Treemap of product category.png')

def pie_chart(dataframe, col,target,color,title):
    plt.figure(figsize=(10,5), dpi = 100)
    target_df = dataframe.groupby([col])[target].agg(['count']).reset_index()

    plt.pie(target_df['count'],labels = target_df[col],
            autopct='%1.2f%%', startangle=45, colors=sns.color_palette(color),
            labeldistance=0.75, pctdistance=0.4)
    plt.title(title, fontsize = 20)
    plt.axis('off')
    plt.legend()
    plt.savefig(f'output/visualisation/commercial/customer buying frequency distribution.png')


def payment_analysis(orders_customers_payment):
    payments = orders_customers_payment.groupby(['payment_type'])['payment_value'].agg(['count', 'sum']).reset_index()

    fig, (ax1, ax2) = plt.subplots(nrows=1, ncols=2, figsize=(20, 15))
    fig.suptitle('Payment Type Count & Sum')
    ax1.pie(payments['count'], labels=payments['payment_type'], autopct='%1.2f%%', startangle=90,
            colors=sns.color_palette('Set2'), labeldistance=0.5, pctdistance=0.6)
    ax1.set_title('Payment Type Count')
    ax2.pie(payments['sum'], labels=payments['payment_type'], autopct='%1.2f%%', startangle=90,
            colors=sns.color_palette('Set1'), labeldistance=0.5, pctdistance=0.6)
    ax2.set_title('Payment Type Sum')
    plt.tight_layout()
    plt.savefig(f'output/visualisation/commercial/payment type count & sum in general.png')

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

    # merging monastery, frequency, recency
    rf_df = df_recency.merge(frequency_df, on='customer_unique_id', how='inner')
    rfm_df = rf_df.merge(monetary_df, on='customer_unique_id', how='inner').drop(columns='Last Purchase Date')
    rfm_df = rfm_df.sort_values(by = ['Frequency','Monetary'], ascending = False)

    return rfm_df

def yearly_new_client(df):
    return df

def customer_lifetime(df):
    return df

