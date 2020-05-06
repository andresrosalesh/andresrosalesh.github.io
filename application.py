import os
import datetime
import math

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import login_required, bin_to_days_of_week, update_nw_values

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# # Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# # Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///deepwork.db")

@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    """
    Home Page where user can log timed tasks.
    """
    # If user logged time
    if request.method == "POST":
        # JSON data format[hours, minutes, seconds, startTime, startDate, stopTime, stopDate, taskDescription, deepworkBool]
        data = request.get_json()

        # Ensure user has recorded time
        if not data['startTime']:
            flash("You must log time to submit a time tracking.")
            return jsonify(dict(redirect='/'))

        # Ensure user has recorded task
        if not data['task']:
            flash("You must enter a task description.")
            return jsonify(dict(redirect='/'))

        # Ensure user has not selected both deep and shallow work buttons
        if data['deepworkBool'] == 2:
            flash("Work cannot be both deep and shallow. Choose one!")
            return jsonify(dict(redirect='/'))

        # Ensure user has selected at least one of the deep and shallow work buttons
        if data['deepworkBool'] == 3:
            flash("You must select either deep or shallow work. Choose one!")
            return jsonify(dict(redirect='/'))

        user_info = db.execute("SELECT * FROM users WHERE id = :id", id=session["user_id"])[0]

        # Deny entry if logged on a non-working day
        weekday_mapping = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        working_days =  bin_to_days_of_week(user_info['days'])
        today = datetime.date.today()
        if weekday_mapping[today.weekday()] not in working_days:
            flash("This is not a working day. Please rest and recuperate!")
            return jsonify(dict(redirect='/'))

        # Convert times and dates to strings, append zero if single digits
        start_time = "".join([(str(i)+":") if i >= 10 else ("0"+str(i)+":") for i in data['startTime']])
        start_date = "".join([str(i) if i >= 10 else "0"+str(i) for i in data['startDate']])
        stop_time = "".join([(str(i)+":") if i >= 10 else "0"+("0"+str(i)+":") for i in data['stopTime']])
        stop_date = "".join([str(i) if i >= 10 else "0"+str(i) for i in data['stopDate']])
        dw = 1 if data['deepworkBool'] == 1 else 0

        # Chop colons off end of time records
        if start_time[len(start_time) - 1] == ":":
            start_time = start_time[:(len(start_time) - 1)]
        if stop_time[len(stop_time) - 1] == ":":
            stop_time = stop_time[:(len(stop_time) - 1)]

        # Update log number for user
        last_log = db.execute("SELECT log FROM timings WHERE user_id = :id ORDER BY log DESC LIMIT 1", id=user_info['id'])
        if (last_log):
            log_num = last_log[0]['log'] + 1
        else:
            log_num = 1

        # Insert timing information into database
        db.execute("INSERT INTO timings (user_id, log, hours, minutes, seconds, start_time, start_date, stop_time, stop_date, task, dw) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                  user_info['id'], log_num, data['hours'], data['minutes'], data['seconds'], start_time, start_date, stop_time, stop_date, data['task'], dw)

        # Trigger "success" message to user
        flash("Timing submitted!")
        return jsonify(dict(redirect='/'))
    else:

        return render_template("index.html")

@app.route("/trends", methods=["GET", "POST"])
@login_required
def trends():
    '''
    Analytics page which displays trends in user's deep work and productivity over time.
    '''

    # Get user info and today's date
    user_info = db.execute("SELECT * FROM users WHERE id = :id", id=session["user_id"])[0]
    today = datetime.date.today()

    # Default is weekly timing data
    type_of_trend = "week"
    timespan = 8

    # A post would mean the user selected the month view
    if request.method == "POST":
        # If user requested a monthly view, return monthly timing data
        if request.form.get("wkmth") == "month":
            # Update type_of_trend to display correct graph
            type_of_trend = "month"
            timespan = 35

    # Get user timings
    timedelay = str(today - datetime.timedelta(days=timespan)).replace("-", "")
    timings = db.execute("SELECT * FROM timings WHERE user_id = :id AND start_date >= :date", id=user_info['id'], date=timedelay)

    # Update no work values if necessary
    update_nw_values(user_info)

    # Grab remaining no work work
    shallow = db.execute("SELECT * FROM shwork WHERE user_id = :id AND date >= :date", id=user_info['id'], date=timedelay)

    # Grab well-being data
    wbdata = db.execute("SELECT * FROM wbeing WHERE user_id = :id AND date >= :date", id=user_info['id'], date=timedelay)

    # Grab all records
    all_timings = db.execute("SELECT * FROM timings WHERE user_id = :id", id=user_info['id'])
    all_shallow = db.execute("SELECT * FROM shwork WHERE user_id = :id", id=user_info['id'])
    all_wbdata = db.execute("SELECT * FROM wbeing WHERE user_id = :id", id=user_info['id'])

    return render_template("trends.html", timings=timings, shallow=shallow, type_of_trend=type_of_trend, wbdata=wbdata, all_timings=all_timings, all_shallow=all_shallow, all_wbdata=all_wbdata)

@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    # Get user information
    user_info = db.execute("SELECT * FROM users WHERE id = :id", id=session["user_id"])[0]

    # If user requested to update profile
    if request.method == "POST":
        # Ensure working hours are provided
        if not request.form.get("hours"):
            flash("You must enter a number from 0 to 24 for hours.")
            return render_template("profile.html", name=user_info['name'])

        # Ensure working minutes are provided
        if not request.form.get("minutes"):
            flash("You must enter a number from 0 to 60 for minutes.")
            return render_template("profile.html", name=user_info['name'])

        # Update user's preferred days of the week as binary 1's and 0's
        days = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
        _valid_days = []
        for i in range(7):
            # If user selected days[i], such as 'mon'
            if request.form.get(days[i]):
                # Record the day as a binary 1
                _valid_days.append("1")
            else:
                # Otherwise if user didn't select day, record as binary 0
                _valid_days.append("0")
        valid_days = "".join(_valid_days) # Turn list of valid days into string

        # Ensure user has selected at least 1 day
        if "1" not in valid_days:
            flash("You must choose at least one working day.")
            return render_template("profile.html", name=user_info['name'])

        # Update user's working hours and preferred days
        db.execute("UPDATE users SET hours = ?, minutes = ?, days = ? WHERE id = ?", request.form.get("hours"), request.form.get("minutes"), valid_days, user_info['id'])

        flash("Profiled updated!")
        return redirect("/profile")
    else:
        # Return information about user's current working preferences
        days = bin_to_days_of_week(user_info['days'])
        return render_template("profile.html", hours=user_info['hours'], minutes=user_info['minutes'], days=days, name=user_info['name'])

@app.route("/shutdown", methods=["GET", "POST"])
@login_required
def shutdown():
    if request.method == "POST":

        # TODO: Ensure user cannot submit more than shutdown form in a day

        # Ensure user submitted hours for sleep
        if not request.form.get("sleeph"):
            flash("You must enter a number from 0 to 24 for hours of sleep.")
            return render_template("shutdown.html")
        sleeph = request.form.get("sleeph")

        # Ensure user submitted minutes for sleep
        if not request.form.get("sleepm"):
            flash("You must enter a number from 0 to 60 for minutes of sleep.")
            return render_template("shutdown.html")
        sleepm = request.form.get("sleepm")

        # Ensure user submitted quality of sleep
        if not request.form.get("sleepq"):
            flash("You must enter a number from 1 to 10 for quality of sleep.")
            return render_template("shutdown.html")
        sleepq = request.form.get("sleepq")

        # Ensure user submitted mood rating
        if not request.form.get("mood"):
            flash("You must enter a number from 1 to 10 for mood.")
            return render_template("shutdown.html")
        mood = request.form.get("mood")

        # Ensure user submitted energy level
        if not request.form.get("energy"):
            flash("You must enter a number from 1 to 10 for energy levels.")
            return render_template("shutdown.html")
        energy = request.form.get("energy")

        # Ensure user has responded to their satisfaction with their productivity and has not selected both yes and no
        if (request.form.getlist('happy') == [] and request.form.getlist('nothappy') == []) or (request.form.getlist('happy') == ['on'] and request.form.getlist('nothappy') == ['on']):
            flash("You must select either Yes or No for Question 5.")
            return render_template("shutdown.html")

        if (request.form.getlist('happy') == ['on']):
            prod = 1
        else:
            prod = 0

        # Ensure user has submitted some journal entry
        if not request.form.get("journal"):
            flash("You must submit a journal entry.")
            return render_template("shutdown.html")
        journal = request.form.get("journal")

        user_info = db.execute("SELECT * FROM users WHERE id = :id", id=session["user_id"])[0]
        db.execute("INSERT INTO wbeing (user_id, date, sleepq, sleeph, sleepm, mood, energy, prod, journal) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)",
                  user_info['id'], datetime.date.today().strftime('%Y%m%d'), sleepq, sleeph, sleepm, mood, energy, prod, journal)

        return redirect("/complete")

    return render_template("shutdown.html")

@app.route("/complete", methods=["GET", "POST"])
@login_required
def complete():
    # Get user information
    user_info = db.execute("SELECT * FROM users WHERE id = :id", id=session["user_id"])[0]

    timings = db.execute("SELECT * FROM timings WHERE user_id = :id AND start_date = :date ORDER BY log DESC", id=user_info['id'], date=datetime.date.today().strftime('%Y%m%d'))
    hours = 0
    minutes = 0
    if timings:
        for entry in timings:
            hours += entry['hours']
            minutes += entry['minutes']
            minutes += entry['seconds'] / 60
        minutes = math.ceil(minutes)

    return render_template("complete.html", hours=hours, minutes=minutes)

@app.route("/logs")
@login_required
def logs():
    # Get user information
    user_info = db.execute("SELECT * FROM users WHERE id = :id", id=session["user_id"])[0]

    # Get timing and well being records
    timings = db.execute("SELECT * FROM timings WHERE user_id = :id ORDER BY log DESC", id=user_info['id'])
    wbdata = db.execute("SELECT * FROM wbeing WHERE user_id = :id ORDER BY date DESC", id=user_info['id'])

    weekday_mapping = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

    # Organize timings into table format on page logs.html
    timings_list = []
    for entry in timings:
        _date = datetime.datetime.strptime(entry['start_date'], '%Y%m%d')
        date = weekday_mapping[_date.weekday()] + ", " + _date.strftime('%B %d, %Y')

        duration = str(entry['hours']) + "h" + str(entry['minutes']) + "m" + str(entry['seconds']) + "s"

        if int(entry['start_time'][:2]) >= 13:
            start_time = str(int(entry['start_time'][:2]) - 12) + entry['start_time'][2:] + " p.m."
        else:
            start_time = entry['start_time'] + " a.m."

        if int(entry['stop_time'][:2]) >= 13:
            stop_time = str(int(entry['stop_time'][:2]) - 12) + entry['stop_time'][2:] + " p.m."
        else:
            stop_time = entry['stop_time'] + " a.m."
        span = start_time + " - " + stop_time

        if entry['dw'] == 1:
            dw = "Yes"
        else:
            dw = "No"

        timings_list.append([date, duration, span, dw, entry['task']])

    # Organize well being data into table format on page logs.html
    wbdata_list = []
    for entry in wbdata:
        _date = datetime.datetime.strptime(entry['date'], '%Y%m%d')
        date = weekday_mapping[_date.weekday()] + ", " + _date.strftime('%B %d, %Y')

        sleep = str(entry['sleepq']) + "/10, " + str(entry['sleeph']) + "h" + str(entry['sleepm']) + "m"
        mood = str(entry['mood']) + "/10"
        energy = str(entry['energy']) + "/10"

        if entry['prod'] == 1:
            prod = "Yes"
        else:
            prod = "No"

        wbdata_list.append([date, sleep, mood, energy, prod, entry['journal']])

    return render_template("logs.html", timings_list=timings_list, wbdata_list=wbdata_list)

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            flash("You must enter a username.")
            return render_template("login.html")

        # Ensure password was submitted
        if not request.form.get("password"):
            flash("You must enter a password.")
            return render_template("login.html")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            flash("The username or password you entered is incorrect.")
            return render_template("login.html")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/login")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    if request.method == "POST":

        # Ensure all fields are submitted properly

        if not request.form.get("fullname"):
            flash("You must enter your name.")
            return render_template("register.html")

        # Ensure username was submitted and username doesn't exist
        if not request.form.get("username"):
            flash("You must enter a username.")
            return render_template("register.html")

        prevuser = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))
        if prevuser:
            if request.form.get("username") == prevuser[0]['username']:
                flash("Username is taken.")
                return render_template("register.html")

        # Ensure password was submitted
        if not request.form.get("password"):
            flash("You must enter a password.")
            return render_template("register.html")

        # Ensure password confirmation was submitted
        if not request.form.get("confirmation"):
            flash("You must confirm your password.")
            return render_template("register.html")

        # Ensure password matches password confirmation
        if request.form.get("confirmation") != request.form.get("password"):
            flash("Your passwords do not match.")
            return render_template("register.html")

        # Ensure working hours are provided
        if not request.form.get("hours"):
            flash("You must enter a number from 0 to 24 for hours.")
            return render_template("register.html")

        # Ensure working minutes are provided
        if not request.form.get("minutes"):
            flash("You must enter a number from 0 to 60 for minutes.")
            return render_template("register.html")

        # Record user's preferred days of the week as binary 1's and 0's
        days = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
        _valid_days = []
        for i in range(7):
            if request.form.get(days[i]):
                _valid_days.append("1")
            else:
                _valid_days.append("0")
        valid_days = "".join(_valid_days)

        # Ensure user has selected at least 1 day
        if "1" not in valid_days:
            flash("You must choose at least one working day.")
            return render_template("register.html")

        # Register user into users table
        db.execute("INSERT INTO users (username, hash, name, hours, minutes, days, lastlog, lastdate) VALUES(?, ?, ?, ?, ?, ?, ?, ?)",
                   request.form.get("username"), generate_password_hash(request.form.get("password")),
                   request.form.get("fullname"), request.form.get("hours"), request.form.get("minutes"), valid_days, 0, datetime.date.today().strftime('%Y%m%d'))

        return redirect("/")
    else:
        return render_template("register.html")