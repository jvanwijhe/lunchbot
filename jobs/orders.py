#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import User, Order

import datetime

import sqlite3
from flask_sqlalchemy import SQLAlchemy
from flask import Flask

from dotenv import load_dotenv
load_dotenv(".env")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lunchbot.db'
db = SQLAlchemy(app)

users = User.query.all()

weeknr = datetime.datetime.now().date().isocalendar()[1] + 1

for user in users:
    order = Order(user.id, weeknr)  
    order.monday = user.monday
    order.tuesday = user.tuesday
    order.wednesday = user.wednesday
    order.thursday = user.thursday
    order.friday = user.friday
    db.session.add(order)
    db.session.commit()
