
import pymysql.cursors

class MySQLConnection:
    def __init__(self,host,user,password,database):
        self.host = host
        self.user = user
        self.password = password
        self.database = database

    def connection(self):
        self.connection = pymysql.connect(
            host = self.host,
            user = self.user,
            password = self.password,
            database = self.database
        )

    def create_table(self, table_name, columns):
        cursor = self.connection.cursor()
        query = f"CREATE TABLE {table_name} ({columns})"
        cursor.execute(query)
        self.connection.commit()

    def close(self):
        if self.connection:
            self.connection.close()
            self.connection = None

    def insert_data(self, table_name, values):
        cursor = self.connection.cursor()
        query = f"INSERT INTO {table_name} VALUES ({values})"
        cursor.execute(query)
        self.connection.commit()