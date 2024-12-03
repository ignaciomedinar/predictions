import pandas as pd
import requests
from sqlalchemy import create_engine, text

# Your API key and parameters
API_KEY = '64906938024e274a6e4662aa87a3787b'
# SPORT = 'soccer_mexico_ligamx'
REGIONS = 'us'
MARKETS = 'h2h'
ODDS_FORMAT = 'decimal'
DATE_FORMAT = 'iso'

leagues =['soccer_argentina_primera_division','soccer_australia_aleague',
          'soccer_austria_bundesliga','soccer_belgium_first_div',
          'soccer_brazil_campeonato','soccer_brazil_serie_b',
          'soccer_chile_campeonato','soccer_china_superleague',
          'soccer_conmebol_copa_libertadores','soccer_denmark_superliga',
          'soccer_efl_champ','soccer_england_efl_cup',
          'soccer_england_league1','soccer_england_league2','soccer_epl',
          'soccer_fifa_world_cup_winner','soccer_finland_veikkausliiga',
          'soccer_france_ligue_one','soccer_france_ligue_two',
          'soccer_germany_bundesliga','soccer_germany_bundesliga2',
          'soccer_germany_liga3','soccer_greece_super_league',
          'soccer_italy_serie_a','soccer_italy_serie_b',
          'soccer_japan_j_league','soccer_korea_kleague1',
          'soccer_league_of_ireland','soccer_mexico_ligamx',
          'soccer_netherlands_eredivisie','soccer_norway_eliteserien',
          'soccer_poland_ekstraklasa','soccer_portugal_primeira_liga',
          'soccer_spain_la_liga','soccer_spain_segunda_division',
          'soccer_spl','soccer_sweden_allsvenskan',
          'soccer_sweden_superettan','soccer_switzerland_superleague',
          'soccer_turkey_super_league','soccer_uefa_champs_league',
          'soccer_uefa_europa_conference_league',
          'soccer_uefa_europa_league','soccer_usa_mls']

# Define the database connection URL
# connection_url = 'mysql://b902878f5a41b4:4acedb6a@eu-cluster-west-01.k8s.cleardb.net/heroku_9f69e70d94a5650' #?reconnect=true
connection_url = 'mysql://root:xEkkvZHDuwVxfhYziMKMxYytsmKvOfSB@junction.proxy.rlwy.net:27797/Predictions'

engine = create_engine(connection_url)  

# Drop the table if it exists at the beginning
with engine.connect() as connection:
    query = text("DROP TABLE IF EXISTS weekly_odds")
    connection.execute(query)

for SPORT in leagues:
    # Request the odds data from the API
    odds_response = requests.get(
        f'https://api.the-odds-api.com/v4/sports/{SPORT}/odds',
        params={
            'api_key': API_KEY,
            'regions': REGIONS,
            'markets': MARKETS,
            'oddsFormat': ODDS_FORMAT,
            'dateFormat': DATE_FORMAT,
        }
    )

    if odds_response.status_code != 200:
        print(f'Failed to get odds: status_code {odds_response.status_code}, response body {odds_response.text}')
    else:
        odds_json = odds_response.json()
        
        # Extract relevant data
        data = []
        for event in odds_json:
            # Extract basic event information
            league=event['sport_title']
            away_team = event['away_team']
            date = event['commence_time'][:10]  # Extract only the date part (YYYY-MM-DD)
            home_team = event['home_team']

            # Loop through all bookmakers
            for bookmaker in event['bookmakers']:
                # Use 'title' if available, otherwise use 'key'
                bookmaker_name = bookmaker.get('title', bookmaker['key'])
                markets = bookmaker['markets']
                
                # Extract prices from the 'h2h' market
                h2h_market = next((market for market in markets if market['key'] == 'h2h'), None)
                if h2h_market and 'outcomes' in h2h_market:
                    outcomes = h2h_market['outcomes']
                    home_odds = next((outcome['price'] for outcome in outcomes if outcome['name'] == home_team), None)
                    draw_odds = next((outcome['price'] for outcome in outcomes if outcome['name'] == 'Draw'), None)
                    away_odds = next((outcome['price'] for outcome in outcomes if outcome['name'] == away_team), None)

                    # Append the row data
                    data.append({
                        'League': league,
                        'Home': home_team,
                        'Away': away_team,
                        'Date': date,
                        'Bookmaker': bookmaker_name,
                        'HomeOdds': home_odds,
                        'DrawOdds': draw_odds,
                        'AwayOdds': away_odds
                    })

        if data:
            df = pd.DataFrame(data)
            # Append to the SQL table
            df.to_sql('weekly_odds', con=engine, if_exists='append', index=False)
            print(f"Data from {SPORT} league inserted into the database.")
            
engine.dispose()