import datetime

# previous_week_start = (datetime.datetime.now().date() - datetime.timedelta(days=datetime.datetime.now().weekday())) - datetime.timedelta(days=7)
# current_week_end = previous_week_start + datetime.timedelta(days=13)

# print(previous_week_start)
# print(current_week_end)

import mysql.connector
import pandas as pd

cnx = mysql.connector.connect(
    host='sql7.freemysqlhosting.net',
    database='sql7618393',
    user='sql7618393',
    password='iYNUZFVcWQ',
    port='3306'
)

cursor = cnx.cursor()

# empdata = pd.read_csv("C:/Users/ignac/OneDrive/Documentos/Prueba Chat GPT/Football v2/flags.csv", index_col=False, delimiter = ',', encoding='latin-1')

# create_table_query = """
# CREATE TABLE IF NOT EXISTS flags (
#     Country VARCHAR(100),
#     alpha2code VARCHAR(2),
#     alpha3code VARCHAR(3),
#     numeric_code INT(64),
#     flag_url VARCHAR(200)
# )
# """

query = ("SELECT DISTINCT * "
            "FROM sql7618393.flags "
            )

cal_df=pd.read_sql(query,cnx)
print(cal_df)


# # Insert the DataFrame data into the table
# insert_query = "INSERT INTO flags (Country, alpha2code, alpha3code, numeric_code, flag_url) VALUES (%s, %s, %s, %s, %s)"
# data = empdata.values.tolist()
# cursor.executemany(insert_query, data)

# cnx.commit()
cursor.close()
cnx.close()

# # Get all the weeks from the database

# query = ("SELECT DISTINCT * "
#             "FROM sql7618393.football_results "
#             "ORDER BY Date ASC"
#             )

# cal_df=pd.read_sql(query,cnx)
# print(cal_df)

# import mysql.connector
# import pandas as pd
# import numpy as np

# # Connect to the MySQL database
# cnx = mysql.connector.connect(
#     host='sql7.freemysqlhosting.net',
#     database='sql7618393',
#     user='sql7618393',
#     password='iYNUZFVcWQ',
#     port='3306'
# )
# cursor = cnx.cursor()

# # Drop the table if it exists
# drop_table_query = "DROP TABLE IF EXISTS flags"
# cursor.execute(drop_table_query)

# # Create the table
# create_table_query = """
# CREATE TABLE flags (
#     Country VARCHAR(100),
#     alpha2code VARCHAR(2),
#     alpha3code VARCHAR(3),
#     NumericCode INT(64),
#     flag_url VARCHAR(200)
# )
# """
# cursor.execute(create_table_query)

# # Read the CSV file into a DataFrame
# empdata = pd.read_csv("C:/Users/ignac/OneDrive/Documentos/Prueba Chat GPT/Football v2/flags.csv", index_col=False, delimiter=',', encoding='latin-1')
# empdata = empdata.replace({np.nan: None})

# # Insert the DataFrame data into the table
# insert_query = "INSERT INTO flags (Country, alpha2code, alpha3code, NumericCode, flag_url) VALUES (%s, %s, %s, %s, %s)"
# data = empdata.values.tolist()
# cursor.executemany(insert_query, data)

# # Commit the changes and close the cursor and connection
# cnx.commit()
# cursor.close()
# cnx.close()
