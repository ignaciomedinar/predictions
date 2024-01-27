import datetime

# # previous_week_start = (datetime.datetime.now().date() - datetime.timedelta(days=datetime.datetime.now().weekday())) - datetime.timedelta(days=7)
# # current_week_end = previous_week_start + datetime.timedelta(days=13)

# # print(previous_week_start)
# # print(current_week_end)

import mysql.connector
import pandas as pd
import numpy as np

# # cnx = mysql.connector.connect(
# #     host='sql7.freemysqlhosting.net',
# #     database='sql7618393',
# #     user='sql7618393',
# #     password='iYNUZFVcWQ',
# #     port='3306'
# # )
# cnx = mysql.connector.connect(
#     host='eu-cdbr-west-03.cleardb.net',
#     database='heroku_f8c05e23b7aa26a',
#     user='b1bb4e88305bd5',
#     password='b6aa7ee8',
#     port='3306'
#     )
# cursor = cnx.cursor()
cnx = mysql.connector.connect(
host='eu-cluster-west-01.k8s.cleardb.net',
database='heroku_9f69e70d94a5650',
user='b902878f5a41b4',
password='4acedb6a',
port='3306'
)
cursor = cnx.cursor()
# # empdata = pd.read_csv("C:/Users/ignac/OneDrive/Documentos/Prueba Chat GPT/Football v2/flags.csv", index_col=False, delimiter = ',', encoding='latin-1')

# create_table_query = """
# CREATE TABLE IF NOT EXISTS flags (
#     Country VARCHAR(100),
#     alpha2code VARCHAR(2),
#     alpha3code VARCHAR(3),
#     numeric_code INT(64),
#     flag_url VARCHAR(200)
# )
# """
# cursor.execute(create_table_query)
# query = ("delete from heroku_f8c05e23b7aa26a.predictions where date <= '2023-11-06' "
#             )

# # "SELECT distinct r.league, r.local, r.visitor, r.goalslocal, r.goalsvisitor, pr.phg, pr.pag, pr.max_prob "
# #                 "FROM heroku_f8c05e23b7aa26a.football_results r "
# #                 "left join heroku_f8c05e23b7aa26a.predictions pr "
# #                 "on pr.date = r.date and pr.local=r.local and pr.visitor=r.visitor "
# #                 "left join heroku_f8c05e23b7aa26a.flags fl "
# #                 "on upper(fl.Country) = upper(r.League) "
# #                 "WHERE pr.date >= '2023-11-06' "
# #                 "AND r.league = 'england' "
# #                 "ORDER BY pr.max_prob desc "


# cal_df=pd.read_sql(query,cnx)
# df=cal_df.nlargest(5, ['max_prob']) 
# print(cal_df)


# # Insert the DataFrame data into the table
# insert_query = "INSERT INTO flags (Country, alpha2code, alpha3code, numeric_code, flag_url) VALUES (%s, %s, %s, %s, %s)"
# data = empdata.values.tolist()
# cursor.executemany(insert_query, data)

# cnx.commit()
# cursor.close()
# cnx.close()

# # # Get all the weeks from the database

# # query = ("SELECT DISTINCT * "
# #             "FROM sql7618393.football_results "
# #             "ORDER BY Date ASC"
# #             )

# # cal_df=pd.read_sql(query,cnx)
# # print(cal_df)

# # import mysql.connector
# # import pandas as pd
# # import numpy as np

# # # Connect to the MySQL database
# # cnx = mysql.connector.connect(
# #     host='sql7.freemysqlhosting.net',
# #     database='sql7618393',
# #     user='sql7618393',
# #     password='iYNUZFVcWQ',
# #     port='3306'
# # )
# # cursor = cnx.cursor()

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

# Read the CSV file into a DataFrame
empdata = pd.read_csv("C:/Users/ignac/OneDrive/Documentos/Prueba Chat GPT/Football v2/flags.csv", index_col=False, delimiter=',', encoding='latin-1')
empdata = empdata.replace({np.nan: None})

# Insert the DataFrame data into the table
insert_query = "INSERT INTO flags (Country, alpha2code, alpha3code, NumericCode, flag_url) VALUES (%s, %s, %s, %s, %s)"
data = empdata.values.tolist()
cursor.executemany(insert_query, data)

# Commit the changes and close the cursor and connection
cnx.commit()
cursor.close()
cnx.close()


# # Connect to the MySQL database
# conn = mysql.connector.connect(
#     host="localhost",
#     user="root",
#     password="milanesa",
#     database="football"
# )

# cursor = conn.cursor()

# # Check if the table exists
# table_check_query = "SHOW TABLES LIKE 'football_results'"
# cursor.execute(table_check_query)

# table_exists = cursor.fetchone() is not None

# if table_exists:
#     # If the table exists, execute your query
#     sql_query = "SELECT min(date) as date FROM football_results WHERE goalslocal IS NULL or goalslocal='' ORDER BY date ASC"
#     sql_all= "SELECT * FROM football_results"
#     cursor.execute(sql_query)
#     result = cursor.fetchone()

#     if result:
#         # Extract year and month from the retrieved date
#         up_year = result[0].year
#         up_month = result[0].month
#         df_all=pd.read_sql(sql_all, conn)
#         df_all['Date'] = pd.to_datetime(df_all['Date'])
#         # Create comparison date for filtering
#         comparison_date = pd.to_datetime(f"{up_year}-{up_month:02d}-01")

#         # Filter DataFrame based on the condition
#         filtered_df = df_all[df_all['Date'] < comparison_date]

#         print(filtered_df)  # Print or do operations on the filtered DataFrame
#     else:
#         print("No data found matching the query.")