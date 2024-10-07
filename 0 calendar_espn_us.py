from bs4 import BeautifulSoup
import requests
import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy import create_engine
import mysql.connector

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

espn = 'https://www.espn.com/soccer/scoreboard/_/date/'

def fetch(start_date, end_date):
    df = pd.DataFrame(columns=['League', 'Week','Date', 'Local', 'Visitor', 'Goalslocal', 'Goalsvisitor', 'Result'])
    current_date = datetime.strptime(start_date, '%Y%m%d')
    end_date = datetime.strptime(end_date, '%Y%m%d')
    
    while current_date <= end_date:
        fecha = current_date.strftime('%Y%m%d')
        url = espn + fecha
        req = requests.get(url, headers=headers)
        soup = BeautifulSoup(req.content, 'html.parser')
        div_tags = soup.find_all('section', attrs={'class': 'Card gameModules'})
        
        for div in div_tags:
            league = div.find('h3', attrs={'class': 'Card__Header__Title Card__Header__Title--no-theme'}).text
            teams = div.find_all('div', attrs={'class': 'ScoreCell__TeamName ScoreCell__TeamName--shortDisplayName db'})
            goals = div.find_all('div', attrs={'class': 'ScoreCell__Score h4 clr-gray-01 fw-heavy tar ScoreCell_Score--scoreboard pl2'})
            
            home = [team.text for index, team in enumerate(teams) if index % 2 == 0]
            away = [team.text for index, team in enumerate(teams) if index % 2 != 0]
            ghome = [int(goal.text) for index, goal in enumerate(goals) if index % 2 == 0]
            gaway = [int(goal.text) for index, goal in enumerate(goals) if index % 2 != 0]
            
            min_length = min(len(home), len(away), len(ghome), len(gaway))
            home = home[:min_length]
            away = away[:min_length]
            ghome = ghome[:min_length]
            gaway = gaway[:min_length]

            if isinstance(fecha, str):
                try:
                    fecha_dt = datetime.strptime(fecha, "%Y%m%d")  # Adjust the format to match your date string format
                except ValueError as e:
                    raise ValueError(f"Incorrect date format for fecha: {fecha}. Expected format: YYYY-MM-DD") from e
            
            data = {
                'League': [league] * min_length,
                'Week': int(fecha_dt.isocalendar().week) * min_length,
                'Year': fecha_dt.year,
                'Date': [datetime.strptime(fecha, '%Y%m%d')] * min_length,
                'Local': home,
                'Visitor': away,
                'Goalslocal': ghome,
                'Goalsvisitor': gaway,
                'Result': ['t' if ghome[i] == gaway[i] else 'l' if ghome[i] > gaway[i] else 'v' for i in range(min_length)]
            }
            
            df = pd.concat([df, pd.DataFrame(data)], ignore_index=True)
        
        print("completed for: " + str(current_date))
        current_date += timedelta(days=1)
    
    return df

# Example usage: Fetch data from June 1, 2024, to July 31, 2024
start_date = '20230101'
end_date = '20241031'
result_df = fetch(start_date, end_date)

conn = mysql.connector.connect(
    host='eu-cluster-west-01.k8s.cleardb.net',
    database='heroku_9f69e70d94a5650',
    user='b902878f5a41b4',  #previous user b1bb4e88305bd5
    password='4acedb6a', #b6aa7ee8
    port='3306'
)

# Heroku clearmysql
cursor = conn.cursor()
sql = 'CREATE DATABASE IF NOT EXISTS heroku_9f69e70d94a5650;'
cursor.execute(sql)
sql='USE heroku_9f69e70d94a5650;'
cursor.execute(sql)
sql='DROP TABLE IF EXISTS heroku_9f69e70d94a5650.football_results_espn_us'
cursor.execute(sql)
conn.close()


# Define the connection URL
connection_url = 'mysql://b902878f5a41b4:4acedb6a@eu-cluster-west-01.k8s.cleardb.net/heroku_9f69e70d94a5650' #?reconnect=true


# Create the engine
engine = create_engine(connection_url) #, pool_recycle=3600

# Insert data from the DataFrame to MySQL
table_name = 'football_results_espn_us'
result_df.to_sql(table_name, con=engine, if_exists='replace', index=False)

# Close the connection to MySQL
engine.dispose()

# Print or use the resulting DataFrame as needed
print(result_df)