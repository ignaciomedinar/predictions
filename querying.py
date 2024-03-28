import mysql.connector

cnx = mysql.connector.connect(
    host='eu-cluster-west-01.k8s.cleardb.net',
    database='heroku_9f69e70d94a5650',
    user='b902878f5a41b4',
    password='4acedb6a',
    port='3306'
)
cursor = cnx.cursor()

update_flag = ("SELECT * "
               "FROM heroku_9f69e70d94a5650.predictions_history "
               "LIMIT 10 "
)
cursor.execute(update_flag)

# Fetch the results if needed
results = cursor.fetchall()
for row in results:
    print(row)

cursor.close()
cnx.close()
