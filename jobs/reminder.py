#!/usr/bin/env python3

from app import db, User, weekdays
import os
import requests

from dotenv import load_dotenv
load_dotenv(".env")
import os
BOT_TOKEN = os.getenv("BOT_TOKEN")

endpoint = "https://slack.com/api/chat.postMessage"

weekday_order = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']

users = User.query.all()
for user in users:
    schedule = sorted([day for day in weekdays.values() if getattr(user, day)], key=weekday_order.index)
    diet = user.diet if user.diet else "None"

    if len(schedule) > 0:
        message = 'hi ' + user.name.capitalize() + ". Your lunch schedule for next week is *" + diet + "* on *" + ", ".join(day for day in schedule[:-1]) + " & " + str(schedule[-1]) + "*.\n\n" + "You can leave it alone if you're happy with that - otherwise don't forget to use `/lunch` in your team's channel to change your preferences." 
    else:
        message = 'hi ' + user.name.capitalize() + ", your lunch schedule for next week is empty. You can leave it alone if you're not having lunch next week - otherwise don't forget to use `/lunch` in your team channel to change it."

    message += "\n\n Remember to adjust next week's order between 9:00 a.m. on Monday and noon on Friday.\n\nNext week's menu can be read at https://go.tq.co/lunch\n\n"

    slack_data = {'token': BOT_TOKEN, 'text': message, 'channel': '@' + user.name}
    print(slack_data)
    response = requests.post(endpoint, data=slack_data)
