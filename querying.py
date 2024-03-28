import mysql.connector

cnx = mysql.connector.connect(
    host='eu-cluster-west-01.k8s.cleardb.net',
    database='heroku_9f69e70d94a5650',
    user='b902878f5a41b4',
    password='4acedb6a',
    port='3306'
)
cursor = cnx.cursor()

update_flag = ("SELECT distinct fr.*, ph.bet, case when ph.bet is null or fr.goalslocal ='' "
                    "then 'NA' when upper(fr.Result)=upper(left(ph.bet,1)) "
                    "then 'Correct' else 'Incorrect' end as success, fl.flag_url, "
                    "ph.phg, ph.pag, ph.max_prob "
                    "FROM heroku_9f69e70d94a5650.football_results fr "
                    "left join heroku_9f69e70d94a5650.predictions_history ph "
                    "on fr.date = ph.date and fr.local=ph.local and fr.visitor=ph.visitor "
                    "left join heroku_9f69e70d94a5650.flags fl "
                    "on upper(fl.Country) = upper(fr.League) "
                    "AND fr.goalslocal <>'' "
                    "ORDER BY fr.date desc, fr.League "
                    "limit 10"
)
cursor.execute(update_flag)

# Fetch the results if needed
results = cursor.fetchall()
for row in results:
    print(row)

cursor.close()
cnx.close()
