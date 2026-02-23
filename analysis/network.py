from itertools import combinations

import networkx as nx

try:
    from bokeh.io import show
    from bokeh.models import Circle, MultiLine, Range1d
    from bokeh.plotting import figure, from_networkx
except ModuleNotFoundError:
    show = None
    Circle = None
    MultiLine = None
    Range1d = None
    figure = None
    from_networkx = None

try:
    from mlxtend.frequent_patterns import apriori, association_rules
except ModuleNotFoundError:
    apriori = None
    association_rules = None

from analysis.pre_process import *


def network_analysis(orders_customers_items, sellers):
    orders_customers_sellers = orders_customers_items.merge(sellers, how='inner', on='seller_id')

    # 1. Generate a table with seller_city and buyer city (aggregation)
    # Ideally generate network analysis
    seller_buyer_df = seller_buyer_network(orders_customers_sellers)

    # 2. Product network analysis （from order - product perspective)
    # e.g. association rule
    product_association(orders_customers_sellers)

    return orders_customers_items


def seller_buyer_network(df):
    buyer_seller_df = df.groupby(['seller_city', 'customer_city'])['customer_unique_id'].agg(['count']).reset_index()
    pivot_table = buyer_seller_df.pivot_table(index=['seller_city'],
                                              columns=['customer_city'],
                                              values='count',
                                              aggfunc=lambda x: ' '.join(str(v) for v in x))

    edge_df = pivot_table.fillna(0).unstack().reset_index()

    edge_df.columns = ['source', 'target', 'weight']
    edge_df['target'] = edge_df['target'].astype('string')
    edge_df['source'] = edge_df['source'].astype('string')
    edge_df['weight'] = edge_df['weight'].astype(str).astype(int)
    edge_df_weight = edge_df[edge_df['weight'] >= 1]
    sample_df = edge_df_weight[:100]

    # Create a network graph
    G = nx.from_pandas_edgelist(sample_df, edge_attr='weight')

    # Draw the network graph & export diagram to output file
    draw_simple_network(G, f'output/visualisations/network/city relationship network.gexf')

    return buyer_seller_df


def product_association(df):
    order_product = df.groupby(['order_id', 'product_category_name_english'])['product_category_name_english'].count(). \
        unstack().reset_index().fillna(0).set_index('order_id')
    if order_product.empty or order_product.shape[1] == 0:
        print('No product-category pairs available for association analysis; skipping.')
        return None

    order_product_df = order_product.gt(0)

    rules, items = get_rules(order_product_df, min_support=0.001)
    rules.to_csv('output/visualisations/network/Product Buying Rules.csv')
    print('Number of Associations: {}'.format(rules.shape[0]))

    if not rules.empty:
        rules.plot.scatter('support', 'confidence', alpha=0.5, marker='*')
        plt.xlabel('Support')
        plt.ylabel('Confidence')
        plt.title('Association Rule')
        plt.savefig(f'output/visualisations/network/Association Rules.png')

    AMorders = order_product.T.dot(order_product)  # AM stands for Adjacency matrix
    np.fill_diagonal(AMorders.values, 0)
    print(AMorders.head())

    G = nx.from_pandas_adjacency(AMorders)
    # Draw the network diagram
    draw_network(G, 'Product Category Network')
    # draw_simple_network(G)

    return None


def get_rules(df, min_support=0.01):
    if apriori is None or association_rules is None:
        print('mlxtend package is not available; using pairwise association fallback.')
        return fallback_pair_rules(df, min_support=min_support, min_confidence=0.6), pd.DataFrame()

    # Apply the Apriori algorithm to find frequent itemsets
    frequent_itemsets = apriori(df, min_support=min_support, use_colnames=True)
    frequent_itemsets['length'] = frequent_itemsets['itemsets'].apply(lambda x: len(x))

    # Generate association rules
    if frequent_itemsets.empty:
        return pd.DataFrame(), frequent_itemsets

    rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=0.6)

    return rules, frequent_itemsets


