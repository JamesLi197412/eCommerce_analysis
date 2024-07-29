# from analysis.exploration import *
from analysis.commercial import *
from analysis.delivery import *
from analysis.review import *
from analysis.network import *
from src.local import *

def analysis():
    # Step 1: Data Gathering
    customers, geolocation, order_items, order_payment, order_reviews, order_dataset, products, sellers, product_category = local_access_df()
    # df_frames = [customers, geolocation, order_items, order_payment, order_reviews, order_dataset, products, sellers, product_category]

    # Step 2: Data Exploration through each src set
    # cust_exploration = Exploration(customers)
    # cust_exploration.df_info_()
    #
    # ord_exploration = Exploration(order_dataset)
    # ord_exploration.df_info_()
    #
    # payment_exploration = Exploration(order_payment)
    # payment_exploration.df_info_()
    #
    # review_exploration = Exploration(order_reviews)
    # review_exploration.df_info_()

    # Commercial Analysis
    # orders & customers datasets
    orders_customers_items = order_customer(order_dataset,customers,order_payment,order_items,products,product_category)

    # Delivery Analysis
    # delivery_analysis(orders_customers_items,sellers,geolocation)

    # Review analysis
    # review_analysis(order_reviews)

    # Network analysis
    # delivery_df = network_analysis(orders_customers_items,sellers)




# file_name, final_df = aws_mysql()
if __name__ == '__main__':
    try:
        analysis()
    except KeyboardInterrupt:
        print('Interrupted')
