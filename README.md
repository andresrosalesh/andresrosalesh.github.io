# About Deep Worker

## Deep Worker is a simple productivity tool which allows you to track how well you spend your working hours and understand trends in your productivity and well-being.

## It is inspired by Cal Newport's book *Deep Work*, which stresses that people should be highly efficient with the time they use to work. This allows for more work to get done in shorter periods of time, as well as more enjoyment of the work because people enter a state of flow, where they are fully engaged with a task, while doing deep work.

## Deep work also leaves more time in the day for leisure. Newport encourages people to end their work days ritualistically with a final shutdown routine.

# Usage

## This tool allows users to: 

- ## Track time spent on tasks, classifying each task as a period of deep or "shallow" work
- ## Set goals for daily working hours throughout the week
- ## Finish work days with a shutdown sequence that records summary data such as daily mood, the previous night's sleep quality, and more, and allow the user to journal any thoughts before ending the day
- ## Access a trends report which displays user's productivity over time and generates related statistics
- ## Access previous time tracking and shutdown data

## Steps:

- ## **Registration**: Register for an account, noting that you must specify some number of hours to work per day and which days of the week you will be working. For all remaining hours which you do not log during a day, they will be recorded as "No Work Hours". For example, if you commit to working 8 hours a day M-F, and on Wedndesday you log 6 hours of deep or shallow work, then the application will store the remaining 2 hours as "No Work Hours". 
![Registration](/static/images/register.png)
- ## **Time Tracking**: After logging in, use the "Track Your Time" module on the home page to submit time trackings. Hit **start** to start the timing, **stop** to pause it, and **reset** to reset the timing. Fill out the task description to describe what you worked on. Classify the task as either deep or shallow work; be conservative with what is deep work - you must have felt very engaged in the task, and it must have demanded close attention. The timer must be stopped prior to submitting a timing.
![Time](/static/images/time.png)
- ## **Shutdown**: Hitting the **Complete Shutdown** button on the homepage will take you to the shutdown form, where you will fill our details regarding your previous day's sleep, mood, etc. After submitting, you will be taken to a celebratory page congratulating you on finishing the day.
![Shutdown](/static/images/shutdown.png)
- ## **Goals**: Access the goals you committed to upon registration. You may also submit a form to update your profile details, i.e. your working hours and days commitment you made when registering.
![Goals](/static/images/goals.png) 
- ## **Trends**: On Trends, you will find a line graph of your deep work, shallow work, and no work hours throughout the week. You may also switch the view to a whole month's viewing. Below that are analytics tying your work productivity to details you give when shutting down for the day. As mentioned above, if you do not log enough time to meet your daily working goals, then that remaining time will appear as "No Work" under trends, allowing you to see how many hours of work you did not do. This is updated up to the previous day, allowing you to still get the current day's work in.
![Weekly Trends](/static/images/weektrends.png)
![Monthly Trends](/static/images/monthtrends.png)
![Analytics](/static/images/analytics.png)
- ## **Logs**: Access your previous time trackings and shutdown submissions.
![Time Logs](/static/images/logstime.png)
![Shutdown Logs](/static/images/logsshutdown.png)

## Users may access the sample account with username 'kidus' and password 'kidus' to play around with a more fleshed out profile.

# Website

## The website is currently hosted on Heroku at: https://git.heroku.com/deep-worker.git

## You may also access the application through the terminal by running 

```
flask run
```

## and hitting the generated web server. 

# Video Demonstration

## An online video demonstration of the web application can be found here:

# Contact

### If you have any questions or suggestions about this application, contact Kidus Negesse (kanegesse AT college DOT harvard DOT edu) or Andrés Rosales (arosales AT college DOT harvard DOT edu).