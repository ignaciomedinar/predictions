from flask import Flask, render_template, request
import mysql.connector
import datetime

app = Flask(__name__)

@app.route('/')
def home():
    title = 'Home'
    message='Goal Genius is a space where you can find football matches from the most important Leagues \
        with Dates, Results and Predictions based on goals scored and goals received.'
    return render_template('base.html', title=title, message=message)

@app.route('/calendar')
def show_matches():
    title = 'Calendar'
    cnx = mysql.connector.connect(user='root', password='milanesa',
                                  host='localhost', database='football')
    cursor = cnx.cursor()
    current_week_start = datetime.datetime.now().date() - datetime.timedelta(days=datetime.datetime.now().weekday())
    current_week_end = current_week_start + datetime.timedelta(days=6)

    # Query the database for the results for the current week
    query = ("SELECT * "
                "FROM football_results "
                "WHERE date >= %s AND date <= %s "
                "ORDER BY date asc, League"
                )
    cursor.execute(query, (current_week_start, current_week_end))
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
    cnx = mysql.connector.connect(user='root', password='milanesa',
                                  host='localhost', database='football')
    cursor = cnx.cursor()
    previous_week_start = (datetime.datetime.now().date() - datetime.timedelta(days=datetime.datetime.now().weekday())) - datetime.timedelta(days=7)
    current_week_end = previous_week_start + datetime.timedelta(days=13)

    # Query the database for the results for the current week
    query = ("SELECT fr.*, ph.bet, case when ph.bet is null "
                "then 'No Contest' when upper(fr.Result)=upper(left(ph.bet,1)) "
                "then 'Correct' else 'Incorrect' end as success "
                "FROM football.football_results fr "
                "left join football.predictions_history ph "
                "on fr.date = ph.date and fr.local=ph.local and fr.visitor=ph.visitor "
                "WHERE fr.date >= %s AND fr.date <= %s AND fr.Result in ('l','v','t') "
                "ORDER BY fr.date desc, fr.League"
                )
    cursor.execute(query, (previous_week_start, current_week_end))
    # Get the column names
    columns = [col[0] for col in cursor.description]

    # Fetch all rows and convert to list of dictionaries
    results = [dict(zip(columns, row)) for row in cursor.fetchall()]

    # Close the database connection
    cursor.close()
    cnx.close()

    # Pass the results and weeks to the HTML template
    return render_template("table_results.html", title=title, results=results)

@app.route('/predictions')
def show_predictions():
    title = 'Predictions'
    cnx = mysql.connector.connect(user='root', password='milanesa',
                                  host='localhost', database='football')
    cursor = cnx.cursor()
    previous_week_start = (datetime.datetime.now().date() - datetime.timedelta(days=datetime.datetime.now().weekday())) - datetime.timedelta(days=7)
    current_week_end = previous_week_start + datetime.timedelta(days=13)

    # Query the database for the results for the current week
    query = ("SELECT pr.*, r.result "
                "FROM football.predictions pr "
                "left join football.football_results r "
                "on pr.date = r.date and pr.local=r.local and pr.visitor=r.visitor "
                "WHERE pr.date >= %s AND pr.date <= %s "
                "ORDER BY pr.max_prob desc"
                )
    cursor.execute(query, (previous_week_start, current_week_end))
    # Get the column names
    columns = [col[0] for col in cursor.description]

    # Fetch all rows and convert to list of dictionaries
    predictions = [dict(zip(columns, row)) for row in cursor.fetchall()]

    # Close the database connection
    cursor.close()
    cnx.close()

    # Pass the results and weeks to the HTML template
    return render_template("table_predictions.html", title=title, predictions=predictions)

@app.route('/invest', methods=['GET', 'POST'])
def show_invest():
    title = 'Investing'
    predictions=''
    if request.method == 'POST':
        amount = request.form['amount']
        num_matches = int(request.form['num_matches'])
        if amount != '':
            inputs=(amount, num_matches)
            current_week_start = datetime.datetime.now().date() - datetime.timedelta(days=datetime.datetime.now().weekday())
            current_week_end = current_week_start + datetime.timedelta(days=6)
            cnx = mysql.connector.connect(user='root', password='milanesa',
                                        host='localhost', database='football')
            cursor = cnx.cursor()

    # Query the database for the results for the current week
            query = ("SELECT pr.*, r.result "
                        "FROM football.predictions pr "
                        "left join football.football_results r "
                        "on pr.date = r.date and pr.local=r.local and pr.visitor=r.visitor "
                        "WHERE pr.date >= %s AND pr.date <= %s "
                        "ORDER BY pr.max_prob desc "
                        "limit %s "
                        )
            cursor.execute(query, (current_week_start, current_week_end, num_matches))

            # Get the column names
            columns = [col[0] for col in cursor.description]
            # Fetch all rows and convert to list of dictionaries
            predictions = [dict(zip(columns, row)) for row in cursor.fetchall()]
            probs = 0
            for row in predictions:
                probs += row['max_prob']
            ratio=int(amount)/probs
            for row in predictions:
                row['bet_amount'] = row['max_prob'] * ratio
            print(probs)
            print(ratio)
            print(predictions)

            # Close the database connection
            cursor.close()
            cnx.close()

        else:
            predictions=''
    return render_template("invest.html", title=title, predictions=predictions,inputs=inputs)

# @app.route("/")
# def show_results():
#     # Connect to the MySQL database
#     cnx = mysql.connector.connect(user='root', password='milanesa',
#                                   host='localhost', database='football')
#     cursor = cnx.cursor()

#     # Get all the weeks from the database
#     query = ("SELECT DISTINCT Week "
#              "FROM football_results "
#              "ORDER BY Week ASC"
#              )
#     cursor.execute(query)
#     weeks = [week[0] for week in cursor.fetchall()]