def fallback_pair_rules(df, min_support=0.01, min_confidence=0.6):
    supports = df.mean(axis=0)
    records = []

    for antecedent, consequent in combinations(df.columns, 2):
        pair_support = (df[antecedent] & df[consequent]).mean()
        if pair_support < min_support:
            continue

        antecedent_support = supports[antecedent]
        consequent_support = supports[consequent]

        conf_ab = pair_support / antecedent_support if antecedent_support else 0
        conf_ba = pair_support / consequent_support if consequent_support else 0

        if conf_ab >= min_confidence and consequent_support:
            records.append(
                {
                    'antecedents': frozenset([antecedent]),
                    'consequents': frozenset([consequent]),
                    'antecedent support': antecedent_support,
                    'consequent support': consequent_support,
                    'support': pair_support,
                    'confidence': conf_ab,
                    'lift': conf_ab / consequent_support
                }
            )
        if conf_ba >= min_confidence and antecedent_support:
            records.append(
                {
                    'antecedents': frozenset([consequent]),
                    'consequents': frozenset([antecedent]),
                    'antecedent support': consequent_support,
                    'consequent support': antecedent_support,
                    'support': pair_support,
                    'confidence': conf_ba,
                    'lift': conf_ba / antecedent_support
                }
            )

    if not records:
        return pd.DataFrame()

    return pd.DataFrame(records).sort_values(by=['support', 'confidence'], ascending=False)


def draw_simple_network(G, path):
    # Draw the network diagram
    plt.figure(figsize=(16, 12))
    pos = nx.spring_layout(G)
    nx.draw(G, pos, with_labels=True, node_size=2000, node_color='skyblue', font_size=10, font_weight='bold',
            edge_color='black')
    labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)
    png_path = path.replace('.gexf', '.png')
    plt.savefig(png_path)
    plt.close()
    nx.write_gexf(G, path=path)


def draw_network(G, title='buyer seller relationship'):
    if show is None or figure is None or from_networkx is None:
        print('bokeh package is not available; skipping interactive network chart.')
        return

    # References: https://melaniewalsh.github.io/Intro-Cultural-Analytics/06-Network-Analysis/02-Making-Network-Viz-with-Bokeh.html
    degrees = dict(nx.degree(G, weight='weight'))

    number_to_adjust_by = 5
    adjusted_node_size = dict([(node, degree + number_to_adjust_by) for node, degree in nx.degree(G)])
    nx.set_node_attributes(G, name='adjusted_node_size', values=adjusted_node_size)

    # Choose attributes from G network to size and color by — setting manual size (e.g. 10) or color (e.g. 'skyblue') also allowed
    size_by_this_attribute = 'adjusted_node_size'

    # Establish which categories will appear when hovering over each node
    HOVER_TOOLTIPS = [
        ("Product", "@index"),
        ("Adjusted Degree", "@adjusted_node_size")
    ]

    # Create a plot — set dimensions, toolbar, and title
    plot = figure(tooltips=HOVER_TOOLTIPS,
                  tools="pan,wheel_zoom,save,reset, tap", active_scroll='wheel_zoom',
                  x_range=Range1d(-10.1, 10.1), y_range=Range1d(-10.1, 10.1), title=title)

    # Create a network graph object
    network_graph = from_networkx(G, nx.spring_layout, scale=10, center=(0, 0))

    # Set node sizes and colors according to node degree (color as category from attribute)
    try:
        network_graph.node_renderer.glyph = Circle(radius=0.15, fill_color='skyblue')
    except Exception as error:
        print(f'Unable to render interactive node glyphs: {error}')
        return

    # Set edge opacity and width
    network_graph.edge_renderer.glyph = MultiLine(line_alpha=0.5, line_width='weight')

    plot.renderers.append(network_graph)

    show(plot)
    # save(plot, filename=f"{title}.html")
