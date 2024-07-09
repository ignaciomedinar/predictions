from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np
import datetime
import math
import statsmodels.formula.api as smf
import mysql.connector
from sqlalchemy import create_engine
import sys
import time

url='https://www.soccerstats.com'
leagues=('england','italy','spain','france','germany','mexico','netherlands','portugal','greece','turkey') #,'belgium','brazil'
actualyear = datetime.date.today().strftime("%Y")

'''Función de scrapping'''
def tabla():
    c=0
    df=pd.DataFrame()
    yr=int(actualyear)-1
    while yr<=int(actualyear):
        for country in leagues:
            # Temporary fix for Mexico as Apertura is not working properly
            if country == 'mexico': # and yr==int(actualyear):
                urlleague=url+'/homeaway.asp?league='+country+'2'
            # elif country == 'mexico' and yr==int(actualyear)-1:
            #     urlleague=url+'/homeaway.asp?league='+country+''
            elif yr==int(actualyear):
                urlleague=url+'/homeaway.asp?league='+country+''
            else:
                urlleague=url+'/homeaway.asp?league='+country+'_'+str(yr)+''
            attempt=0
            while attempt<10:
                page = requests.get(urlleague)
                soup = BeautifulSoup(page.content, 'html.parser')
                divTag = soup.find_all('div',id="h2h-team1")
                divTaga = soup.find_all('div',id="h2h-team2")
                try:
                    for tag in divTag:
                        table = tag.find_all('table')
                        df_h=pd.read_html(str(table))[0]
                    c=c+1
                    df_h.columns=df_h.iloc[0]
                    df_h.drop(index=df_h.index[0],axis=0,inplace=True)
                    df_h.rename(columns = {np.nan:'Team'}, inplace=True)
                    df_h.columns = df_h.columns.fillna('Pos')
                    df_h['HA']='Home'
                    df_h['Season']=str(yr) + "-" + str(yr+1)
                    df_h['League']=country
                    df = pd.concat([df, df_h], ignore_index=True)

                    for tag in divTaga:
                        table = tag.find_all('table')
                        df_a=pd.read_html(str(table))[0]
                    df_a.columns=df_a.iloc[0]
                    df_a.drop(index=df_a.index[0],axis=0,inplace=True)
                    df_a.rename(columns = {np.nan:'Team'}, inplace=True)
                    df_a.columns = df_a.columns.fillna('Pos')
                    df_a['HA']='Away'
                    df_a['Season']=str(yr) + "-" + str(yr+1)
                    df_a['League']=country
                    df = pd.concat([df, df_a], ignore_index=True)
                    df_h.drop(df_h.index , inplace=True)
                    df_a.drop(df_a.index , inplace=True)
                    attempt=10
                    print(country, attempt)
                except:
                    print("Error: "+country+" - "+str(yr)+" Att: "+str(attempt))
                    attempt = attempt + 1
                    time.sleep(15)
                    if attempt==10:
                        print("Missed: "+country+" - "+str(yr)+" Try again later")
                        sys.exit()
        yr=yr+1
    return(df)

# # Check if today is Monday, otherwise exit
# if datetime.datetime.now().weekday() != 0:  # Monday is 0, Sunday is 6
#     sys.exit("predictions.py should only run on Mondays.")

df=pd.DataFrame(columns=['id','Pos','Team','GP','W','D','L','GF','GA','GD','Pts','HA','Season','League'])
df_tabla=tabla()

##### previous clearDB: #heroku_f8c05e23b7aa26a


# # Connect to the MySQL database
# cnx = mysql.connector.connect(user='root', password='milanesa',
#                                 host='localhost', database='football')

# cnx = mysql.connector.connect(
#     host='sql7.freemysqlhosting.net',
#     database='sql7618393',
#     user='sql7618393',
#     password='iYNUZFVcWQ',
#     port='3306'
# )
# heroku con

#mysql://b902878f5a41b4:4acedb6a@eu-cluster-west-01.k8s.cleardb.net/heroku_9f69e70d94a5650
cnx =mysql.connector.connect(
    host='eu-cluster-west-01.k8s.cleardb.net',
    database='heroku_9f69e70d94a5650', #heroku_f8c05e23b7aa26a
    user='b902878f5a41b4',
    password='4acedb6a',
    port='3306'
)

cursor = cnx.cursor()


