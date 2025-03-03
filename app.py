from flask import Flask, render_template, request, send_from_directory, redirect
import mysql.connector
import datetime
from dateutil.relativedelta import relativedelta
import calendar
import smtplib
# from dotenv import load_dotenv
import os
import pandas as pd
from itertools import combinations

app = Flask(__name__)

def add_days(date, days):
    return date + datetime.timedelta(days=days)
# Register the custom filter
app.jinja_env.filters['add_days'] = add_days

# @app.before_request
# def https_redirect():
#     if not request.is_secure and request.headers.get('X-Forwarded-Proto') != 'https':
#         return redirect(request.url.replace('http://', 'https://'), code=301)

@app.route('/')
def home():
    title = 'Welcome to Goal Genius!'
    message='Goal Genius is a platform that offers football result predictions on football matches from \
        the most significant Leagues. It also provides Dates, Results, and the Matches that will \
        take place in the next weeks.<br><br> \
        The predictions are based \
        on a statistic model considering goals scored and goals received by teams in the last two years.'
    
    cnx = mysql.connector.connect(
    host=os.getenv('MYSQL_HOST'),
    database=os.getenv('MYSQL_DATABASE'),
    user=os.getenv('MYSQL_USER'),
    password=os.getenv('MYSQL_PASSWORD'),
    port=os.getenv('MYSQL_PORT'),
    charset='utf8',  # Ensure the connection uses UTF-8
    use_unicode=True
    )

    cursor = cnx.cursor()
    previous_week_start = (datetime.datetime.now().date() - datetime.timedelta(days=datetime.datetime.now().weekday())) - datetime.timedelta(days=7)
    current_week_start = previous_week_start + datetime.timedelta(days=7)
    current_week_end = previous_week_start + datetime.timedelta(days=13)
    di=current_week_start.day
    df=current_week_end.day
    mi = calendar.month_abbr[current_week_start.month]  # Access month abbreviation using the month number
    mf = calendar.month_abbr[current_week_end.month]  # Access month abbreviation using the month number
    yf=current_week_end.year

    # Query the database for the results for the current week
    query = ('''
             SELECT DISTINCT 
             pr.League, pr.Round, pr.Week, pr.Year, pr.Date, pr.Local, pr.Visitor,
             pr.bet, pr.phg, pr.pag, pr.Created, 
             case when lg.Country not in ('America', 'Europe','Africa','Asia','Concacaf','Conmebol', 'Europe', 'World') 
            and lg.league not in ( 
            'Copa Do Brazil', 
            'U.S. Open Cup', 
            'Copa de la Liga de Inglaterra', 
            'Copa de Alemania', 
            'Coppa Italia',
            'English EFL Trophy')
             and lower(lg.League) not like '%cup%' 
            and lower(lg.League) not like '%copa%' 
             then pr.max_prob else 0 end as max_prob, 
             r.result, 
             CASE WHEN r.goalslocal IS NULL THEN '' ELSE r.goalslocal END AS goalslocal, 
             CASE WHEN r.goalsvisitor IS NULL THEN '' ELSE r.goalsvisitor END AS goalsvisitor, 
             fl.flag_url, lg.country,
             pr.top_homebookmaker, pr.top_homeodds,
             pr.top_drawbookmaker, pr.top_drawodds,
             pr.top_awaybookmaker, pr.top_awayodds
             FROM Predictions.predictions pr 
             LEFT JOIN Predictions.results r 
             ON pr.date = r.date AND pr.local = r.local AND pr.visitor = r.visitor 
             LEFT JOIN Predictions.leagues lg 
             ON UPPER(lg.League) = UPPER(pr.League) 
             LEFT JOIN Predictions.flags fl 
             ON UPPER(fl.Country) = UPPER(lg.Country) 
             WHERE pr.date >= %s AND pr.date <= %s 
             ORDER BY case when lg.Country not in ('America', 'Europe','Africa','Asia','Concacaf','Conmebol', 'Europe', 'World') 
            and lg.league not in ( 
            'Copa Do Brazil', 
            'U.S. Open Cup', 
            'Copa de la Liga de Inglaterra', 
            'Copa de Alemania', 
            'Coppa Italia',
            'English EFL Trophy')
            and lower(lg.League) not like '%cup%' 
            and lower(lg.League) not like '%copa%' 
            then pr.max_prob else 0 end DESC
            limit 1
             '''
                )
    cursor.execute(query, (current_week_start, current_week_end))
    # Get the column names
    columns = [col[0] for col in cursor.description]

    # Fetch all rows and convert to list of dictionaries
    predictions = [dict(zip(columns, row)) for row in cursor.fetchall()]

    # Close the database connection
    cursor.close()
    cnx.close()


    return render_template('homepage.html', title=title, message=message, predictions=predictions)

