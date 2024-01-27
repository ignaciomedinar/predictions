import requests
from bs4 import BeautifulSoup
import mysql.connector
from sqlalchemy import create_engine
import pandas as pd
import datetime
import time

# Fetch the website data
url='https://www.soccerstats.com/'
leagues=('england','italy','spain','france','germany','mexico','netherlands','portugal','greece','brazil')
# leagues=('mexico','other')
actualyear = datetime.date.today().strftime("%Y")
actualmonth = datetime.date.today().strftime("%m")

# Extract relevant information from the parsed data
# ... (code to extract and process data from the website)
def datenumber(month):
    match month:
        case "JAN" | "ENE":
            dateno =1
        case "FEB":
            dateno =2
        case "MAR":
            dateno =3
        case "APR" | "ABR":
            dateno =4
        case "MAY":
            dateno =5
        case "JUN":
            dateno =6
        case "JUL":
            dateno =7
        case "AUG" | "AGO":
            dateno =8
        case "SEP":
            dateno=9
        case "OCT":
            dateno=10
        case "NOV":
            dateno=11
        case "DEC" | "DIC":
            dateno=12
    return(int(dateno))

def mexico_mediotiempo(yr,country='mexico'):
    teamsmex= {'Atlético de San Luis':'A. San Luis','Atlas':'Atlas','América':'CF America','León':'Club Leon','Cruz Azul':'Cruz Azul','Chivas':'Guadalajara','FC Juárez':'Juarez','Mazatlán':'Mazatlan','Monterrey':'Monterrey','Necaxa':'Necaxa','Pachuca':'Pachuca','Puebla':'Puebla','Pumas':'Pumas UNAM','Club Querétaro':'Queretaro','Santos':'Santos Laguna','Tigres':'Tigres','Club Tijuana':'Tijuana','Toluca':'Toluca'}
    # data = [['Atlético de San Luis'],['A. San Luis'],['Atlas'],['Atlas'],['América'],['CF America'],['León'],['Club Leon'],['Cruz Azul'],['Cruz Azul'],['Chivas'],['Guadalajara'],['FC Juárez'],['Juarez'],['Mazatlán'],['Mazatlan'],['Monterrey'],['Monterrey'],['Necaxa'],['Necaxa'],['Pachuca'],['Pachuca'],['Puebla'],['Puebla'],['Pumas'],['Pumas UNAM'],['Club Querétaro'],['Queretaro'],['Santos'],['Santos Laguna'],['Tigres'],['Tigres'],['Club Tijuana'],['Tijuana'],['Toluca'],['Toluca']]
    # data =['Atlético de San Luis'],[' A. San Luis'],['Atlas'],[' Atlas'],['América'],[' CF America'],['León'],[' Club Leon'],['Cruz Azul'],[' Cruz Azul'],['Chivas'],[' Guadalajara'],['FC Juárez'],[' Juarez'],['Mazatlán'],[' Mazatlan'],['Monterrey'],[' Monterrey'],['Necaxa'],[' Necaxa'],['Pachuca'],[' Pachuca'],['Puebla'],[' Puebla'],['Pumas'],[' Pumas UNAM'],['Club Querétaro'],[' Queretaro'],['Santos'],[' Santos Laguna'],['Tigres'],[' Tigres'],['Club Tijuana'],[' Tijuana'],['Toluca'],[' Toluca'],
    # dfmex=pd.DataFrame(data, columns=['MedioTiempo', 'SoccerStats'])
    temps=['apertura','clausura']
    for temp in temps:
        if temp=='apertura':
            tp='199'
            anio=yr
        else:
            tp='385'
            anio=yr+1
        for x in range(1,18):
            urlleague = 'https://www.mediotiempo.com/futbol/liga-mx/calendario/'+tp+'-'+str(yr)+'/regular/'+str(x)
            page = requests.get(urlleague)
            soup = BeautifulSoup(page.content, 'html.parser')
            table=soup.find('table',class_="ctr-stadistics-header__table")
            try:
                rows=table.find_all('tr')
                dat=None
                for row in range(1,len(rows)):
                    fecha_div = rows[row].find('div', class_="ctr-stadistics-header__date")
                    fecha = fecha_div.text.strip() if fecha_div else None
                    if fecha is not None and fecha != '':
                        dat= datetime.date(int(anio), datenumber(fecha[3:6].upper()), int(fecha[0:2]))
                    first_team_div = rows[row].find('div', class_='ctr-stadistics-header__first-team')
                    if first_team_div:
                        team_name_div = first_team_div.find('div', class_='ctr-stadistics-header__team-name')
                        if team_name_div:
                            local = team_name_div.text.strip()
                        else:
                            local=None
                    else:
                        local = None
                    second_team_div = rows[row].find('div', class_='ctr-stadistics-header__second-team')
                    if second_team_div:
                        team_name_div = second_team_div.find('div', class_='ctr-stadistics-header__team-name')
                        if team_name_div:
                            visitor = team_name_div.text.strip()
                        else:
                            visitor=None
                    else:
                        visitor = None
                    score_div = rows[row].find('div', class_='ctr-stadistics-header__result-team')
                    if score_div:
                        span = score_div.find('span')
                        if span:
                            try:
                                goalslocal= int(span.text.split("-")[0].strip())
                            except:
                                goalslocal = ''
                        else:
                            goalslocal=None
                    else:
                        goalslocal=None
                    if str:
                        if score_div:
                            span = score_div.find('span')
                            if span:
                                try:
                                    goalsvisitor=int(span.text.split("-")[1].strip())
                                except:
                                    goalsvisitor = ''
                            else:
                                goalsvisitor=None
                    else:
                        goalsvisitor=None

                    week= int(dat.isocalendar().week)
                    if goalslocal>goalsvisitor: 
                        result = "l" 
                    elif goalslocal<goalsvisitor: 
                        result = "v" 
                    elif goalslocal=='' or goalsvisitor=='': 
                        result = ""
                    else:
                        result = 't'
                    new_row={'League': country,'Round': x,'Week': week,'Year': yr,'Date': dat, 
                            'Local': local,'Visitor': visitor,'Goalslocal': goalslocal,'Goalsvisitor': goalsvisitor,
                            'Result': result}
                    
                    df.loc[len(df)] = new_row

            except:
                print('No data in Mexico: '+str(yr)+' - '+temp+' - '+str(x))
    for i in range(len(df['Local'])):
        team = df.loc[i, 'Local']
        if team in teamsmex:
            df.loc[i, 'Local'] = teamsmex[team]
    for i in range(len(df['Visitor'])):
        team = df.loc[i, 'Visitor']
        if team in teamsmex:
            df.loc[i, 'Visitor'] = teamsmex[team]

    
