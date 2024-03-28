from flask import Flask, render_template, request, send_from_directory, redirect
import mysql.connector
import datetime
from dateutil.relativedelta import relativedelta
import calendar
import smtplib

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
    title = 'Welcome'
    message='Goal Genius is a platform that offers football result predictions on football matches from \
        the most significant Leagues. It also provides Dates, Results, and the Matches that will \
        take place in the next 4 months.<br><br> \
        The predictions are based \
        on a statistic model considering goals scored and goals received by teams in the last two years.'
    return render_template('base.html', title=title, message=message)

@app.route('/calendar')
def show_matches():
    title = 'Next Matches'
    # cnx = mysql.connector.connect(user='root', password='milanesa',
                                #   host='localhost', database='football')
     ## heroku db
    cnx = mysql.connector.connect(
    host='eu-cluster-west-01.k8s.cleardb.net',
    database='heroku_9f69e70d94a5650',
    user='b902878f5a41b4',
    password='4acedb6a',
    port='3306'
    )
    cursor = cnx.cursor()
    current_week_start = datetime.datetime.now().date() - datetime.timedelta(days=datetime.datetime.now().weekday())
    current_week_end = current_week_start + datetime.timedelta(days=6)
    six_months = datetime.date.today() + relativedelta(months=+4)

    # Query the database for the results for the current week
    query = ("SELECT fr.*, fl.flag_url "
                "FROM football_results fr "
                "left join heroku_9f69e70d94a5650.flags fl "
                "on upper(fl.Country) = upper(fr.League) "
                "WHERE date >= %s "
                "AND date <= %s "
                "AND goalslocal ='' "
                "ORDER BY date asc, League"
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
    # cnx = mysql.connector.connect(user='root', password='milanesa',
    #                               host='localhost', database='football')
     ## heroku db
    #mysql://b902878f5a41b4:4acedb6a@eu-cluster-west-01.k8s.cleardb.net/heroku_9f69e70d94a5650
    cnx = mysql.connector.connect(
    host='eu-cluster-west-01.k8s.cleardb.net',
    database='heroku_9f69e70d94a5650',
    user='b902878f5a41b4',
    password='4acedb6a',
    port='3306'
    )
    cursor = cnx.cursor()
    previous_week_start = (datetime.datetime.now().date() - datetime.timedelta(days=datetime.datetime.now().weekday())) - datetime.timedelta(days=7)
    current_week_end = previous_week_start + datetime.timedelta(days=13)
    current_week=datetime.date.today().isocalendar()[1]
    current_year=datetime.date.today().year

    # Get all the weeks from the database
    query = ("SELECT DISTINCT concat(Year,'-W',lpad(Week,2,0)) "
                "FROM heroku_9f69e70d94a5650.football_results "
                "WHERE concat(year,week)<=%s%s "
                "ORDER by concat(Year,'-W',lpad(week,2,0)) DESC"
                )
    cursor.execute(query, (current_year,current_week,))
    weeks = [week[0] for week in cursor.fetchall()]
    first_dates_week=[datetime.datetime.strptime(week + '-1', "%Y-W%W-%w") for week in weeks]
    last_dates_week=[first + datetime.timedelta(days=6) for first in first_dates_week]

    selected_week_start = request.args.get('week')

    # Get all the teams from the database
    query = ("SELECT DISTINCT Local "
                "FROM heroku_9f69e70d94a5650.football_results "
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
                    "ph.phg, ph.pag, ph.max_prob "
                    "FROM heroku_9f69e70d94a5650.football_results fr "
                    "left join heroku_9f69e70d94a5650.predictions_history ph "
                    "on fr.date = ph.date and fr.local=ph.local and fr.visitor=ph.visitor "
                    "left join heroku_9f69e70d94a5650.flags fl "
                    "on upper(fl.Country) = upper(fr.League) "
                    "WHERE fr.date >= %s AND fr.date <= %s "
                    "AND fr.goalslocal <>'' "
                    "ORDER BY fr.date desc, fr.League"
                    )
        cursor.execute(query, (selected_week_start, selected_week_end))
        # print("selección: " + selected_week_start)
    else:
        # Query the database for the results for the current week
        query = ("SELECT distinct fr.*, ph.bet, case when ph.bet is null or fr.goalslocal ='' "
                    "then 'NA' when upper(fr.Result)=upper(left(ph.bet,1)) "
                    "then 'Correct' else 'Incorrect' end as success, fl.flag_url, "
                    "ph.phg, ph.pag, ph.max_prob "
                    "FROM heroku_9f69e70d94a5650.football_results fr "
                    "left join heroku_9f69e70d94a5650.predictions_history ph "
                    "on fr.date = ph.date and fr.local=ph.local and fr.visitor=ph.visitor "
                    "left join heroku_9f69e70d94a5650.flags fl "
                    "on upper(fl.Country) = upper(fr.League) "
                    "WHERE fr.date >= %s AND fr.date <= %s "
                    "AND fr.goalslocal <>'' "
                    "ORDER BY fr.date desc, fr.League"
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
    # cnx = mysql.connector.connect(user='root', password='milanesa',
    #                               host='localhost', database='football')
     ## heroku db
    cnx = mysql.connector.connect(
    host='eu-cluster-west-01.k8s.cleardb.net',
    database='heroku_9f69e70d94a5650',
    user='b902878f5a41b4',
    password='4acedb6a',
    port='3306'
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
    query = ("SELECT distinct pr.*, r.result, r.goalslocal, r.goalsvisitor, fl.flag_url "
                "FROM heroku_9f69e70d94a5650.predictions pr "
                "left join heroku_9f69e70d94a5650.football_results r "
                "on pr.date = r.date and pr.local=r.local and pr.visitor=r.visitor "
                "left join heroku_9f69e70d94a5650.flags fl "
                "on upper(fl.Country) = upper(pr.League) "
                "WHERE pr.date >= %s AND pr.date <= %s "
                "ORDER BY pr.max_prob desc"
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

@app.route('/invest', methods=['GET', 'POST'])
def show_invest():
    title = 'Investing'
    selected_leagues =()
    # cnx = mysql.connector.connect(user='root', password='milanesa',
    #                               host='localhost', database='football')
     ## heroku db
    cnx = mysql.connector.connect(
    host='eu-cluster-west-01.k8s.cleardb.net',
    database='heroku_9f69e70d94a5650',
    user='b902878f5a41b4',
    password='4acedb6a',
    port='3306'
    )
    cursor = cnx.cursor()
    current_week_start = datetime.datetime.now().date() - datetime.timedelta(days=datetime.datetime.now().weekday())
    current_week_end = current_week_start + datetime.timedelta(days=6)

    # Query the database for the results for the current week
    query = ("SELECT distinct League "
                "FROM heroku_9f69e70d94a5650.predictions "
                "WHERE date >= %s "
                "ORDER BY League"
                )
    cursor.execute(query, (current_week_start, ))
    # Get the column names
    
    leagues = [league[0] for league in cursor.fetchall()]

    inputs=()
    predictions=''
    if request.method == 'POST':
        amount = request.form['amount']
        try:
            num_matches = int(request.form['num_matches'])
        except: 
            num_matches = 10
 
        selected_leagues = request.form.getlist('leagues[]')
        if len(selected_leagues):
            pass
        else:
            selected_leagues = leagues
        selected_leagues_str = ",".join(["'" + league + "'" for league in selected_leagues])
        if amount != '' and num_matches!='':
            inputs=(amount, num_matches)
            current_week_start = datetime.datetime.now().date() - datetime.timedelta(days=datetime.datetime.now().weekday())
            current_week_end = current_week_start + datetime.timedelta(days=6)
            # cnx = mysql.connector.connect(user='root', password='milanesa',
            #                             host='localhost', database='football')
            ## heroku db
            cnx = mysql.connector.connect(
            host='eu-cluster-west-01.k8s.cleardb.net',
            database='heroku_9f69e70d94a5650',
            user='b902878f5a41b4',
            password='4acedb6a',
            port='3306'
            )
            cursor = cnx.cursor()

    # Query the database for the results for the current week
            query = ("SELECT distinct pr.*, r.result, fl.flag_url "
                        "FROM heroku_9f69e70d94a5650.predictions pr "
                        "left join heroku_9f69e70d94a5650.football_results r "
                        "on pr.date = r.date and pr.local=r.local and pr.visitor=r.visitor "
                        "left join heroku_9f69e70d94a5650.flags fl "
                        "on upper(fl.Country) = upper(pr.League) "
                        "WHERE pr.date >= %s AND pr.date <= %s "
                        f"AND pr.league in ({selected_leagues_str}) "
                        "ORDER BY pr.max_prob desc "
                        "limit %s"
                        )
            cursor.execute(query, (current_week_start, current_week_end, num_matches))

            # Get the column names
            columns = [col[0] for col in cursor.description]
            # Fetch all rows and convert to list of dictionaries
            predictions = [dict(zip(columns, row)) for row in cursor.fetchall()]
            probs = 0
            for row in predictions:
                probs += row['max_prob']
            ratio=float(amount)/probs
            for row in predictions:
                row['bet_amount'] = row['max_prob'] * ratio

            # Close the database connection
            cursor.close()
            cnx.close()

        else:
            predictions=''
    return render_template("invest.html", title=title, predictions=predictions,inputs=inputs,leagues=leagues,selected_leagues=selected_leagues)

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
