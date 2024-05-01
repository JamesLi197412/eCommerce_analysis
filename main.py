#
import pandas as pd
from data.S3Access import *
#from data.MySQLConnection import *

def commerce_analysis():
    file_name, final_df = AWS_access()
    #connection = MySQLConnection()
    # Loop through dictionary
    for file_name, data in final_df.items():
        table_name = file_name.split('.')[0]
        df = pd.DataFrame(data)
        print(df.columns)
    return file_name, final_df

def AWS_access():
    """
    :return: csv_keys : file name at AWS S3 bucket
    """
    #config = configparser.ConfigParser()
    #config.read(config_file)

    access_key_id = "AKIAYPUDGOYO6UHV4R4U"
    secret_access_key = "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"
    region_name = "ap-northeast-1"
    bucket_name = "ecommerceolist"

    s3_reader = S3Reader(access_key_id, secret_access_key, region_name)

    csv_keys, info_dict = s3_reader.process_csv_files(bucket_name)

    return csv_keys, info_dict


if __name__ == '__main__':
    file_name, final_df = commerce_analysis()