# # Get all the weeks from the database
today = datetime.date.today()
current_week = int(today.isocalendar().week)
next_week= int(today.isocalendar().week)+1
current_week_start = datetime.datetime.now().date() - datetime.timedelta(days=datetime.datetime.now().weekday())
current_week_end = current_week_start + datetime.timedelta(days=6)
next_week_end=current_week_start + datetime.timedelta(days=13)
query = ("SELECT DISTINCT * "
            "FROM heroku_9f69e70d94a5650.football_results " # football
            "ORDER BY Date ASC"
            )

cal_df=pd.read_sql(query,cnx)
cal_df=cal_df[(cal_df['Date'] <= next_week_end)]
cursor.close()
cnx.close()

df_tabla=df_tabla.astype(({"Pos": int,"GP": int, "GF": int,"GA": int}))

'''Genera tabla df_calc donde va a tener los cálculos necesarios de cada equipo'''
# Hacer la tabla con los cálculos necesarios
df_calc=df_tabla[['League','Team','GP','GF','GA','HA']]
df_calc=df_calc.groupby(['Team','HA','League'], as_index=False).sum()
df_calc=df_calc.assign(gpjfav=df_calc['GF']/df_calc['GP'])
df_calc=df_calc.assign(gpjcon=df_calc['GA']/df_calc['GP'])

df_mean=df_calc.groupby(['League','HA']).agg(avefav=('gpjfav','mean'),avecon=('gpjcon','mean'))
df_calc=pd.merge(df_mean, df_calc, on=['League', 'HA'], how='right')

df_calc.loc[df_calc['gpjfav']>0, 'attack']=df_calc['gpjfav']/df_calc['avefav']
df_calc.loc[df_calc['gpjfav']<=0, 'attack']=df_calc['avefav']
df_calc.loc[df_calc['gpjcon']>0, 'defense']=df_calc['gpjcon']/df_calc['avecon']
df_calc.loc[df_calc['gpjcon']<=0, 'defense']=df_calc['avecon']
df_calc.loc[df_calc['GP']==0, 'defense']=df_calc['avecon']
df_calc.loc[df_calc['GP']==0, 'attack']=df_calc['avefav']
    
df_calc.fillna(1, inplace = True)

# df_ad=df_calc.pivot('Team', 'HA', ['attack', 'defense'])
df_ad = df_calc.pivot(index='Team', columns='HA', values=['attack', 'defense'])


df_ad.columns = df_ad.columns.swaplevel().to_flat_index().map('_'.join)
df_ad=df_ad.reset_index()

'''Genera tabla con partidos de la semana'''
df_week=cal_df.loc[(cal_df['Week'] == current_week) & (cal_df['Year'] == int(actualyear)) ]
df_week=pd.merge(df_week,df_ad[['Team','Home_attack', 'Home_defense']],left_on='Local', right_on='Team', how='left')
df_week=df_week.drop(columns=['Team'])
df_week=pd.merge(df_week,df_ad[['Team','Away_attack', 'Away_defense']],left_on='Visitor', right_on='Team', how='left')
df_week=df_week.drop(columns=['Team'])
df_week=pd.merge(df_week,df_calc[df_calc['HA'] == 'Home'][['Team','avefav']],left_on='Local', right_on='Team', how='left')
df_week.rename(columns = {'avefav':'avefav_home'}, inplace = True)
df_week=df_week.drop(columns=['Team'])
df_week=pd.merge(df_week,df_calc[df_calc['HA'] == 'Away'][['Team','avefav']],left_on='Visitor', right_on='Team', how='left')
df_week.rename(columns = {'avefav':'avefav_away'}, inplace = True)
df_week=df_week.drop(columns=['Team'])

df_week=df_week.assign(phg=df_week['Home_attack']*df_week['Away_defense']*df_week['avefav_home'])
df_week=df_week.assign(pag=df_week['Away_attack']*df_week['Home_defense']*df_week['avefav_away'])
df_week=df_week.assign(ptg=df_week['phg']+df_week['pag'])

for i in range(8):
    ag="p_"+str(i)+"ag"
    hg="p_"+str(i)+"hg"
    df_week[str(ag)]=((df_week['pag']**i)*np.exp(-df_week['pag']))/(math.factorial(i))
    df_week[str(hg)]=((df_week['phg']**i)*np.exp(-df_week['phg']))/math.factorial(i)

for i in range(8):
    for j in range(8):
        if i>j:
            df_week["p"+str(i)+"-"+str(j)]=df_week["p_"+str(i)+"hg"]*df_week["p_"+str(j)+"ag"]
        elif i==j:
            df_week["p"+str(i)+"-"+str(j)]=df_week["p_"+str(i)+"hg"]*df_week["p_"+str(j)+"ag"]
        elif i<j:
            df_week["p"+str(i)+"-"+str(j)]=df_week["p_"+str(i)+"hg"]*df_week["p_"+str(j)+"ag"]

