import pymysql.cursors
import pandas as pd


class MySQLConnection:
    def __init__(self, host, user, password, database):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None

    def connection_generate(self):
        if self.connection is not None:
            return self.connection

        self.connection = pymysql.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database
        )
        return self.connection

    def create_table(self, table_name, columns):
        connection = self.connection_generate()
        with connection.cursor() as cursor:
            query = f"CREATE TABLE IF NOT EXISTS `{table_name}` ({columns})"
            cursor.execute(query)
        connection.commit()

    def close(self):
        if self.connection:
            self.connection.close()
            self.connection = None

    def insert_data(self, table_name, values):
        if isinstance(values, pd.DataFrame):
            self.insert_dataframe(table_name, values)
            return

        connection = self.connection_generate()
        with connection.cursor() as cursor:
            query = f"INSERT INTO `{table_name}` VALUES ({values})"
            cursor.execute(query)
        connection.commit()

    def insert_dataframe(self, table_name, dataframe):
        if dataframe.empty:
            return

        connection = self.connection_generate()
        columns = [f'`{column}`' for column in dataframe.columns]
        placeholders = ', '.join(['%s'] * len(columns))
        query = f"INSERT INTO `{table_name}` ({', '.join(columns)}) VALUES ({placeholders})"
        rows = [
            tuple(None if pd.isna(value) else value for value in row)
            for row in dataframe.itertuples(index=False, name=None)
        ]

        with connection.cursor() as cursor:
            cursor.executemany(query, rows)
        connection.commit()
