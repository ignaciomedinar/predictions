import mysql.connector

# Database credentials
# heroku
# db_config = {
#     'host': 'eu-cluster-west-01.k8s.cleardb.net',
#     'database': 'heroku_9f69e70d94a5650',
#     'user': 'b902878f5a41b4',
#     'password': '4acedb6a',
#     'port': '3306'
# }

# railway
db_config = {
    'host': 'junction.proxy.rlwy.net',
    'database': 'Predictions',
    'user': 'root',
    'password': 'xEkkvZHDuwVxfhYziMKMxYytsmKvOfSB',
    'port': '27797'
}

# Establish connection
cnx = mysql.connector.connect(**db_config)
cursor = cnx.cursor()

# Get the thread ID of the current connection
cursor.execute("SELECT CONNECTION_ID()")
current_thread_id = cursor.fetchone()[0]

# Get all process IDs
cursor.execute("SHOW PROCESSLIST")
processes = cursor.fetchall()

# Kill each process
for process in processes:
    process_id = process[0]
    if process_id != current_thread_id:  # Do not kill the current connection
        try:
            cursor.execute(f"KILL {process_id}")
            print(f"Killed process ID: {process_id}")
        except mysql.connector.Error as err:
            print(f"Error killing process ID {process_id}: {err}")

# Clean up
cursor.close()
cnx.close()
