import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np

from bokeh.io import output_notebook, show, save
from bokeh.models import Range1d, Circle, ColumnDataSource, MultiLine, EdgesAndLinkedNodes, NodesAndLinkedEdges
from bokeh.plotting import figure
from bokeh.plotting import from_networkx
from bokeh.palettes import Blues8,Spectral8,Plasma256,Colorblind
from bokeh.transform import linear_cmap
from networkx.algorithms import community

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

    # 1. Generate a table with seller_city and buyer city (aggregation)
    # Ideally generate network analysis
    seller_buyer_df = seller_buyer_network(orders_customers_sellers)



    # 2. Product network analysis （from order - product perspective)
    # e.g. association rule
    product_association(orders_customers_sellers)



    return orders_customers_items


def seller_buyer_network(df):
    buyer_seller_df = df.groupby(['seller_city','customer_city'])['customer_unique_id'].agg(['count']).reset_index()
    pivot_table = buyer_seller_df.pivot_table(index = ['seller_city'],
                                              columns = ['customer_city'],
                                              values = 'count',
                                              aggfunc=lambda x: ' '.join(str(v) for v in x))

    edge_df = pivot_table.fillna(0).unstack().reset_index()

    edge_df.columns = ['source','target','weight']
    edge_df['target'] = edge_df['target'].astype('string')
    edge_df['source'] = edge_df['source'].astype('string')
    edge_df['weight'] = edge_df['weight'].astype(str).astype(int)
    edge_df_weight = edge_df[edge_df['weight'] >= 1]
    sample_df = edge_df_weight[:100]

    # Create a network graph
    G = nx.from_pandas_edgelist(sample_df, edge_attr='weight')

    # Draw the network graph
    #pos = nx.spring_layout(G)
    #nx.draw(G, pos, with_labels=True, node_size=2000, node_color='skyblue', font_size=10, font_weight='bold',
    #        edge_color='gray', width=2)
    #labels = nx.get_edge_attributes(G, 'weight')
    #nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)
    #draw_network(G)
    #nx.write_gexf(G, path = f'output/visualisation/network/city relationship network.gexf')

    return buyer_seller_df

def product_association(df):
    onehotOrders = (df.groupby(['order_id', 'product_category_name_english'])['product_category_name_english'].count().unstack().
                    reset_index().fillna(0).set_index('order_id') > 0) * 1

    onehotOrders = onehotOrders.fillna(0)
    AMorders = onehotOrders.T.dot(onehotOrders) # AM stands for Adjacency matrix
    np.fill_diagonal(AMorders.values,0)

    G = nx.from_pandas_adjacency(AMorders)

    # Draw the network diagram
    #pos = nx.circular_layout(G)
    # nx.draw(G, pos, with_labels=True, node_size=2000, node_color='skyblue', font_size=10, font_weight='bold',
    #        edge_color='black')
    #plt.show()
    draw_network(G)
    return None


def draw_network(G, title = 'buyer seller relationship'):
    # References: https://melaniewalsh.github.io/Intro-Cultural-Analytics/06-Network-Analysis/02-Making-Network-Viz-with-Bokeh.html
    degrees = dict(nx.degree(G))
    nx.set_node_attributes(G, name = 'degree', values = degrees)

    number_to_adjust_by = 5
    adjusted_node_size = dict([(node, degree + number_to_adjust_by) for node, degree in nx.degree(G)])
    nx.set_node_attributes(G, name='adjusted_node_size', values=adjusted_node_size)

    communities = nx.community.greedy_modularity_communities(G)

    # Create empty dictionaries
    modularity_class = {}
    modularity_color = {}
    print(Spectral8)
    # Loop through each community in the network
    for community_number, community in enumerate(communities):
        # For each member of the community, add their community number and a distinct color
        print(community)
        for name in community:
            modularity_class[name] = community_number
            modularity_color[name] = Plasma256[community_number]

    # Add modularity class and color as attributes from the network above
    nx.set_node_attributes(G, modularity_class, 'modularity_class')
    nx.set_node_attributes(G, modularity_color, 'modularity_color')

    from bokeh.models import EdgesAndLinkedNodes, NodesAndLinkedEdges

    # Choose colors for node and edge highlighting
    node_highlight_color = 'white'
    edge_highlight_color = 'black'

    # Choose attributes from G network to size and color by — setting manual size (e.g. 10) or color (e.g. 'skyblue') also allowed
    size_by_this_attribute = 'adjusted_node_size'
    color_by_this_attribute = 'modularity_color'

    # Pick a color palette — Blues8, Reds8, Purples8, Oranges8, Viridis8
    color_palette = Blues8

    # Establish which categories will appear when hovering over each node
    HOVER_TOOLTIPS = [
        ("Character", "@index"),
        ("Degree", "@degree"),
        ("Modularity Class", "@modularity_class"),
        ("Modularity Color", "$color[swatch]:modularity_color"),
    ]

    # Create a plot — set dimensions, toolbar, and title
    plot = figure(tooltips=HOVER_TOOLTIPS,
                  tools="pan,wheel_zoom,save,reset", active_scroll='wheel_zoom',
                  x_range=Range1d(-10.1, 10.1), y_range=Range1d(-10.1, 10.1), title=title)

    # Create a network graph object
    # https://networkx.github.io/documentation/networkx-1.9/reference/generated/networkx.drawing.layout.spring_layout.html
    network_graph = from_networkx(G, nx.spring_layout, scale=10, center=(0, 0))

    # Set node sizes and colors according to node degree (color as category from attribute)
    network_graph.node_renderer.glyph = Circle(radius=size_by_this_attribute, fill_color=color_by_this_attribute)
    # Set node highlight colors
    network_graph.node_renderer.hover_glyph = Circle(radius=size_by_this_attribute, fill_color=node_highlight_color,
                                                     line_width=2)
    network_graph.node_renderer.selection_glyph = Circle(radius=size_by_this_attribute, fill_color=node_highlight_color,
                                                         line_width=2)

    # Set edge opacity and width
    network_graph.edge_renderer.glyph = MultiLine(line_alpha=0.5, line_width=1)
    # Set edge highlight colors
    network_graph.edge_renderer.selection_glyph = MultiLine(line_color=edge_highlight_color, line_width=2)
    network_graph.edge_renderer.hover_glyph = MultiLine(line_color=edge_highlight_color, line_width=2)

    # Highlight nodes and edges
    network_graph.selection_policy = NodesAndLinkedEdges()
    network_graph.inspection_policy = NodesAndLinkedEdges()

    plot.renderers.append(network_graph)

    show(plot)
    # save(plot, filename=f"{title}.html")