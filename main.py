# from analysis.exploration import *
# from analysis.commercial import *
from analysis.review import *
from src.local import *


# from analysis.network import *

def commercial_analysis():
    customers, geolocation, order_items, order_payment, order_reviews, order_dataset, products, sellers, product_category = local_access_df()
    # df_frames = [customers, geolocation, order_items, order_payment, order_reviews, order_dataset, products, sellers, product_category]
    # Step 1: Data Exploration through each src set
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

    # Data Visualisation for understanding src distribution and trend more
    # Commercial Analysis
    # orders & customers datasets
    # date_state_sales = order_customer(order_dataset,customers,order_payment,order_items,products,product_category)

    # Delivery Analysis
    # delivery_analysis(order_dataset, customers, sellers, order_items,products,geolocation)

    # Review analysis
    review_analysis(order_reviews)

    # Network analysis
    # delivery_df = network_analysis(order_dataset, customers, order_payment, order_items, products, product_category,sellers)

    return None


# file_name, final_df = aws_mysql()
if __name__ == '__main__':
    try:
        analysis = commercial_analysis()
    except KeyboardInterrupt:
        print('Interrupted')