df_week["home_win"]=df_week["p1-0"]+df_week["p2-0"]+df_week["p3-0"]+df_week["p4-0"]+df_week["p5-0"]+df_week["p6-0"]+df_week["p7-0"]+df_week["p2-1"]+df_week["p3-1"]+df_week["p4-1"]+df_week["p5-1"]+df_week["p6-1"]+df_week["p7-1"]+df_week["p3-2"]+df_week["p4-2"]+df_week["p5-2"]+df_week["p6-2"]+df_week["p7-2"]+df_week["p4-3"]+df_week["p5-3"]+df_week["p6-3"]+df_week["p7-3"]+df_week["p5-4"]+df_week["p6-4"]+df_week["p7-4"]+df_week["p6-5"]+df_week["p7-5"]+df_week["p7-6"]
df_week["draw"]=df_week["p0-0"]+df_week["p1-1"]+df_week["p2-2"]+df_week["p3-3"]+df_week["p4-4"]+df_week["p5-5"]+df_week["p6-6"]+df_week["p7-7"]
df_week["away_win"]=df_week["p0-1"]+df_week["p0-2"]+df_week["p1-2"]+df_week["p0-3"]+df_week["p1-3"]+df_week["p2-3"]+df_week["p0-4"]+df_week["p1-4"]+df_week["p2-4"]+df_week["p3-4"]+df_week["p0-5"]+df_week["p1-5"]+df_week["p2-5"]+df_week["p3-5"]+df_week["p4-5"]+df_week["p0-6"]+df_week["p1-6"]+df_week["p2-6"]+df_week["p3-6"]+df_week["p4-6"]+df_week["p5-6"]+df_week["p0-7"]+df_week["p1-7"]+df_week["p2-7"]+df_week["p3-7"]+df_week["p4-7"]+df_week["p5-7"]+df_week["p6-7"]
df_week["max_prob"]=df_week[["home_win", "draw","away_win"]].max(axis=1)

col0 = 'max_prob'
col1 = 'home_win'
col2 = 'away_win'
col3 = 'draw'
conditions = [ df_week[col0] == df_week[col1], df_week[col0] == df_week[col2], df_week[col0] == df_week[col3] ]
choices = [ "Local", 'Visitor', 'Tie' ]
        
df_week["bet"] = np.select(conditions, choices, default=np.nan)
df_week=df_week.sort_values(by="max_prob", ascending=False)

df_final=df_week[['League', 'Round', 'Week', 'Year', 'Date', 'Local', 'Visitor', 'max_prob', 'bet', 'phg', 'pag']]
df_final=df_final.round({'phg': 0, 'pag': 0})
df_final['Created']=datetime.datetime.now()

# # Define the connection parameters
# # These parameters are local
# user = 'root'
# password = 'milanesa'
# host = 'localhost'
# database = 'football'

# Theses parameters are from https://www.freemysqlhosting.net/account/
# Server = 'sql7.freemysqlhosting.net'
# Name= 'sql7618393'
# Username= 'sql7618393'
# Password= 'iYNUZFVcWQ'
# Port = 3306

# Define the connection URL
# connection_url = 'mysql+mysqlconnector://sql7618393:iYNUZFVcWQ@sql7.freemysqlhosting.net:3306/sql7618393'

# Create the engine
# engine = create_engine(connection_url)

# Define the connection URL
connection_url = 'mysql://b902878f5a41b4:4acedb6a@eu-cluster-west-01.k8s.cleardb.net/heroku_9f69e70d94a5650' #?reconnect=true

# Create the engine
engine = create_engine(connection_url) 

# # Create a SQLAlchemy engine to connect to the database
# engine = create_engine(f'mysql://{user}:{password}@{host}/{database}')

# Insert data from the DataFrame to MySQL
table_name = 'predictions'
df_final.to_sql(table_name, con=engine, if_exists='replace', index=False)

# Append the dataframe to the MySQL table
df_final.to_sql('predictions_history', con=engine, if_exists='append', index=False)
print('Predictions completed!')

# Close the connection to MySQL
engine.dispose()

'''
Siguientes pasos:
1. Crear 3 tablas en html - partidos con resultados, predicciones y resultados vs predicciones
2. Crear un formulario para que el usuario meta cantidad y número de partidos para que le diga el 
   monto a apostar por juego
3. Crear un diseño mejor
4. Meter google ads
5. Comprar dominio
6. Publicar
'''