@app.route('/calendar')
def show_matches():
    title = 'Next Matches'

    cnx = mysql.connector.connect(
    host=os.getenv('MYSQL_HOST'),
    database=os.getenv('MYSQL_DATABASE'),
    user=os.getenv('MYSQL_USER'),
    password=os.getenv('MYSQL_PASSWORD'),
    port=os.getenv('MYSQL_PORT'),
    charset='utf8',  # Ensure the connection uses UTF-8
    use_unicode=True
    )

    cursor = cnx.cursor()
    current_week_start = datetime.datetime.now().date() - datetime.timedelta(days=datetime.datetime.now().weekday())
    current_week_end = current_week_start + datetime.timedelta(days=6)
    six_months = datetime.date.today() + relativedelta(months=+4)

    # Query the database for the results for the current week
    query = ("SELECT fr.*, fl.flag_url, "
            "lg.country "
            "FROM results fr "
            "left join Predictions.leagues lg "
            "on fr.league=lg.league "
            "left join Predictions.flags fl "
            "on upper(fl.country) = upper(lg.country) "
            "WHERE date >= %s "
            "AND date <= %s "
            "AND (goalslocal ='' "
            "or goalslocal is null) "
            "ORDER BY date asc, fr.league"
            )
    cursor.execute(query, (current_week_start, six_months,))
    # Get the column names
    columns = [col[0] for col in cursor.description]

    # Fetch all rows and convert to list of dictionaries
    matches = [dict(zip(columns, row)) for row in cursor.fetchall()]

    # Close the database connection
    cursor.close()
    cnx.close()

    # Pass the results and weeks to the HTML template
    return render_template("table_calendar.html", title=title,matches=matches)