def tabla(up_year,up_month):
    yr=int(up_year)
    while yr<=int(actualyear):
        mexico_mt=False
        for mt in range(up_month,13):
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
                attempt=0
                while attempt<10:
                    page = requests.get(urlleague)
                    soup = BeautifulSoup(page.content, 'html.parser')

                    # Scrape dates and teams with scores
                    table = soup.find('table', id='btable')
                    # Check if tbody exists within the table with id 'btable'
                    tbody = table.find('tbody') if table else None
                    if not tbody and country=='mexico':
                        mexico_mt =True
                    try:
                        rows = table.find_all('tr')
                        for row in range(0,len(rows)):
                            if len(rows[row].find_all('td')[0].get_text(strip=True))>3:
                                dt = rows[row].find_all('td')[0].get_text(strip=True)
                                if len(dt) == 8:
                                    dat =  datetime.date(int(yr), datenumber(dt[5:8].upper()), int(dt[3:4]))
                                else:
                                    dat =  datetime.date(int(yr), datenumber(dt[6:9].upper()), int(dt[3:5]))
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
                        print(country+str(yr)+" - "+str(mt)+": Check!")
                        attempt=10
                    except:
                        print("Error: "+country+" - "+str(yr)+"-"+str(mt)+" Att: "+str(attempt))
                        attempt = attempt + 1
                        time.sleep(15)
                        if attempt==10:
                            print(country+str(yr)+" - "+str(mt)+": No record")
        if mexico_mt ==True:
            mexico_mediotiempo(yr)
        yr=yr+1
                    
    return(df)

df=pd.DataFrame(columns=['League','Round','Week','Year','Date','Local','Visitor','Goalslocal','Goalsvisitor','Result'])

# Connect to the MySQL database
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="milanesa",
    # database="football"
)
# Connection to freemysqlhosting
# conn = mysql.connector.connect(
#     host='sql7.freemysqlhosting.net',
#     database='sql7618393',
#     user='sql7618393',
#     password='iYNUZFVcWQ',
#     port='3306'
# )

# # Connection to cleardb/heroku
# conn = mysql.connector.connect(
#     host='eu-cdbr-west-03.cleardb.net',
#     database='heroku_f8c05e23b7aa26a',
#     user='b1bb4e88305bd5',
#     password='b6aa7ee8',
#     port='3306'
# )

cursor = conn.cursor()
sql = 'CREATE DATABASE IF NOT EXISTS football;'
cursor.execute(sql)
sql='USE football;'
cursor.execute(sql)
# Check if the table exists
table_check_query = "SHOW TABLES LIKE 'football_results'"
cursor.execute(table_check_query)

