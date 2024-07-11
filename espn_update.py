from bs4 import BeautifulSoup
import requests
import pandas as pd
from datetime import datetime, timedelta, date
from sqlalchemy import create_engine, text

# Define the connection URL
connection_url = 'mysql://b902878f5a41b4:4acedb6a@eu-cluster-west-01.k8s.cleardb.net/heroku_9f69e70d94a5650'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

def fetch(start_date, end_date):
    df = pd.DataFrame(columns=['League', 'Week', 'Year', 'Date', 'Local', 'Visitor', 'Goalslocal', 'Goalsvisitor', 'Result'])
    current_date = start_date
    today = datetime.today()
    
    # Ensure current_date is a datetime object
    if isinstance(current_date, date) and not isinstance(current_date, datetime):
        current_date = datetime.combine(current_date, datetime.min.time())

    while current_date <= end_date:
        fecha = current_date.strftime('%Y%m%d')
        url = f'https://espndeportes.espn.com/futbol/resultados/_/fecha/{fecha}'
        req = requests.get(url, headers=headers)
        soup = BeautifulSoup(req.content, 'html.parser')
        div_tags = soup.find_all('section', attrs={'class': 'Card gameModules'})
        
        for div in div_tags:
            league_tag = div.find('h3', attrs={'class': 'Card__Header__Title Card__Header__Title--no-theme'}) 
            if not league_tag:
                league_tag = div.find('h3', attrs={'class': 'Card_HeaderTitle CardHeader_Title--no-theme'})
                if not league_tag:
                    continue  # Skip this div if no league title is found
            league = league_tag.text

            teams = div.find_all('div', attrs={'class': 'ScoreCell__TeamName ScoreCell__TeamName--shortDisplayName truncate db'}) #ScoreCell_TeamName ScoreCell_TeamName--shortDisplayName truncate db
            if not teams:
                teams = div.find_all('div', attrs={'class': 'ScoreCell_TeamName ScoreCell_TeamName--shortDisplayName truncate db'})
            goals = div.find_all('div', attrs={'class': 'ScoreCell__Score h4 clr-gray-01 fw-heavy tar ScoreCell_Score--scoreboard pl2'})
            
            home = [team.text for index, team in enumerate(teams) if index % 2 == 0]
            away = [team.text for index, team in enumerate(teams) if index % 2 != 0]
            ghome = [goal.text if goal.text.isdigit() else None for index, goal in enumerate(goals) if index % 2 == 0]
            gaway = [goal.text if goal.text.isdigit() else None for index, goal in enumerate(goals) if index % 2 != 0]
            
            min_length = min(len(home), len(away))
            home = home[:min_length]
            away = away[:min_length]

            # Ensure ghome and gaway have the same length as min_length
            if len(ghome) < min_length:
                ghome.extend([None] * (min_length - len(ghome)))
            else:
                ghome = ghome[:min_length]

            if len(gaway) < min_length:
                gaway.extend([None] * (min_length - len(gaway)))
            else:
                gaway = gaway[:min_length]
            
            if isinstance(fecha, str):
                try:
                    fecha_dt = datetime.strptime(fecha, "%Y%m%d")  # Adjust the format to match your date string format
                except ValueError as e:
                    raise ValueError(f"Incorrect date format for fecha: {fecha}. Expected format: YYYY-MM-DD") from e

            data = {
                'League': [league] * min_length,
                'Week': int(fecha_dt.date().isocalendar().week),
                'Year': fecha_dt.year,
                'Date': [datetime.strptime(fecha, '%Y%m%d')] * min_length,
                'Local': home,
                'Visitor': away,
                'Goalslocal': [int(ghome[i]) if ghome[i] is not None and current_date <= today else None for i in range(min_length)],
                'Goalsvisitor': [int(gaway[i]) if gaway[i] is not None and current_date <= today else None for i in range(min_length)],
                'Result': [
                    't' if ghome[i] is not None and gaway[i] is not None and ghome[i] == gaway[i] else
                    'l' if ghome[i] is not None and gaway[i] is not None and int(ghome[i]) > int(gaway[i]) else
                    'v' if ghome[i] is not None and gaway[i] is not None and int(ghome[i]) < int(gaway[i]) else
                    None for i in range(min_length)
                ]
            }
            
            df = pd.concat([df, pd.DataFrame(data)], ignore_index=True)
        
        print("Completed: ", current_date)
        current_date += timedelta(days=1)
    
    return df

# Function to get max date from MySQL table
def get_max_date_from_mysql(engine):
    with engine.connect() as connection:
        query = text("SELECT MAX(Date) FROM football_results WHERE Result IS NOT NULL")
        result = connection.execute(query).fetchone()
        return result[0] if result else None

# Function to delete records after max date
def delete_records_after_max_date(engine, max_date):
    with engine.connect() as connection:
        delete_query = text("DELETE FROM football_results WHERE Date >= :max_date")
        max_date_text = max_date.strftime('%Y-%m-%d')  # Format datetime to string
        connection.execute(delete_query, {'max_date': max_date_text})
        connection.commit()

# Main function to update MySQL table
def update_mysql_table(connection_url):
    # Create the engine
    engine = create_engine(connection_url)
    
    # Get max date from existing data in MySQL
    max_date = get_max_date_from_mysql(engine)
    
    # Calculate start and end dates
    if max_date:
        start_date = max_date
        delete_records_after_max_date(engine, max_date)
    else:
        start_date = datetime.strptime('20230101', '%Y%m%d')  # Initial start date if table is empty
    
    end_date = datetime.now() + timedelta(days=30)
    
    # Fetch new data from ESPN
    result_df = fetch(start_date, end_date)
    
    # Insert data to MySQL
    table_name = 'football_results'
    result_df.to_sql(table_name, con=engine, if_exists='append', index=False)
    
    # Close the connection to MySQL
    engine.dispose()

# Call the update function
update_mysql_table(connection_url)