@app.route('/results')
def show_results():
    title = 'Results'
    cnx = mysql.connector.connect(
    host=os.getenv('MYSQL_HOST'),
    database=os.getenv('MYSQL_DATABASE'),
    user=os.getenv('MYSQL_USER'),
    password=os.getenv('MYSQL_PASSWORD'),
    port=os.getenv('MYSQL_PORT'),
    charset='utf8',  # Ensure the connection uses UTF-8
    use_unicode=True
    )
    cursor = cnx.cursor()
    previous_week_start = (datetime.datetime.now().date() - datetime.timedelta(days=datetime.datetime.now().weekday())) - datetime.timedelta(days=7)
    current_week_end = previous_week_start + datetime.timedelta(days=13)
    current_week=datetime.date.today().isocalendar()[1]
    current_year=datetime.date.today().year

    # Get all the weeks from the database
    query = ("SELECT DISTINCT concat(Year,'-W',week(date,3)), year, week(date,3) "
                "FROM Predictions.results "
                "WHERE concat(year,week)<=%s%s "
                "ORDER by year desc, week(date,3) DESC"
                )
    cursor.execute(query, (current_year,current_week,))
    weeks = [week[0] for week in cursor.fetchall()]
    first_dates_week=[datetime.datetime.strptime(week + '-1', "%Y-W%W-%w") for week in weeks]
    last_dates_week=[first + datetime.timedelta(days=6) for first in first_dates_week]

    selected_week_start = request.args.get('week')

    # Get all the teams from the database
    query = ("SELECT DISTINCT Local "
                "FROM Predictions.results "
                "ORDER BY Local ASC"
                )
    cursor.execute(query)
    teams = [team[0] for team in cursor.fetchall()]

    if selected_week_start:
        # selected_week_start = selected_week_start.strftime('%Y-%m-%d %H:%M:%S')
        selected_week_start=datetime.datetime.strptime(selected_week_start,'%Y-%m-%d %H:%M:%S')
        # print(type(selected_week_start))
        # print(selected_week_start)
        selected_week_end = selected_week_start + datetime.timedelta(days=6)
        # Query the database for the results for the current week
        query = ("SELECT distinct fr.*, ph.bet, case when ph.bet is null or fr.goalslocal ='' "
                    "then 'NA' when upper(fr.Result)=upper(left(ph.bet,1)) "
                    "then 'Correct' else 'Incorrect' end as success, fl.flag_url, "
                    "ph.phg, ph.pag, "
                    "case when lg.Country not in ('America', 'Europe','Africa','Asia','Concacaf','Conmebol', 'Europe', 'World') "
                    "and lg.league not in ( "
                    "'Copa Do Brazil', "
                    "'U.S. Open Cup', "
                    "'Copa de la Liga de Inglaterra', "
                    "'Copa de Alemania', "
                    "'Coppa Italia', "
                    "'English EFL Trophy') "
                    "and lower(lg.League) not like '%cup%' "
                    "and lower(lg.League) not like '%copa%' "
                    "then ph.max_prob else 0 end as max_prob, "
                    "lg.country "
                    "FROM Predictions.results fr "
                    "left join Predictions.predictions_history ph "
                    "on fr.date = ph.date and fr.local=ph.local and fr.visitor=ph.visitor "
                    "left join Predictions.leagues lg "
                    "on lg.league = fr.league "
                    "left join Predictions.flags fl "
                    "on upper(fl.country) = coalesce(upper(lg.country),upper(fr.league)) "
                    "WHERE fr.date >= %s AND fr.date <= %s "
                    "AND fr.goalslocal <>'' "
                    "ORDER BY max_prob DESC"
                    )
        cursor.execute(query, (selected_week_start, selected_week_end))
        # print("selección: " + selected_week_start)
    else:
        # Query the database for the results for the current week
        query = ("SELECT distinct fr.*, ph.bet, case when ph.bet is null or fr.goalslocal ='' "
                    "then 'NA' when upper(fr.Result)=upper(left(ph.bet,1)) "
                    "then 'Correct' else 'Incorrect' end as success, fl.flag_url, "
                    "ph.phg, ph.pag, "
                    "case when lg.Country not in ('America', 'Europe','Africa','Asia','Concacaf','Conmebol', 'Europe', 'World') "
                    "and lg.league not in ( "
                    "'Copa Do Brazil', "
                    "'U.S. Open Cup', "
                    "'Copa de la Liga de Inglaterra', "
                    "'Copa de Alemania', "
                    "'Coppa Italia', "
                    "'English EFL Trophy') " 
                    "and lower(lg.League) not like '%cup%' "
                    "and lower(lg.League) not like '%copa%' "
                    "then ph.max_prob else 0 end as max_prob, "
                    "lg.country "
                    "FROM Predictions.results fr "
                    "left join Predictions.predictions_history ph "
                    "on fr.date = ph.date and fr.local=ph.local and fr.visitor=ph.visitor "
                    "left join Predictions.leagues lg "
                    "on lg.league = fr.league "
                    "left join Predictions.flags fl "
                    "on upper(fl.Country) = coalesce(upper(lg.country),upper(fr.league)) "
                    "WHERE fr.date >= %s AND fr.date <= %s "
                    "AND fr.goalslocal <>'' "
                    "ORDER BY max_prob DESC"
                    )
        cursor.execute(query, (previous_week_start, current_week_end))
        # print("selección: " + previous_week_start)
    # Get the column names
    columns = [col[0] for col in cursor.description]

    # Fetch all rows and convert to list of dictionaries
    results = [dict(zip(columns, row)) for row in cursor.fetchall()]
    # predict=[results['success'].count('Correct'),results['success'].count('Incorrect')]
    # correct = results[0]['success'].count('Correct')
    for i in range(len(results)):
        if results[i] is None:
            results[i] = 0.0

    correct=0
    incorrect=0
    correct_w=0
    incorrect_w=0
    for x in range(len(results)):
        if results[x]['success']=='Correct':
            correct+=1
            if results[x]['max_prob'] is not None:
                correct_w=correct_w+results[x]['max_prob']
        if results[x]['success']=='Incorrect':
            incorrect+=1
            if results[x]['max_prob'] is not None:
                incorrect_w=incorrect_w+results[x]['max_prob']

    # Top 10
    # top = sorted(results, key = lambda x: x['max_prob'], reverse = True)[:10]
    top = sorted(results, key=lambda x: x['max_prob'] if x['max_prob'] is not None else 0.0, reverse=True)[:10]

    # df=results.nlargest(5, ['max_prob']) 
    top_correct_w=0
    top_incorrect_w=0
    for x in range(len(top)):
        if top[x]['success']=='Correct':
            if top[x]['max_prob'] is not None:
                top_correct_w=top_correct_w+top[x]['max_prob']
        if top[x]['success']=='Incorrect':
            incorrect+=1
            if top[x]['max_prob'] is not None:
                top_incorrect_w=top_incorrect_w+top[x]['max_prob']

    # Close the database connection
    cursor.close()
    cnx.close()

    # Pass the results and weeks to the HTML template
    return render_template("table_results.html", title=title, results=results, first_dates_week=first_dates_week, last_dates_week=last_dates_week,correct=correct,incorrect=incorrect, selected_week_start=selected_week_start,correct_w=correct_w,incorrect_w=incorrect_w,top_correct_w=top_correct_w,top_incorrect_w=top_incorrect_w) #,predict=predict*/