table_exists = cursor.fetchone() is not None

if table_exists:
    # If the table exists, execute your query
    sql_query = "SELECT min(date) as date FROM football_results WHERE goalslocal IS NULL or goalslocal='' ORDER BY date ASC"
    sql_all= "SELECT * FROM football_results"
    cursor.execute(sql_query)
    result = cursor.fetchone()

    if result:
        # Extract year and month from the retrieved date
        try:
            up_year = result[0].year
            up_month = result[0].month
        except:
            up_year = actualyear
            up_month = actualmonth
        df_all=pd.read_sql(sql_all, conn)
        df_all['Date'] = pd.to_datetime(df_all['Date'])
        # Create comparison date for filtering
        comparison_date = pd.to_datetime(f"{up_year}-{up_month}-01")

        # Filter DataFrame based on the condition
        filtered_df = df_all[df_all['Date'] < comparison_date]

        # print(filtered_df)  # Print or do operations on the filtered DataFrame
    else:
        up_year = actualyear -1
        up_month = 1
        print("No data found matching the query.")

# cursor = conn.cursor()
# sql = 'CREATE DATABASE IF NOT EXISTS sql7618393;'
# cursor.execute(sql)
# sql='USE sql7618393;'
# cursor.execute(sql)
# sql='DROP TABLE IF EXISTS sql7618393.football_results'
# cursor.execute(sql)

# # Heroku clearmysql
# cursor = conn.cursor()
# sql = 'CREATE DATABASE IF NOT EXISTS heroku_f8c05e23b7aa26a;'
# cursor.execute(sql)
# sql='USE heroku_f8c05e23b7aa26a;'
# cursor.execute(sql)
# sql='DROP TABLE IF EXISTS heroku_f8c05e23b7aa26a.football_results'
# cursor.execute(sql)

conn.close()
# calendar = tabla(2022,1)
calendar = tabla(up_year,up_month) 
df_final=df_all._append(df,ignore_index=True)

# Select rows where 'Goalslocal', 'Goalsvisitor', and 'Result' columns are not null or empty
not_null_or_empty = (
    df_final['Goalslocal'].notnull() & 
    df_final['Goalsvisitor'].notnull() & 
    df_final['Result'].notnull() &
    (df_final['Goalslocal'] != '') & 
    (df_final['Goalsvisitor'] != '') & 
    (df_final['Result'] != '')
)
df_complete_data = df_final[not_null_or_empty]

# Define columns to check for duplicates except the specified columns
columns_to_check_duplicates = df_complete_data.columns.difference(['Goalslocal', 'Goalsvisitor', 'Result'])

# Drop duplicates based on columns except 'Goalslocal', 'Goalsvisitor', and 'Result'
unique_r = df_complete_data.drop_duplicates(subset=columns_to_check_duplicates, keep='first')
unique_rows = unique_r.drop_duplicates()

# Keep only the rows where 'Goalslocal', 'Goalsvisitor', and 'Result' columns are populated
not_null_or_empty_rows = (
    df_final[['Goalslocal', 'Goalsvisitor', 'Result']].notnull().all(axis=1) & 
    (df_final['Goalslocal'] != '') & 
    (df_final['Goalsvisitor'] != '') & 
    (df_final['Result'] != '')
)
non_empty_rows = df_final[not_null_or_empty_rows]

# Concatenate both unique rows and non-empty rows to get all required rows
all_required_rows = pd.concat([unique_rows, non_empty_rows], ignore_index=True)

# Drop duplicates after concatenation
all_required_rows = all_required_rows.drop_duplicates(keep='first')


# Define the connection parameters
user = 'root'
password = 'milanesa'
host = 'localhost'
database = 'football'


# Create a SQLAlchemy engine to connect to the database
engine = create_engine(f'mysql://{user}:{password}@{host}/{database}')

# Define the connection URL
# connection_url = 'mysql+mysqlconnector://sql7618393:iYNUZFVcWQ@sql7.freemysqlhosting.net:3306/sql7618393'

# # Define the connection URL
# connection_url = 'mysql://b1bb4e88305bd5:b6aa7ee8@eu-cdbr-west-03.cleardb.net/heroku_f8c05e23b7aa26a' #?reconnect=true


# # Create the engine
# engine = create_engine(connection_url) #, pool_recycle=3600

# Insert data from the DataFrame to MySQL
table_name = 'football_results'
# calendar.to_sql(table_name, con=engine, if_exists='replace', index=False)
all_required_rows.to_sql(table_name, con=engine, if_exists='replace', index=False)
print(all_required_rows)

# Close the connection to MySQL
engine.dispose()

print('Calendar created successfully!')