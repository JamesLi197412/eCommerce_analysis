import matplotlib
import pandas as pd
matplotlib.use('TkAgg')
import squarify
from analysis.pre_process import *
import psutil

import lifetimes
from lifetimes import BetaGeoFitter # BG/NBD
from lifetimes import GammaGammaFitter # Gamma-Gamma Model
from lifetimes.plotting import plot_frequency_recency_matrix


def order_customer(orders,customers,payment,items,products,product_category):
    # Prepare the dataset
    orders = order_data(orders)
    orders['order_date'] = orders['order_purchase_timestamp'].dt.date
    orders['order_month'] = orders['order_purchase_timestamp'].dt.month
    orders_customers = pd.merge(orders, customers, on = 'customer_id', how = 'left')
    orders_customers_payment = pd.merge(orders_customers, payment, on = 'order_id', how = 'inner')
    del [[orders, customers, payment,orders_customers]]

    # sales-state/city-date/month values
    geolocation_sales(orders_customers_payment, 'customer_state')
    geolocation_sales(orders_customers_payment, 'customer_city')

    # Peak time of sales
    # From the plot, it shows SP has the highest sales over the time.
    # In addition, there is a high spike on one specific point.
    # to find out its speciality, then -- Black Friday
    """
        SP_sales = top_n_sales[top_n_sales['customer_state'] == 'SP'].copy(deep = True)
        SP_point = SP_sales.sort_values(by = 'sum', ascending= False)
        print(SP_point.head())
    """

    # payment analysis (portion, price distribution, what products paid by each type)
    orders_customers_items = pd.merge(orders_customers_payment, items, on = 'order_id', how = 'left')
    orders_customers_items = pd.merge(orders_customers_items, products, on = 'product_id', how = 'inner')
    orders_customers_items = pd.merge(orders_customers_items, product_category, how = 'inner', on = 'product_category_name')
    del [[orders_customers_payment, products,product_category]]
    print('RAM memory % used:', psutil.virtual_memory()[3]/1000000000)

    # Product category and its treemap
    popular_category(orders_customers_items, 'product_category_name_english','order_id','output/visualisations/commercial/Treemap of product category.png')

    # Yearly New Clients
    yearly_new_client(orders_customers_items)

    # DAU (Daily Active User)
    DAU(orders_customers_items, 'customer_unique_id')

    # Customer Analysis
    customer_analysis(orders_customers_items)



    return orders_customers_items




def customer_split_analysis(customer_frequency,orders_customers_items):
    df = pd.merge(customer_frequency, orders_customers_items, how = 'inner', on = 'customer_unique_id')

    # Use treemap to find out where they from and count, including product category,
    popular_category(df, 'customer_state', 'customer_unique_id', 'output/visualisations/commercial/customer buy once state distribution.png')

    popular_category(df, 'product_category_name_english', 'customer_unique_id', 'output/visualisations/commercial/customer buy once product distribution.png')

    #bar_plot(df,'customer_state','customer_unique_id',f'output/visualisations/commercial/city bar.png')

def customer_analysis(orders_customers_items):
    # Customer analysis
    rfm_customer = rfm_analysis(orders_customers_items)
    # Pie chart to show portion of customer who bought products on Olist
    pie_chart(rfm_customer, 'Frequency', 'customer_unique_id', 'Set2', 'Customer Portion in General',
              path=f'output/visualisations/commercial/customer buying frequency distribution.png')

    # Split customer into two parts
    customer_regular = rfm_customer[rfm_customer['Frequency'] > 1].copy(deep=True)

    clv, clv_group = customer_lifetime(orders_customers_items)
    clv.to_csv('clv.csv')

    customer_once = rfm_customer[rfm_customer['Frequency'] == 1].copy(deep=True)
    customer_split_analysis(customer_once, orders_customers_items)

    # Regular Customers
    customer_regular = customer_regular.merge(orders_customers_items, how='inner', on='customer_unique_id')
    customer_regular['RN'] = customer_regular.sort_values(['order_date'], ascending=[True]) \
                                 .groupby(['customer_unique_id']).cumcount() + 1
    customer_regular.sort_values(by=['customer_unique_id', 'RN'], ascending=[True, True], inplace=True)



def bar_plot(df,col,target,path):
    city_df = df.groupby([col])[target].agg(['count']).reset_index().sort_values(by = 'count', ascending= False)
    sns.barplot(
        city_df, x="count", y="product_category_name",
        errorbar=("pi", 50), capsize=.4,
        err_kws={"color": ".5", "linewidth": 2.5},
        linewidth=2.5, edgecolor=".5", facecolor=(0, 0, 0, 0),
    )
    plt.savefig(path)

def product_popularity(df,path):
    product_df = df.groupby(['product_category_name'])['customer_unique_id'].agg(['count']).reset_index().sort_values(by = 'count', ascending= False)
    sns.barplot(
        product_df, x="count", y="product_category_name",
        errorbar=("pi", 50), capsize=.4,
        err_kws={"color": ".5", "linewidth": 2.5},
        linewidth=2.5, edgecolor=".5", facecolor=(0, 0, 0, 0),
    )
    plt.savefig(f'output/visualisations/commercial/product popularity.png')