@app.route('/predictions')
def show_predictions():
    title = 'Predictions'

    cnx = mysql.connector.connect(
    host=os.getenv('MYSQL_HOST'),
    database=os.getenv('MYSQL_DATABASE'),
    user=os.getenv('MYSQL_USER'),
    password=os.getenv('MYSQL_PASSWORD'),
    port=os.getenv('MYSQL_PORT'),
    charset='utf8',  # Ensure the connection uses UTF-8
    use_unicode=True
    )
    cursor = cnx.cursor()
    previous_week_start = (datetime.datetime.now().date() - datetime.timedelta(days=datetime.datetime.now().weekday())) - datetime.timedelta(days=7)
    current_week_start = previous_week_start + datetime.timedelta(days=7)
    current_week_end = previous_week_start + datetime.timedelta(days=13)
    di=current_week_start.day
    df=current_week_end.day
    mi = calendar.month_abbr[current_week_start.month]  # Access month abbreviation using the month number
    mf = calendar.month_abbr[current_week_end.month]  # Access month abbreviation using the month number
    yf=current_week_end.year

    # Query the database for the results for the current week
    query = ('''
             SELECT DISTINCT 
             pr.League, pr.Round, pr.Week, pr.Year, pr.Date, pr.Local, pr.Visitor,
             pr.bet, pr.phg, pr.pag, pr.Created, 
             case when lg.Country not in ('America', 'Europe','Africa','Asia','Concacaf','Conmebol', 'Europe', 'World') 
            and lg.league not in ( 
            'Copa Do Brazil', 
            'U.S. Open Cup', 
            'Copa de la Liga de Inglaterra', 
            'Copa de Alemania', 
            'Coppa Italia')
             and lower(lg.League) not like '%cup%' 
            and lower(lg.League) not like '%copa%' 
             then pr.max_prob else 0 end as max_prob, 
             r.result, 
             CASE WHEN r.goalslocal IS NULL THEN '' ELSE r.goalslocal END AS goalslocal, 
             CASE WHEN r.goalsvisitor IS NULL THEN '' ELSE r.goalsvisitor END AS goalsvisitor, 
             fl.flag_url, lg.country,
             pr.top_homebookmaker, pr.top_homeodds,
             pr.top_drawbookmaker, pr.top_drawodds,
             pr.top_awaybookmaker, pr.top_awayodds
             FROM Predictions.predictions pr 
             LEFT JOIN Predictions.results r 
             ON pr.date = r.date AND pr.local = r.local AND pr.visitor = r.visitor 
             LEFT JOIN Predictions.leagues lg 
             ON UPPER(lg.League) = UPPER(pr.League) 
             LEFT JOIN Predictions.flags fl 
             ON UPPER(fl.Country) = UPPER(lg.Country) 
             WHERE pr.date >= %s AND pr.date <= %s 
             ORDER BY case when lg.Country not in ('America', 'Europe','Africa','Asia','Concacaf','Conmebol', 'Europe', 'World') 
            and lg.league not in ( 
            'Copa Do Brazil', 
            'U.S. Open Cup', 
            'Copa de la Liga de Inglaterra', 
            'Copa de Alemania', 
            'Coppa Italia')
            and lower(lg.League) not like '%cup%' 
            and lower(lg.League) not like '%copa%' 
            then pr.max_prob else 0 end DESC
             '''
                )
    cursor.execute(query, (current_week_start, current_week_end))
    # Get the column names
    columns = [col[0] for col in cursor.description]

    # Fetch all rows and convert to list of dictionaries
    predictions = [dict(zip(columns, row)) for row in cursor.fetchall()]

    # Close the database connection
    cursor.close()
    cnx.close()

    # Pass the results and weeks to the HTML template
    return render_template("table_predictions.html", title=title, predictions=predictions, current_week_end=current_week_end,di=di,df=df,mi=mi,mf=mf,yf=yf)

