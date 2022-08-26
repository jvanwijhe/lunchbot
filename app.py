#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import sqlite3
import datetime
import random
from flask import g, Flask, request, make_response, Response, send_from_directory, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from slackclient import SlackClient

from dotenv import load_dotenv
load_dotenv(".env")
import os
BOT_TOKEN = os.getenv("BOT_TOKEN")

diets = ['omni', 'vegetarian', 'vegan']
weekdays = {'m': 'monday', 'tu': 'tuesday', 'w': 'wednesday', 'th': 'thursday', 'f': 'friday'}
weekday_order = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']

channels = {'GBL0RUWMD': 'tnw-test', 
            'CCLR422RM': 'cooper',
            'G20SB497U': 'homerun',
            'G3KNYAWBT': 'katalysis',
            'G2W8TDE6M': 'prco',
            'G2Q732N92': 'tnw',
            'G43APP3QU': 'tripaneer',
            'GDM08H39S': 'tq',
            'G8H9KUCB1': 'starred',
            'G6WJ5HENS': 'trueclicks',
            'G629QG9BP': 'secfi',
            'G278SACTS': 'opensocial',
            'G20RTJX4P': 'autheos',
            'G5Y8E7P1D': 'creative-fabrica',
            'G9JGS4PEK': 'realtimeboard',
            'GCD6Z2SJ1': 'honeypot'
            }

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lunchbot.db'
db = SQLAlchemy(app)
slack_client = SlackClient(BOT_TOKEN)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    slack_id = db.Column(db.String(80), unique=True)
    name = db.Column(db.String(120), None)
    diet = db.Column(db.String(80), None)
    monday = db.Column(db.Boolean, default=1)
    tuesday = db.Column(db.Boolean, default=1)
    wednesday = db.Column(db.Boolean, default=1)
    thursday = db.Column(db.Boolean, default=1)
    friday = db.Column(db.Boolean, default=1)
    team = db.Column(db.String(120), None)
    allergy1 = db.Column(db.String(120), None)
    allergy2 = db.Column(db.String(120), None)
    allergy3 = db.Column(db.String(120), None)
    allergy4 = db.Column(db.String(120), None)
    pin = db.Column(db.String(80), unique=True)
    balance = db.Column(db.Integer, default=0)
    admin_level = db.Column(db.Integer, default=0)

    def __init__(self, slack_id):
        self.slack_id = slack_id

    def __repr__(self):
        return('<User %r>' % self.name)

class Token(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    code = db.Column(db.Integer, nullable=False)
    redeemed = db.Column(db.Boolean, default=0)

    def __init__(self, user_id, code):
        self.user_id = user_id
        self.code = code

    def __repr__(self):
        return('<Token %r>' % self.code)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    week = db.Column(db.Integer, None)
    monday = db.Column(db.Boolean, None)
    tuesday = db.Column(db.Boolean, None)
    wednesday = db.Column(db.Boolean, None)
    thursday = db.Column(db.Boolean, None)
    friday = db.Column(db.Boolean, None)

    def __init__(self, user_id, week):
        self.user_id = user_id
        self.week = week

    def __repr__(self):
        return('<Order %r>' % self.week)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.DateTime(timezone=True), default=datetime.datetime.utcnow)

    def __init__(self, user_id):
        self.user_id = user_id

    def __repr__(self):
        return('<Transaction %r>' % self.date)

class Donation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    donator = db.Column(db.String(80))
    date = db.Column(db.DateTime(timezone=True), default=datetime.datetime.utcnow)
    redeemed = db.Column(db.Boolean, default=0)
    claimed_by = db.Column(db.String(80))

    def __init__(self, user_id):
        self.user_id = user_id

    def __repr__(self):
        return('<Donation %r>' % self.user_id)

def get_user(slack_id):
    user = User.query.filter_by(slack_id=slack_id).first()
    if not user:
        user = User(slack_id)
        db.session.add(user)
    return user

def set_team(user, channel_id):
    for channel in channels.keys():
        if channel == channel_id:
            team = channels[channel]
            user.team = team
            db.session.commit()
    return team

def set_pin(user):
    pin = str(random.randint(0, 10**4)).zfill(4)
    while User.query.filter(User.pin==pin).first():
        pin = str(random.randint(0, 10**4)).zfill(4)
    user.pin = pin
    db.session.commit()
    return pin


def get_schedule(user):
    schedule = sorted([day for day in weekdays.values() if getattr(user, day)], key=weekday_order.index)
    return schedule

def get_allergies(user):
    allergies = [getattr(user, 'allergy' + str(number)) for number in range(1, 5) if getattr(user, 'allergy' + str(number))]
    return allergies

def get_params():
    payload = request.form.get('payload')
    params = json.loads(payload)
    return params

def is_dialog(params):
    if 'dialog_submission' in params.values():
        button = False
        return button
    else:
        button = True
        return button

def verify_channel(channel_id):
    channel_id = channel_id
    if channel_id in channels.keys():
        valid_channel = True
        return valid_channel
    else:
        pass

@app.route('/', methods=['GET'])
def landing():
    return Response("Welcome to lunchbot")