#     # Get all the teams from the database
#     query = ("SELECT DISTINCT Local "
#              "FROM football.football_results "
#              "ORDER BY Local ASC"
#              )
#     cursor.execute(query)
#     teams = [team[0] for team in cursor.fetchall()]

#     # Get the selected week from the request arguments
#     selected_week = request.args.get('week')
#     if selected_week:
#         # Query the database for the results for the selected week
#         query = ("SELECT * "
#                  "FROM football_results "
#                  "WHERE Week = %s AND Result in ('l','v','t') "
#                  "ORDER BY date DESC, League"
#                  )
#         cursor.execute(query, (selected_week,))
#         week_no = f"Week {selected_week.strftime('%U')}"
       
#     else:
#         # Get the current week's start and end date
#         # Assuming you have a date column named "date" in your football_results table
#         current_week_start = datetime.datetime.now().date() - datetime.timedelta(days=datetime.datetime.now().weekday())
#         current_week_end = current_week_start + datetime.timedelta(days=6)

#         # Query the database for the results for the current week
#         query = ("SELECT * "
#                  "FROM football_results "
#                  "WHERE date >= %s AND date <= %s AND Result in ('l','v','t')"
#                  "ORDER BY date DESC, League"
#                  )
#         cursor.execute(query, (current_week_start, current_week_end))
#         # Set the current week variable
#         week_no = f"Week {current_week_start.strftime('%U')}"
        
#     # Get the column names
#     columns = [col[0] for col in cursor.description]

#     # Fetch all rows and convert to list of dictionaries
#     results = [dict(zip(columns, row)) for row in cursor.fetchall()]
#     print(cursor)

#     # Close the database connection
#     cursor.close()
#     cnx.close()

#     # Pass the results and weeks to the HTML template
#     return render_template("tablas.html", results=results, weeks=weeks, selected_week=selected_week, week_no=week_no, teams=teams)

# @app.route('/matches')
# def matches():
#     # Get the selected week from the dropdown menu
#     current_week_start = datetime.datetime.now().date() - datetime.timedelta(days=datetime.datetime.now().weekday())
    
#     cnx = mysql.connector.connect(user='root', password='milanesa',
#                                   host='localhost', database='football')
#     cursor = cnx.cursor()
#     query = ("SELECT DISTINCT Week "
#              "FROM football_results "
#              "ORDER BY Week ASC"
#              )
#     cursor.execute(query)
#     weeks = [week[0] for week in cursor.fetchall()]
#     week = request.args.get('week',default=current_week_start)
    
#     # Query the database for the matches for the selected week
#     query = ("SELECT * "
#              "FROM football_results "
#              "WHERE Week = %s AND Result in ('l','v','t')"
#              "ORDER BY date DESC, League"
#              )
#     cursor.execute(query, (week,))
#     # Get the column names
#     columns = [col[0] for col in cursor.description]

#     # Fetch all rows and convert to list of dictionaries
#     results = [dict(zip(columns, row)) for row in cursor.fetchall()]
#     # matches = Match.query.filter_by(week=week).all()

#     # Close the database connection
#     cursor.close()
#     cnx.close()

#     # Pass the matches and weeks to the HTML template
#     return render_template('index.html', results=results, week=week, weeks=weeks)

# @app.route('/teams')
# def teams():
     
#     cnx = mysql.connector.connect(user='root', password='milanesa',
#                                   host='localhost', database='football')
#     cursor = cnx.cursor()
#     query = ("SELECT DISTINCT Local "
#              "FROM football_results "
#              "ORDER BY Local ASC"
#              )
#     cursor.execute(query)
#     teams = [team[0] for team in cursor.fetchall()]
#     team = request.args.get('team',default='Arsenal')
    
#     # Query the database for the matches for the selected week
#     query = ("SELECT * "
#              "FROM football_results "
#              "WHERE Local = %s or Visitor = %s "
#              "ORDER BY date asc"
#              )
#     cursor.execute(query, (team,team,))
#     selected_team=team
#     # Get the column names
#     columns = [col[0] for col in cursor.description]
#     # Fetch all rows and convert to list of dictionaries
#     results = [dict(zip(columns, row)) for row in cursor.fetchall()]
#     # matches = Match.query.filter_by(week=week).all()

#     # Close the database connection
#     cursor.close()
#     cnx.close()

# @app.route('/predictions')
# def teams():
     
#     cnx = mysql.connector.connect(user='root', password='milanesa',
#                                   host='localhost', database='football')
#     cursor = cnx.cursor()
#     query = ("SELECT DISTINCT Local "
#              "FROM football_results "
#              "ORDER BY Local ASC"
#              )
#     cursor.execute(query)
#     teams = [team[0] for team in cursor.fetchall()]
#     team = request.args.get('team',default='Arsenal')
    
#     # Query the database for the matches for the selected week
#     query = ("SELECT * "
#              "FROM football_results "
#              "WHERE Local = %s or Visitor = %s "
#              "ORDER BY date asc"
#              )
#     cursor.execute(query, (team,team,))
#     selected_team=team
#     # Get the column names
#     columns = [col[0] for col in cursor.description]
#     # Fetch all rows and convert to list of dictionaries
#     results = [dict(zip(columns, row)) for row in cursor.fetchall()]
#     # matches = Match.query.filter_by(week=week).all()

#     # Close the database connection
#     cursor.close()
#     cnx.close()

#     # Pass the matches and weeks to the HTML template
#     return render_template('index.html', results=results, teams=teams, selected_team=selected_team)


if __name__ == "__main__":
    app.run(debug=True)
