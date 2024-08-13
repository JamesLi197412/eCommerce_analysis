import pandas as pd

from MySQLConnection import *
from S3Access import *


def mysql():
    file_name, final_df = AWS_access()
    connection = MySQLConnection('*******', '******', '*******', '******')

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
    :return: csv_keys : file name at AWS S3 bucket and src stored in dictionary formart
    """
    # config = configparser.ConfigParser()
    # config.read(config_file)

    access_key_id = "*************"
    secret_access_key = "*************"
    region_name = "*************"
    bucket_name = "*************"

    s3_reader = S3Reader(access_key_id, secret_access_key, region_name)

    csv_keys, info_dict = s3_reader.process_csv_files(bucket_name)

    return csv_keys, info_dict
