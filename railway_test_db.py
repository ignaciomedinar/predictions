from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
# import mysql

# Define the connection URL
# connection_url = 'mysql://root:xEkkvZHDuwVxfhYziMKMxYytsmKvOfSB@junction.proxy.rlwy.net:27797/Predictions'

import mysql.connector
import pandas as pd
import numpy as np

# Establish connection to MySQL with the correct character set
# cnx = mysql.connector.connect(
#     host='eu-cluster-west-01.k8s.cleardb.net',
#     database='heroku_9f69e70d94a5650',
#     user='b902878f5a41b4',
#     password='4acedb6a',
#     port='3306',
#     charset='utf8',  # Ensure the connection uses UTF-8
#     use_unicode=True
# )

cnx = mysql.connector.connect(
    host='junction.proxy.rlwy.net',
    database='Predictions',
    user='root',
    password='xEkkvZHDuwVxfhYziMKMxYytsmKvOfSB',
    port='27797',
    # charset='utf8',  # Ensure the connection uses UTF-8
    # use_unicode=True,
    # allow_public_key_retrieval=True,
    auth_plugin='mysql_native_password'
)

cursor = cnx.cursor()

# Read CSV with the correct encoding
empdata = pd.read_csv("C:/Users/ignac/Downloads/football_results_espn_us_202411301252.csv", index_col=False, delimiter=',', encoding='latin-1') 
empdata = empdata.replace({np.nan: None})

# Drop the table if it exists
drop_table_query = "DROP TABLE IF EXISTS results"
cursor.execute(drop_table_query)

# Create the table
create_table_query = """
CREATE TABLE results (
    league	varchar(100),
    Week	int,
    Date	varchar(50),
    Local	varchar(50),
    Visitor	varchar(50),
    Goalslocal	int,
    Goalsvisitor	int,
    Result	varchar(50),
    Year	double
) CHARACTER SET utf8 COLLATE utf8_general_ci
"""
cursor.execute(create_table_query)

# Insert the DataFrame data into the table
insert_query = "INSERT INTO results (league, Week, Date, Local, Visitor, Goalslocal, Goalsvisitor, Result, Year) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
data = empdata.values.tolist()
cursor.executemany(insert_query, data)

# Commit the transaction
cnx.commit()
cursor.close()
cnx.close()
