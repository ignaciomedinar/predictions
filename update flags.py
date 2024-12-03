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
    charset='utf8',  # Ensure the connection uses UTF-8
    use_unicode=True
)

cursor = cnx.cursor()

# Read CSV with the correct encoding
empdata = pd.read_csv("C:/Users/ignac/OneDrive/Documentos/Prueba Chat GPT/Football v2/flags.csv", index_col=False, delimiter=',', encoding='latin-1')
empdata = empdata.replace({np.nan: None})

# Drop the table if it exists
drop_table_query = "DROP TABLE IF EXISTS flags"
cursor.execute(drop_table_query)

# Create the table
create_table_query = """
CREATE TABLE flags (
    Country VARCHAR(100),
    alpha2code VARCHAR(2),
    alpha3code VARCHAR(3),
    NumericCode INT(64),
    flag_url VARCHAR(200)
) CHARACTER SET utf8 COLLATE utf8_general_ci
"""
cursor.execute(create_table_query)

# Insert the DataFrame data into the table
insert_query = "INSERT INTO flags (Country, alpha2code, alpha3code, NumericCode, flag_url) VALUES (%s, %s, %s, %s, %s)"
data = empdata.values.tolist()
cursor.executemany(insert_query, data)

# Commit the transaction
cnx.commit()
cursor.close()
cnx.close()