@app.route('/invest')
def show_invest():
    title = 'Suggested Parlays'
    # selected_leagues =()

    cnx = mysql.connector.connect(
    host=os.getenv('MYSQL_HOST'),
    database=os.getenv('MYSQL_DATABASE'),
    user=os.getenv('MYSQL_USER'),
    password=os.getenv('MYSQL_PASSWORD'),
    port=os.getenv('MYSQL_PORT'),
    charset='utf8',  # Ensure the connection uses UTF-8
    use_unicode=True
    )

    cursor = cnx.cursor()
    current_week_start = datetime.datetime.now().date() - datetime.timedelta(days=datetime.datetime.now().weekday())
    current_week_end = current_week_start + datetime.timedelta(days=6)

    query = ('''
             SELECT DISTINCT 
             pr.League, pr.Round, pr.Week, pr.Year, pr.Date, pr.Local, pr.Visitor,
             pr.bet, pr.phg, pr.pag, pr.Created, 
             case when lg.Country not in ('America', 'Europe','Africa','Asia','Concacaf','Conmebol', 'Europe', 'World') 
            and lg.league not in ( 
            'Copa Do Brazil', 
            'U.S. Open Cup', 
            'Copa de la Liga de Inglaterra', 
            'Copa de Alemania', 
            'Coppa Italia')
             and lower(lg.League) not like '%cup%' 
            and lower(lg.League) not like '%copa%' 
             then pr.max_prob else 0 end as max_prob, 
             r.result, 
             CASE WHEN r.goalslocal IS NULL THEN '' ELSE r.goalslocal END AS goalslocal, 
             CASE WHEN r.goalsvisitor IS NULL THEN '' ELSE r.goalsvisitor END AS goalsvisitor, 
             fl.flag_url, lg.country,
             pr.top_homebookmaker, pr.top_homeodds,
             pr.top_drawbookmaker, pr.top_drawodds,
             pr.top_awaybookmaker, pr.top_awayodds
             FROM Predictions.predictions pr 
             LEFT JOIN Predictions.results r 
             ON pr.date = r.date AND pr.local = r.local AND pr.visitor = r.visitor 
             LEFT JOIN Predictions.leagues lg 
             ON UPPER(lg.League) = UPPER(pr.League) 
             LEFT JOIN Predictions.flags fl 
             ON UPPER(fl.Country) = UPPER(lg.Country) 
             WHERE pr.date >= %s AND pr.date <= %s 
             ORDER BY case when lg.Country not in ('America', 'Europe','Africa','Asia','Concacaf','Conmebol', 'Europe', 'World') 
            and lg.league not in ( 
            'Copa Do Brazil', 
            'U.S. Open Cup', 
            'Copa de la Liga de Inglaterra', 
            'Copa de Alemania', 
            'Coppa Italia')
            and lower(lg.League) not like '%cup%' 
            and lower(lg.League) not like '%copa%' 
            then pr.max_prob else 0 end DESC
            limit 7
             '''
                )
    cursor.execute(query, (current_week_start, current_week_end))
    # Get the column names
    columns = [col[0] for col in cursor.description]
    predictions = [dict(zip(columns, row)) for row in cursor.fetchall()]

    # Close the database connection
    cursor.close()
    cnx.close()
    df = pd.DataFrame(predictions)
    df=df.sort_values(by='max_prob', ascending=False).head(7)
    parlay_combinations = list(combinations(df.index, 3))
    parlay_data = []
    for parlay_num, (idx1, idx2, idx3) in enumerate(parlay_combinations, start=1):
        # Define a helper function to get the winner and loser based on 'victor' value
        def get_winner_loser(row):
            if row['bet'] == 'Local':
                return row['Local'], row['Visitor']
            else:
                return row['Visitor'], row['Local']
        
        # Extract winner and loser for each match in the combination
        winner1, loser1 = get_winner_loser(df.loc[idx1])
        winner2, loser2 = get_winner_loser(df.loc[idx2])
        winner3, loser3 = get_winner_loser(df.loc[idx3])

        # Retrieve probabilities for each match
        prob1 = df.loc[idx1, 'max_prob']
        prob2 = df.loc[idx2, 'max_prob']
        prob3 = df.loc[idx3, 'max_prob']

        # Retrieve probabilities for each match
        date1 = df.loc[idx1, 'Date']
        date2 = df.loc[idx2, 'Date']
        date3 = df.loc[idx3, 'Date']

        # Retrieve probabilities for each match
        flag1 = df.loc[idx1, 'flag_url']
        flag2 = df.loc[idx2, 'flag_url']
        flag3 = df.loc[idx3, 'flag_url']

        # # Convert the probabilities to numeric values (e.g., '61%' becomes 0.61)
        # prob1 = float(prob1.strip('%'))
        # prob2 = float(prob2.strip('%'))
        # prob3 = float(prob3.strip('%'))

        # print(prob1, prob2, prob3)
        # Calculate potential win (product of probabilities)
        potential_win = (1/prob1) * (1/prob2) * (1/prob3)
        # Append the parlay row
        parlay_data.append({
            'parlay': parlay_num,
            'date1': date1, 'date2': date2, 'date3': date3,
            'flag1': flag1, 'flag2': flag2, 'flag3': flag3,
            'winner1': winner1, 'winner2': winner2, 'winner3': winner3,
            'loser1': loser1, 'loser2': loser2, 'loser3': loser3,
            'potential_win': potential_win            
        })
        matches=parlay_data
    return render_template("table_invest.html", title=title, matches=matches)

@app.route('/sitemap.xml')
def static_from_root():
    return send_from_directory(app.static_folder, request.path[1:])

@app.route('/details')
def show_details():
    pass

# @app.route('/contact_submit',methods=['POST'])
# def contact_submit():
#     if request.method == 'POST':
#         name = request.form['name']
#         email = request.form['email']
#         message = request.form['message']

#         # Set up your email server and credentials
#         smtp_server = "smtp.gmail.com"
#         smtp_port = 465
#         sender_email = "ignaciomedinar@gmail.com"
#         sender_password = ""

#         subject = f"New contact form submission from {name}"
#         body = f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}"

#         try:
#             # Connect to the SMTP server and send the email
#             with smtplib.SMTP(smtp_server, smtp_port) as server:
#                 server.starttls()
#                 server.login(sender_email, sender_password)
#                 server.sendmail(sender_email, sender_email, f'Subject: {subject}\n\n{body}')

#             # Return a success message
#             return "Message sent successfully!"
#         except Exception as e:
#             return f"An error occurred: {str(e)}"
#     return render_template("comments.html")


if __name__ == "__main__":
    app.run(debug=True)  #, port=5000