@app.route('/', methods=['POST'])
def test():
    channel_id = request.form.get('channel_id')
    valid_channel=verify_channel(channel_id)
    if not valid_channel:
        channel_name = request.form.get('channel_name')
        return Response("Sorry, your team '" + channel_name + "' is not subscribed to TQ's lunch plan, but you should really consider joining!")

    name = request.form.get('user_name')
    display_name = request.form.get('name')
    slack_id = request.form.get('user_id')
    user = User.query.filter_by(slack_id=slack_id).first()

    arg = request.form.get('text')
    if arg=='give':
        today = datetime.datetime.today().strftime('%Y-%m-%d')
        donations = db.session.query(Donation).filter(Donation.date.like(today+'%'))
        donator = name

        for open_donation in donations:
            if open_donation.user_id == user.id:
                return Response("You already donated your lunch today.")
        else:
            donation = Donation(user.id)      
            donation.donator = donator
            db.session.add(donation) 
            db.session.commit()
            return Response("You donated your lunch!")

    if arg=='take':
        today = datetime.datetime.today().strftime('%Y-%m-%d')
        donations = db.session.query(Donation).filter(Donation.date.like(today+'%'))
        for donation in donations:
            if donation.redeemed == 0:
                donation = donation
                donation.redeemed = 1
                donation.claimed_by = name
                db.session.commit()
                return Response(":clap:" + donation.donator + " gave " + name + " their lunch! How lovely of them. :clap:")
        else:
            return Response("Whomp whomp")

    with open('forms/place-order.json', 'r') as f:
        message = json.loads(f.read())

    message["text"] = "Hello " + name.capitalize() + "!"
    if user:
        days = get_schedule(user)
        allergies = get_allergies(user)
        if len(days) > 0:
            message["text"] += "\nYour order for next week is *" + user.diet + "* lunch on *" + ", ".join(day for day in days[:-1]).title() + "* & *" + str(days[-1]).capitalize() + "*\n"

            if user.pin:
                message["text"] += "Your PIN code is: *" + str(user.pin) + "*\n"

            if (len(allergies)):
                message["text"] += "Your allergies are: *" + ", ".join(allergy for allergy in allergies[:-1]).title() + "* & *" + str(allergies[-1]).capitalize() + "*"
            else:
                message["text"] += "You don't have any allergies set"

            message["text"] += "\n\n   :memo: *Adjust order:* Working from home one day next week? Adjust your order so we don’t waste food, or worse, don’t have enough for you.\n   :no_entry_sign: *Report allergies:* Let us know what you’re allergic to and we’ll do our best to accommodate.\n   :thumbsup: *Looks good:* My order is perfect as is.\n" 
        else:
            message["text"] += "\nYou don't have a lunch order in place at the moment."

    else:
        message["text"] += "\nYou have not made a lunch order before, let's get started."

    message["text"] +=  "\nCheck out next week's menu: https://go.tq.co/lunch"
    return Response(json.dumps(message), mimetype='application/json')

@app.route('/buttons', methods=['POST'])
def handle_buttons():
    params = get_params()
    button = is_dialog(params)
    slack_id = params['user']['id']
    callback = params['callback_id']

    if button == True:
        option = params['actions'][0]['name']
        trigger_id = params['trigger_id']
        timestamp = params['message_ts']

    if button and option == 'diet_picker':
        with open('forms/diet-menu.json', 'r') as m:
            menu = m.read()
            return Response(menu, mimetype='application/json')

    # serve allergy selection dialog
    elif button and option == "allergies_button":
        with open('forms/allergy-form.json', 'r') as allergypicker:
            allergypicker = json.load(allergypicker)
            allergymenu = slack_client.api_call('dialog.open', trigger_id=params["trigger_id"], dialog=allergypicker)
        return Response(":ok_hand: Awesome, we'll keep your allergies on record. Don't forget to do `/lunch` again if you also need to adjust your order.")

    # write 'pause' to db
    elif button and option == 'pause':
        user = get_user(slack_id)
        for day in weekday_order:
            setattr(user, day, 0)
        db.session.commit()
        return Response(":ok_hand: Great, your lunch order has been paused. We won't make you lunch until you adjust your order in the future.")


    # write diet choice and serve day selector dialog
    elif callback == "diet_options":
        diet = params['actions'][0]['selected_options'][0]['value']

        user = get_user(slack_id)
        channel_id = params['channel']['id']
        team = set_team(user, channel_id)
        name = params['user']['name']
        user.name = name
        user.diet = diet
        db.session.commit()

        with open('forms/order-form.json', 'r') as daypicker:
            daypicker = json.load(daypicker)
            daymenu = slack_client.api_call('dialog.open', trigger_id=params["trigger_id"], dialog=daypicker)
        return Response("Great, we'll keep this order and renew it every week unless you change it.")

    # Write day schedule to database
    elif callback == "daypicker":
        user = get_user(slack_id)
        for day, value in params['submission'].items():
            if value == 'yes':
                setattr(user, day, 1) != "0"
            else:
                setattr(user, day, 0)
        db.session.commit()
        return Response(), 200

    # Write allergies to database
    elif callback == "allergypicker":
        user = get_user(slack_id)
        name = params['user']['name']
        user.name = name
        for allergy, value in params['submission'].items():
            print('ok')
            setattr(user, allergy, value)
        db.session.commit()
        return Response(), 200

    else:
        return Response("Have a nice day!")

@app.route('/reports/<path:path>')
def send_report(path):
    return send_from_directory('reports', path)

@app.route('/tokens', methods=['GET', 'POST'])
def verify_token():
    entered_token = request.args['code']
    user = User.query.filter_by(pin=entered_token).first()
    if user == None:
        return jsonify({'status': 'not_found'})

    user.balance += 1 
    transaction = Transaction(user.id)
    db.session.add(transaction)
    db.session.commit()
    return jsonify({'status': 'ok'})

@app.route('/daily-lunches', methods=['GET'])
def show():
    result = db.engine.execute("""
        SELECT DATE(`date`) as `day`, COUNT(*) as `count`
        FROM `transaction`
        WHERE `date` > DATETIME('now', '-7 days')
        GROUP BY `day`
    """)
    data = {}
    for row in result:
        data[row[0]] = row[1]

    return jsonify(data)

if __name__ == "__main__":
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

