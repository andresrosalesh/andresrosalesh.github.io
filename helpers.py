import os
import requests
import urllib.parse

from cs50 import SQL
from flask import redirect, render_template, request, session
from functools import wraps
import datetime

db = SQL("sqlite:///deepwork.db")

def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

def bin_to_days_of_week(string):
    '''
    Turns a binary string of days into its equivalent weekdays, where the first binary digit corressponds to Monday.

    Example: "1101100" returns ['Monday', 'Tuesday', 'Thursday', 'Friday']
    '''
    if not string:
        return []
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    days_of_week = []
    for i in range(7):
        if string[i] == "1":
            days_of_week.append(days[i])
    return days_of_week

def update_nw_values(user_info):
    '''
    This function fills in the remaining hours not logged during a working day with no work hours (there are shallow key words
    sometimes because the function would previously fill these hours as shallow hours --> refactoring, TODO at some point).

    This is updated each time the user accesses their trends and analytics. Starting with the day
    after the last working day which was udpated with real shallow work, it looks at each day since
    and determines how much no work fills in the remaining time they must be working.

    For example, if the last working day which was updated was 2020-04-26, and it
    is currently 2020-04-30, the function will update the no work work values for 2020-04-27, 2020-04-28,
    and 2020-04-29. It does not udpate 2020-04-30 because that is the current working day, and the user could
    still log in more work.
    '''

    # Get last date udpated
    lastdate = user_info['lastdate']

    # Get user's preferred working hours and days
    total_hours = user_info['hours']
    total_mins = user_info['minutes']
    working_days = bin_to_days_of_week(user_info['days'])
    weekday_mapping = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

    # Update all values up to yesterday
    _currentdate = datetime.date.today() - datetime.timedelta(days=1) # Use datetime object to subtract day
    currentdate = _currentdate.strftime('%Y%m%d')

    # If last updated date was yesterday, no updates are need, exit
    if (lastdate == currentdate):
        return

    # Otherwise, proceed to update
    else:
        # Convert last updated date to datetime object for easy date manipulation
        updatedDate = datetime.datetime(int(lastdate[0:4]), int(lastdate[4:6]), int(lastdate[6:])) + datetime.timedelta(days=1)

        # Iterate until updateddate is the _current_date
        while updatedDate.date() <= _currentdate:
            # If this is a preferred working date for the user
            if (weekday_mapping[updatedDate.weekday()] in working_days):
                # Initialize placeholders
                sw_hours = 0
                sw_mins = 0
                sw_secs = 0
                dw_hours = 0
                dw_mins = 0
                dw_secs = 0

                # Get timing entries for this day and add up the deep work and shallow work times
                entries = db.execute("SELECT * FROM timings WHERE user_id = :id AND start_date = :start_date", id=user_info['id'], start_date=updatedDate.strftime('%Y%m%d'))
                for entry in entries:
                    if entry['dw'] == 0:
                        sw_hours += entry['hours']
                        sw_mins += entry['minutes']
                        sw_secs += entry['seconds']
                    else:
                        dw_hours += entry['hours']
                        dw_mins += entry['minutes']
                        dw_secs += entry['seconds']

                # Convert everything into seconds for easier processing
                # Find difference between total hours user is required to work and the hours they logged (deepwork + shallowwork logged)
                total_secs = (total_hours)*3600 + (total_mins)*60
                recorded_secs = (dw_hours + sw_hours)*3600 + (dw_mins + sw_mins)*60 + (dw_secs + sw_secs)
                diff_secs = total_secs - recorded_secs

                # Enter difference into the shwork table
                diff_hours = diff_secs // 3600
                diff_secs = diff_secs - (diff_hours*3600)
                diff_mins = diff_secs // 60
                diff_secs = diff_secs - (diff_mins*60)

                db.execute("INSERT INTO shwork (user_id, date, hours, minutes, seconds) VALUES(?, ?, ?, ?, ?)",
                       user_info['id'], updatedDate.strftime('%Y%m%d'), diff_hours, diff_mins, diff_secs)

            # Move to next day
            updatedDate += datetime.timedelta(days=1)

    # Update lastdate field in users
    db.execute("UPDATE users SET lastdate = ?", currentdate)
    return