def distribution_plt(dataframe,column_name,title,xlabel,ylabel):
    # Distribution of Age of Employees
    sns.distplot(dataframe[column_name], color = 'red')
    plt.title(title, fontsize = 30)
    plt.xlabel(xlabel, fontsize = 15)
    plt.ylabel(ylabel)
    plt.axvline(np.median(dataframe[column_name]), 0, linestyle='--', linewidth=1.5, color='b')
    # plt.savefig(f'output/visualisations/commercial/customer buying frequency distribution.png')
    #plt.show()

def popular_category(df,col,target,path):
    category_df = df.groupby(col)[target].agg(['count']).reset_index().sort_values(by = 'count', ascending = False)
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
    plt.savefig(path)

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
    plt.savefig(f'output/visualisations/commercial/payment type count & sum in general.png')

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
    # Group by Customers and find its min or first purchase date - > yearly new clients
    client_first = df.groupby(['customer_unique_id'])['order_purchase_timestamp'].agg(['min']).reset_index().rename(columns = {'min':'first_purchase_date'})
    client_first['order_date'] = pd.to_datetime(client_first['first_purchase_date'], errors='coerce')
    client_first['order_month'] = client_first['order_date'].dt.month
    client_first['order_year'] = client_first['order_date'].dt.year

    yearly_clients = client_first.groupby(['order_year','order_month'])['customer_unique_id'].agg(['count']).reset_index().rename(columns = {'count':'new clients'})

    yearly_clients['date'] = pd.to_datetime(yearly_clients['order_year'].astype(str) +
                                            yearly_clients['order_month'].astype(str), format='%Y%m')

    plt.figure(figsize=(12, 6))
    sns.lineplot(data=yearly_clients, x='date', y='new clients')
    plt.title(f'New Clients Over months')
    plt.xlabel('order_month')
    plt.ylabel('# of New Clients')
    plt.legend('# of New Clients over months')
    plt.savefig(f'output/visualisations/commercial/number_of_new_clients.png')

def DAU(df, client_col):
    # Group by Customers and find its min or first purchase date - > yearly new clients
    client_active = df.groupby(['order_purchase_timestamp'])[client_col].agg(['count']).reset_index().rename(
        columns={'count': 'active_user'})
    client_active['order_date'] = client_active['order_purchase_timestamp'].dt.strftime('%Y/%m/%d')

    DAU_df = client_active.groupby(['order_date'])['active_user'].agg(['sum']).reset_index().rename(
        columns={'sum': 'DAU'})

    plt.figure(figsize=(25, 15))
    sns.lineplot(data=DAU_df, x='order_date', y='DAU')
    plt.title(f'Daily Active Users')
    plt.xlabel('order_date')
    plt.ylabel('DAU')
    plt.legend('DAU')
    plt.savefig(f'output/visualisations/commercial/daily_active_users.png')


def customer_lifetime(df):
    # Customer Value = Average Order Value * Purchase Frequency
    # Increase CLV -> increase revenue & reduce customer acquisition cost
    # target your ideal customers

    # Frequency/ Recency analysis utilising BG/NBD model
    clv = lifetimes.utils.summary_data_from_transaction_data(df, 'customer_unique_id', 'order_purchase_timestamp', 'price',
                                                             observation_period_end='2017-12-09')
    # Only choose frequency >= 2
    clv = clv[clv['frequency'] > 1]

    # BetaGeoFitter - > implement BG/NBD -> predict # of purchases for each customers.
    bgf = BetaGeoFitter(penalizer_coef= 0.001)
    bgf.fit(clv['frequency'], clv['recency'], clv['T'])

    t = 180  # 30 day period
    clv['expected_purc_6_months'] = bgf.conditional_expected_number_of_purchases_up_to_time(t, clv['frequency'],
                                                                                            clv['recency'], clv['T'])

    # Gamma-Gamma Model -> predicts the most likely value for each transition
    # print(clv[['frequency','monetary_value']].corr()) # to prove there is no correlation between them.
    ggf = GammaGammaFitter(penalizer_coef=0.01)
    ggf.fit(clv["frequency"], clv["monetary_value"])

    clv['6_monhths_clv'] = ggf.customer_lifetime_value(bgf,
                                                       clv["frequency"],
                                                       clv["recency"],
                                                       clv["T"],
                                                       clv["monetary_value"],
                                                       time=6,
                                                       freq='D',
                                                       discount_rate=0.01)

    clv['Segment'] = pd.qcut(clv['6_monhths_clv'], 4,
                             labels=['Hibernating', 'Need Attention', 'LoyalCustomers', 'Champions'])

   # Group by Segment
    clv_group = clv.groupby('Segment').mean()

    # After CLV, we can offer specific products to each segment
    # Create a marketing plan to increase CLV for lower segment
    # Focus on higher segments to decrease customer acquisition costs.

    return clv, clv_group


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
    plt.savefig(f'output/visualisations/commercial/sales_{geolocation}_date.png')

    # sales-state-month sales
    month_state_sales = orders_customers_payment.groupby(['order_month',geolocation])['payment_value'].agg(['count', 'sum']).reset_index()
    top_n_sales_month = month_state_sales[month_state_sales[geolocation].isin(top_n_states)]
    plt.figure(figsize=(12, 6))
    sns.lineplot(data = top_n_sales_month,x='order_month', y='sum', hue=geolocation)
    plt.title(f'Sales by {geolocation} Over months')
    plt.xlabel('order_month')
    plt.ylabel('Sales')
    plt.legend(title= geolocation)
    plt.savefig(f'output/visualisations/commercial/sales_{geolocation}_month.png')

