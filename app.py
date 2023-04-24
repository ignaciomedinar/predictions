from flask import Flask, render_template, request
import mysql.connector
import datetime

app = Flask(__name__)

@app.route("/")
def show_results():
    # Connect to the MySQL database
    cnx = mysql.connector.connect(user='root', password='milanesa',
                                  host='localhost', database='football')
    cursor = cnx.cursor()

    # Get all the weeks from the database
    query = ("SELECT DISTINCT Week "
             "FROM football_results "
             "ORDER BY Week ASC"
             )
    cursor.execute(query)
    weeks = [week[0] for week in cursor.fetchall()]

    # Get all the weeks from the database
    query = ("SELECT DISTINCT Local "
             "FROM football.football_results "
             "ORDER BY Local ASC"
             )
    cursor.execute(query)
    teams = [team[0] for team in cursor.fetchall()]

    # Get the selected week from the request arguments
    selected_week = request.args.get('week')
    if selected_week:
        # Query the database for the results for the selected week
        query = ("SELECT * "
                 "FROM football_results "
                 "WHERE Week = %s AND Result in ('l','v','t') "
                 "ORDER BY date DESC, League"
                 )
        cursor.execute(query, (selected_week,))
        week_no = f"Week {selected_week.strftime('%U')}"
       
    else:
        # Get the current week's start and end date
        # Assuming you have a date column named "date" in your football_results table
        current_week_start = datetime.datetime.now().date() - datetime.timedelta(days=datetime.datetime.now().weekday())
        current_week_end = current_week_start + datetime.timedelta(days=6)

        # Query the database for the results for the current week
        query = ("SELECT * "
                 "FROM football_results "
                 "WHERE date >= %s AND date <= %s AND Result in ('l','v','t')"
                 "ORDER BY date DESC, League"
                 )
        cursor.execute(query, (current_week_start, current_week_end))
        # Set the current week variable
        week_no = f"Week {current_week_start.strftime('%U')}"
        
    # Get the column names
    columns = [col[0] for col in cursor.description]

    # Fetch all rows and convert to list of dictionaries
    results = [dict(zip(columns, row)) for row in cursor.fetchall()]

    # Close the database connection
    cursor.close()
    cnx.close()

    # Pass the results and weeks to the HTML template
    return render_template("index.html", results=results, weeks=weeks, selected_week=selected_week, week_no=week_no, teams=teams)

@app.route('/matches')
def matches():
    # Get the selected week from the dropdown menu
    current_week_start = datetime.datetime.now().date() - datetime.timedelta(days=datetime.datetime.now().weekday())
    
    cnx = mysql.connector.connect(user='root', password='milanesa',
                                  host='localhost', database='football')
    cursor = cnx.cursor()
    query = ("SELECT DISTINCT Week "
             "FROM football_results "
             "ORDER BY Week ASC"
             )
    cursor.execute(query)
    weeks = [week[0] for week in cursor.fetchall()]
    week = request.args.get('week',default=current_week_start)
    
    # Query the database for the matches for the selected week
    query = ("SELECT * "
             "FROM football_results "
             "WHERE Week = %s AND Result in ('l','v','t')"
             "ORDER BY date DESC, League"
             )
    cursor.execute(query, (week,))
    # Get the column names
    columns = [col[0] for col in cursor.description]

    # Fetch all rows and convert to list of dictionaries
    results = [dict(zip(columns, row)) for row in cursor.fetchall()]
    # matches = Match.query.filter_by(week=week).all()

    # Close the database connection
    cursor.close()
    cnx.close()

    # Pass the matches and weeks to the HTML template
    return render_template('index.html', results=results, week=week, weeks=weeks)

@app.route('/teams')
def teams():
     
    cnx = mysql.connector.connect(user='root', password='milanesa',
                                  host='localhost', database='football')
    cursor = cnx.cursor()
    query = ("SELECT DISTINCT Local "
             "FROM football_results "
             "ORDER BY Local ASC"
             )
    cursor.execute(query)
    teams = [team[0] for team in cursor.fetchall()]
    team = request.args.get('team',default='Arsenal')
    
    # Query the database for the matches for the selected week
    query = ("SELECT * "
             "FROM football_results "
             "WHERE Local = %s or Visitor = %s "
             "ORDER BY date asc"
             )
    cursor.execute(query, (team,team,))
    selected_team=team
    # Get the column names
    columns = [col[0] for col in cursor.description]
    # Fetch all rows and convert to list of dictionaries
    results = [dict(zip(columns, row)) for row in cursor.fetchall()]
    # matches = Match.query.filter_by(week=week).all()

    # Close the database connection
    cursor.close()
    cnx.close()

    # Pass the matches and weeks to the HTML template
    return render_template('index.html', results=results, teams=teams, selected_team=selected_team)


if __name__ == "__main__":
    app.run(debug=True)
