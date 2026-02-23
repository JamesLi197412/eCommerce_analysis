import pandas as pd

from src.MySQLConnection import MySQLConnection
from src.S3Access import S3Reader


def infer_mysql_type(series):
    if pd.api.types.is_integer_dtype(series):
        return 'BIGINT'
    if pd.api.types.is_float_dtype(series):
        return 'DOUBLE'
    if pd.api.types.is_bool_dtype(series):
        return 'BOOLEAN'
    if pd.api.types.is_datetime64_any_dtype(series):
        return 'DATETIME'
    return 'VARCHAR(255)'


def build_mysql_schema(dataframe):
    column_defs = []
    for column_name in dataframe.columns:
        mysql_type = infer_mysql_type(dataframe[column_name])
        column_defs.append(f'`{column_name}` {mysql_type}')
    return ', '.join(column_defs)


def mysql():
    file_name, final_df = AWS_access()
    connection = MySQLConnection('*******', '******', '*******', '******')

    # Loop through dictionary
    for file_name, data in final_df.items():
        table_name = file_name.split('.')[0].replace('-', '_')
        df = pd.DataFrame(data)
        if df.empty:
            continue

        schema = build_mysql_schema(df)
        connection.create_table(table_name, schema)
        connection.insert_dataframe(table_name, df)

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
