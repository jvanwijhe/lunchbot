#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import User, Token, set_pin

import random

import sqlite3
from flask_sqlalchemy import SQLAlchemy
from flask import Flask

from dotenv import load_dotenv
load_dotenv(".env")

import os
import requests
BOT_TOKEN = os.getenv("BOT_TOKEN")
endpoint = "https://slack.com/api/chat.postMessage"

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lunchbot.db'
db = SQLAlchemy(app)

# Clear all current balances
User.query.update({User.balance: 0})
db.session.commit()

# Assign PINs to new users
teams = ['tnw', 'tq', 'starred', 'trueclicks', 'secfi', 'katalysis', 'homerun', 'prco', 'tripaneer', 'opensocial', 'cooper']
weekdays = {'m': 'monday', 'tu': 'tuesday', 'w': 'wednesday', 'th': 'thursday', 'f': 'friday'}

users = User.query.filter(User.team.in_(teams))

for user in users:
    schedule = len([day for day in weekdays.values() if getattr(user, day)])
    print(user.name, schedule)

    if not user.pin:
        print("notify PIN")
        set_pin(user)

        message = 'Hi ' + user.name.capitalize() + ". Your lunch PIN is:\n"
        message += "`" + user.pin + "`\n"

        slack_data = {'token': BOT_TOKEN, 'text': message, 'channel': '@' + user.name}
        response = requests.post(endpoint, data=slack_data)
