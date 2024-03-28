import mysql.connector
import pandas as pd
import numpy as np

cnx = mysql.connector.connect(
host='eu-cluster-west-01.k8s.cleardb.net',
database='heroku_9f69e70d94a5650',
user='b902878f5a41b4',
password='4acedb6a',
port='3306'
)
cursor = cnx.cursor()

empdata = pd.read_csv("C:/Users/ignac/OneDrive/Documentos/Prueba Chat GPT/Football v2/flags.csv", index_col=False, delimiter = ',', encoding='latin-1')
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
)
"""
cursor.execute(create_table_query)

# Insert the DataFrame data into the table
insert_query = "INSERT INTO flags (Country, alpha2code, alpha3code, NumericCode, flag_url) VALUES (%s, %s, %s, %s, %s)"
data = empdata.values.tolist()
cursor.executemany(insert_query, data)


cnx.commit()
cursor.close()
cnx.close()

    # "update heroku_f8c05e23b7aa26a.flags "
    # "set flag_url= 'https://en.wikipedia.org/wiki/Flag_of_Turkey#/media/File:Flag_of_Turkey.svg' "
    # "where Country='Turkey'"

# update_flag = (
#     "GRANT UPDATE ON heroku_f8c05e23b7aa26a.flags TO 'b902878f5a41b4'@'eu-cluster-west-01.k8s.cleardb.net' "

# )
# cursor.execute(update_flag)