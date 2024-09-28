# https://github.com/luukhopman/football-logos/blob/master/logos/C1/FC%20Stade-Lausanne-Ouchy.png

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

actualyear = datetime.date.today().strftime("%Y")
# Function to get the week number of the year, starting on Monday
def get_week_number(date):
    return int(date.isocalendar().week)

cnx =mysql.connector.connect(
    host='eu-cluster-west-01.k8s.cleardb.net',
    database='heroku_9f69e70d94a5650', #heroku_f8c05e23b7aa26a
    user='b902878f5a41b4',
    password='4acedb6a',
    port='3306'
)

cursor = cnx.cursor()

today = datetime.date.today()
current_week = int(today.isocalendar().week)
next_week= int(today.isocalendar().week)+1
current_week_start = datetime.datetime.now().date() - datetime.timedelta(days=datetime.datetime.now().weekday())
current_week_end = current_week_start + datetime.timedelta(days=6)
next_week_end=current_week_start + datetime.timedelta(days=13)
date_548_days_ago = datetime.datetime.now().date() - datetime.timedelta(days=548)
query = ("SELECT DISTINCT League, date(Date) as Date, Local, Visitor, Goalslocal, Goalsvisitor, Result, year(date) as Year "
            "FROM heroku_9f69e70d94a5650.football_results " # football
            "ORDER BY Date ASC"
            )
cal_df=pd.read_sql(query,cnx)
cal_df=cal_df[(cal_df['Date'] <= next_week_end)]
# Assign the week number to a new column
cal_df['Week'] = cal_df['Date'].apply(get_week_number)
current_week_start_str = current_week_start.strftime('%Y-%m-%d')
date_548_days_ago_str = date_548_days_ago.strftime('%Y-%m-%d')

query = (f"SELECT League, fre.Local as Team, COUNT(fre.Result) AS GP, SUM(fre.Goalslocal) AS GF, SUM(fre.Goalsvisitor) AS GA, 'Home' AS HA "
         f"FROM football_results fre "
         f"WHERE fre.Date BETWEEN '{date_548_days_ago_str}' AND '{current_week_start_str}' "
         f"GROUP BY League, fre.Local "
         f"UNION ALL "
         f"SELECT League, fre.Visitor as Team, COUNT(fre.Result) AS GP, SUM(fre.Goalsvisitor) AS GF, SUM(fre.Goalslocal) AS GA, 'Away' AS HA "
         f"FROM football_results fre "
         f"WHERE fre.Date BETWEEN '{date_548_days_ago_str}' AND '{current_week_start_str}' "
         f"GROUP BY League, fre.Visitor"
            )
df_tabla=pd.read_sql(query,cnx)

cursor.close()
cnx.close()

df_tabla = df_tabla.dropna(subset=['GP', 'GF', 'GA'])
df_tabla=df_tabla.astype(({"GP": int, "GF": int,"GA": int}))

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

# Concatenate Team and League to create a unique index
df_calc['Team_League'] = df_calc['Team'] + ' - ' + df_calc['League']

# Pivot the DataFrame using the new unique index
df_ad = df_calc.pivot(index='Team_League', columns='HA', values=['attack', 'defense'])

# If you want to split the concatenated column back into 'Team' and 'League' for readability
df_ad.reset_index(inplace=True)
df_ad[['Team', 'League']] = df_ad['Team_League'].str.split(' - ', expand=True)
# df_ad.drop(columns=['Team_League'], inplace=True)


df_ad.columns = df_ad.columns.swaplevel().to_flat_index().map('_'.join)
df_ad=df_ad.reset_index()
# Print or inspect the resulting DataFrame
# print(df_ad)


cal_df['Local_League'] = cal_df['Local'] + ' - ' + cal_df['League']
cal_df['Visitor_League'] = cal_df['Visitor'] + ' - ' + cal_df['League']

print(cal_df['Week'])
print(cal_df['Year'])
'''Genera tabla con partidos de la semana'''
df_week=cal_df.loc[(cal_df['Week'] == current_week) & (cal_df['Year'] == int(actualyear)) ]

print(df_week)

df_week=pd.merge(df_week,df_ad[['_Team_League','Home_attack', 'Home_defense']],left_on='Local_League', right_on='_Team_League', how='left')
df_week=df_week.drop(columns=['_Team_League'])
df_week=pd.merge(df_week,df_ad[['_Team_League','Away_attack', 'Away_defense']],left_on='Visitor_League', right_on='_Team_League', how='left')
df_week=df_week.drop(columns=['_Team_League'])

df_week=pd.merge(df_week,df_calc[df_calc['HA'] == 'Home'][['Team_League','avefav']],left_on='Local_League', right_on='Team_League', how='left')
df_week.rename(columns = {'avefav':'avefav_home'}, inplace = True)
df_week=df_week.drop(columns=['Team_League'])
df_week=pd.merge(df_week,df_calc[df_calc['HA'] == 'Away'][['Team_League','avefav']],left_on='Visitor_League', right_on='Team_League', how='left')
df_week.rename(columns = {'avefav':'avefav_away'}, inplace = True)
df_week=df_week.drop(columns=['Team_League'])

print(df_week)

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
df_week['Round']=None

df_final=df_week[['League', 'Round', 'Week', 'Year', 'Date', 'Local', 'Visitor', 'max_prob', 'bet', 'phg', 'pag']]
df_final=df_final.round({'phg': 0, 'pag': 0})
df_final['Created']=datetime.datetime.now()
df_final['bet']=np.where((df_final['phg'] == df_final['pag']) & (df_final['bet'] == 'Local'),'Tie->Local', \
        np.where((df_final['phg'] == df_final['pag']) & (df_final['bet'] == 'Visitor'),'Tie->Visitor', \
        np.where((df_final['phg'] == df_final['pag']) & (df_final['bet'] == 'Tie'),'Tie', \
        df_final['bet'])))

print(df_final)

# Define the connection URL
connection_url = 'mysql://b902878f5a41b4:4acedb6a@eu-cluster-west-01.k8s.cleardb.net/heroku_9f69e70d94a5650' #?reconnect=true

# Create the engine
engine = create_engine(connection_url) 

# # Create a SQLAlchemy engine to connect to the database
# engine = create_engine(f'mysql://{user}:{password}@{host}/{database}')

# Insert data from the DataFrame to MySQL
table_name = 'predictions_espn'
df_final.to_sql(table_name, con=engine, if_exists='replace', index=False)

# Append the dataframe to the MySQL table
df_final.to_sql('predictions_history', con=engine, if_exists='append', index=False) # changed from predictions_history_espn
print('Predictions completed!')

# Close the connection to MySQL
engine.dispose()