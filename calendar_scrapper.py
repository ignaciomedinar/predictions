import requests
from bs4 import BeautifulSoup
import mysql.connector
from sqlalchemy import create_engine
import pandas as pd
import datetime

# Fetch the website data
url='https://www.soccerstats.com/'
leagues=('england','italy','spain','france','germany','mexico','netherlands','portugal')
actualyear = datetime.date.today().strftime("%Y")

# Extract relevant information from the parsed data
# ... (code to extract and process data from the website)
def datenumber(month):
    match month:
        case "Jan":
            dateno =1
        case "Feb":
            dateno =2
        case "Mar":
            dateno =3
        case "Apr":
            dateno =4
        case "May":
            dateno =5
        case "Jun":
            dateno =6
        case "Jul":
            dateno =7
        case "Aug":
            dateno =8
        case "Sep":
            dateno=9
        case "Oct":
            dateno=10
        case "Nov":
            dateno=11
        case "Dec":
            dateno=12
    return(int(dateno))

def tabla():
    yr=int(actualyear)-1
    while yr<=int(actualyear):
        for mt in range(1,12):
            for country in leagues:
                if country == 'mexico' and yr==int(actualyear):
                    urlleague=url+'results.asp?league=mexico2&pmtype=month'+str(mt)+''
                elif country == 'mexico' and yr==int(actualyear)-1:
                    urlleague=url+'results.asp?league=mexico&pmtype=month'+str(mt)+''
                else:
                    if yr==int(actualyear):
                         urlleague=url+'results.asp?league='+country+'&pmtype=month'+str(mt)+''
                    else:
                        urlleague=url+'results.asp?league='+country+'_'+str(yr)+'&pmtype=month'+str(mt)+''
                page = requests.get(urlleague)
                soup = BeautifulSoup(page.content, 'html.parser')

                # Scrape dates and teams with scores
                table = soup.find('table', id='btable')
                rows = table.find_all('tr')
                try:
                    for row in range(0,len(rows)):
                        if len(rows[row].find_all('td')[0].get_text(strip=True))>3:
                            dt = rows[row].find_all('td')[0].get_text(strip=True)
                            if len(dt) == 8:
                                dat =  datetime.date(int(yr), datenumber(dt[5:8]), int(dt[3:4]))
                            else:
                                dat =  datetime.date(int(yr), datenumber(dt[6:9]), int(dt[3:5]))
                            local = rows[row].find_all('td')[1].get_text(strip=True)
                            score =  rows[row].find_all('td')[2].get_text(strip=True)
                            if score.find('-')>0 and dat<=datetime.date.today():
                                goalslocal = int(score[:score.find('-')])
                                goalsvisitor = int(score[score.find('-')+1:])
                            else:
                                goalslocal = ''
                                goalsvisitor = ''
                            visitor =  rows[row].find_all('td')[3].get_text(strip=True)
                        
                            # print(dat, local, goalslocal, visitor, goalsvisitor)
                            week= int(dat.isocalendar().week)
                            if goalslocal>goalsvisitor: 
                                result = "l" 
                            elif goalslocal<goalsvisitor: 
                                result = "v" 
                            elif goalslocal=='' or goalsvisitor=='': 
                                result = ""
                            else:
                                result = 't'
                            new_row={'League': country,'Round': '','Week': week,'Year': yr,'Date': dat, 
                                    'Local': local,'Visitor': visitor,'Goalslocal': goalslocal,'Goalsvisitor': goalsvisitor,
                                    'Result': result}
                            
                            df.loc[len(df)] = new_row
                except:
                    print(country+str(yr)+str(mt)+": No record")
        yr=yr+1
                    
    return(df)

df=pd.DataFrame(columns=['League','Round','Week','Year','Date','Local','Visitor','Goalslocal','Goalsvisitor','Result'])
calendar = tabla()
# print(prueba)

# Connect to the MySQL database
# conn = mysql.connector.connect(
#     host="localhost",
#     user="root",
#     password="milanesa",
#     # database="football"
# )
conn = mysql.connector.connect(
    host='sql7.freemysqlhosting.net',
    database='sql7618393',
    user='sql7618393',
    password='iYNUZFVcWQ',
    port='3306'
)
# cursor = conn.cursor()
# sql = 'CREATE DATABASE IF NOT EXISTS football;'
# cursor.execute(sql)
# sql='USE football;'
# cursor.execute(sql)
# sql='DROP TABLE IF EXISTS football.football_results'
# cursor.execute(sql)
cursor = conn.cursor()
sql = 'CREATE DATABASE IF NOT EXISTS sql7618393;'
cursor.execute(sql)
sql='USE sql7618393;'
cursor.execute(sql)
sql='DROP TABLE IF EXISTS sql7618393.football_results'
cursor.execute(sql)

conn.close()

# Define the connection parameters
# user = 'root'
# password = 'milanesa'
# host = 'localhost'
# database = 'football'


# Create a SQLAlchemy engine to connect to the database
# engine = create_engine(f'mysql://{user}:{password}@{host}/{database}')
# Define the connection URL
connection_url = 'mysql+mysqlconnector://sql7618393:iYNUZFVcWQ@sql7.freemysqlhosting.net:3306/sql7618393'

# Create the engine
engine = create_engine(connection_url)

# Insert data from the DataFrame to MySQL
table_name = 'football_results'
calendar.to_sql(table_name, con=engine, if_exists='replace', index=False)

# Close the connection to MySQL
engine.dispose()

print('Calendar created successfully!')