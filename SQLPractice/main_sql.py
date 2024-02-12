from configparser import ConfigParser
import psycopg2
import psycopg2.extras as psql_extras
import pandas as pd
from typing import Dict


def load_connection_info(ini_filename: str) -> Dict[str, str]:
    parser = ConfigParser()
    parser.read(ini_filename)
    config = {}
    # Create a dictionary of the variables stored under the "postgresql" section of the .ini
    if parser.has_section('postgres'):
        params = parser.items('postgres')
        for param in params:
            config[param[0]] = param[1]


    # conn_info = {param[0]: param[1] for param in parser.items("postgresql")}
    return config

def connect(config):
    """Connect to the PostgreSQL database server"""
    try:
        # connecting to the PostgreSQL server
        with psycopg2.connect(**config) as conn:
            print('Connected to the PostgreSQL server.')
            return conn
    except (psycopg2.DatabaseError, Exception) as error:
        print(error)

def insert_data(
        query: str,
        conn: psycopg2.extensions.connection,
        cur: psycopg2.extensions.cursor,
        df: pd.DataFrame,
        page_size: int
) -> None:
    data_tuples = [tuple(row.to_numpy()) for index, row in df.iterrows()]

    try:
        psql_extras.execute_values(
            cur, query, data_tuples, page_size=page_size)
        print("Query:", cur.query)

    except Exception as error:
        print(f"{type(error).__name__}: {error}")
        print("Query:", cur.query)
        conn.rollback()
        cur.close()

    else:
        conn.commit()


if __name__ == "__main_sql__":
    port_num = 5432
    conn = psycopg2.connect(
        host = 'localhost',
        database = 'olist_ecommerce',
        user = 'postgres',
        password = 'Lizhiyue1997412'
    )
    config = c
    '''
    # host, database, user, password
    conn_info = load_connection_info("db.ini")
    # Connect to the "houses" database
    connection = psycopg2.connect(**conn_info)
    cursor = connection.cursor()

    # Insert data into the "house" table
    house_df = pd.DataFrame({
        "id": [1, 2, 3],
        "address": ["Street MGS, 23", "Street JHPB, 44", "Street DS, 76"]
    })
    house_query = "INSERT INTO house(id, address) VALUES %s"
    insert_data(house_query, connection, cursor, house_df, 100)

    # Insert data into the "person" table
    person_df = pd.DataFrame({
        "id": [1, 2, 3, 4],
        "name": ["Michael", "Jim", "Pam", "Dwight"],
        "house_id": [1, 2, 2, 3]
    })
    person_query = "INSERT INTO person(id, name, house_id) VALUES %s"
    insert_data(person_query, connection, cursor, person_df, 100)

    # Close all connections to the database
    connection.close()
    cursor.close()
    '''