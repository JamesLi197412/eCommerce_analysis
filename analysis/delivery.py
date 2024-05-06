# To-do list:
# 1. Cities matches
# 2. Network analysis
# 3. Delivery Gap (Estimated vs Actual
# 4. why canceled
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt


def order_data(df):
    """to adjust order date column in orders dataset"""
    df['order_delivered_customer_date'] = pd.to_datetime(df['order_delivered_customer_date'],errors='coerce')
    df['order_delivered_carrier_date'] = pd.to_datetime(df['order_delivered_carrier_date'],errors='coerce')
    df['order_approved_at'] = pd.to_datetime(df['order_approved_at'],errors='coerce')
    df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'],errors='coerce')
    df['order_estimated_delivery_date'] = pd.to_datetime(df['order_estimated_delivery_date'],errors='coerce')
    return df

def delivery_analysis(orders,customers,payment,items,products,product_category, sellers):
    # One customer could have multiple orders
    orders = order_data(orders)
    orders['order_date'] = orders['order_purchase_timestamp'].dt.date
    orders['order_month'] = orders['order_purchase_timestamp'].dt.month
    orders_customers = orders.merge(customers, on = 'customer_id', how = 'left')
    orders_customers_payment = orders_customers.merge(payment, on = 'order_id', how = 'inner')
    orders_customers_items = orders_customers_payment.merge(items, on='order_id', how='left')
    orders_customers_items = orders_customers_items.merge(products, on = 'product_id', how = 'inner')
    orders_customers_items = orders_customers_items.merge(product_category, how = 'inner', on = 'product_category_name')
    orders_customers_sellers = orders_customers_items.merge(sellers, how = 'inner', on = 'seller_id')
    # print(orders_customers_sellers.columns)
    # 1. Generate a table with seller_city and buyer city (aggregation)
    # Ideally generate network analysis
    seller_buyer_df = seller_buyer_network(orders_customers_sellers)

    # 2. Product network analysis （from order - product perspective)
    # e.g. association rule


    return orders_customers_items


def seller_buyer_network(df):
    g = nx.Graph()
    buyer_seller_df = df.groupby(['seller_city','customer_city'])['customer_unique_id'].agg(['count']).reset_index()
    pivot_table = buyer_seller_df.pivot_table(index = ['seller_city'],
                                              columns = ['customer_city'],
                                              values = 'count',
                                              aggfunc=lambda x: ' '.join(str(v) for v in x))
    pivot_table = pivot_table.fillna(0)
    edge_df = pivot_table.unstack().reset_index()

    edge_df.columns = ['source','target','weight']
    edge_df['target'] = edge_df['target'].astype('string')
    edge_df['source'] = edge_df['source'].astype('string')
    edge_df['weight'] = edge_df['weight'].astype(str).astype(int)
    #edge_df.to_csv('test3.csv')
    edge_df_weight = edge_df[edge_df['weight'] >= 1]
    sample_df = edge_df_weight[:100]

    # Create a network graph
    G = nx.from_pandas_edgelist(sample_df, edge_attr='weight')

    # Draw the network graph
    pos = nx.spring_layout(G)
    nx.draw(G, pos, with_labels=True, node_size=2000, node_color='skyblue', font_size=10, font_weight='bold',
            edge_color='gray', width=2)
    labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)

    plt.show()
    nx.write_gexf(G, path = f'output/visualisation/delivery/city relationship network.gexf')

    return buyer_seller_df

