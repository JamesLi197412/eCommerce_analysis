#
from data.S3Access import *
from data.MySQLConnection import *
from data.local import *
from analysis.exploration import *
from analysis.commerical_analysis import *


def mysql():
    file_name, final_df = AWS_access()
    connection = MySQLConnection('localhost', 'root', 'Lizhiyue1997412', 'test')

    # Loop through dictionary
    for file_name, data in final_df.items():
        table_name = file_name.split('.')[0]
        df = pd.DataFrame(data)
        columns = df.columns
        connection.create_table(table_name, columns)
        connection.insert_data(table_name, df)

    connection.close()
    return file_name, final_df

def AWS_access():
    """
    :return: csv_keys : file name at AWS S3 bucket and data stored in dictionary formart
    """
    # config = configparser.ConfigParser()
    # config.read(config_file)

    access_key_id = "AKIAYPUDGOYO6UHV4R4U"
    secret_access_key = "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"
    region_name = "ap-northeast-1"
    bucket_name = "ecommerceolist"

    s3_reader = S3Reader(access_key_id, secret_access_key, region_name)

    csv_keys, info_dict = s3_reader.process_csv_files(bucket_name)

    return csv_keys, info_dict


def commercial_analysis():
    customers, geolocation, order_items, order_payment, order_reviews, order_dataset, products, sellers, product_category = local_access_df()
    # Data Exploration through each data set
    cust_exploration = Exploration(customers)
    cust_exploration.df_info_()

    ord_exploration = Exploration(order_dataset)
    ord_exploration.df_info_()

    payment_exploration = Exploration(order_payment)
    payment_exploration.df_info_()

    # Data Visualisation for understanding data distribution and trend more
    # orders & customers dataset
    date_state_sales = order_customer(order_dataset,customers,order_payment)



    # sales analysis by merging multiple tables


    # sales analysis
    return date_state_sales


# file_name, final_df = aws_mysql()
if __name__ == '__main__':
    commercial_analysis()


