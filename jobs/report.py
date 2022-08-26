#!/usr/bin/env python3

from app import db, weekday_order, diets

import datetime
import xlsxwriter
import string

def transpose_matrix(matrix):
    return list(map(list, zip(*matrix)))

weeknr = datetime.datetime.now().date().isocalendar()[1] + 1

filename = 'reports/lunch-order-wk%s.xlsx' % (weeknr)
workbook = xlsxwriter.Workbook(filename)
worksheet1 = workbook.add_worksheet('Kitchen')
worksheet2 = workbook.add_worksheet('Teams')
worksheet3 = workbook.add_worksheet('Individuals')
teams = [tup[0] for tup in db.engine.execute('select team from user group by team')]
entries = []
individuals = []
team_totals = []
row = 2

for day in weekday_order:
    day = transpose_matrix(list(db.engine.execute('select diet, count(id) from user where ' + day +'=1 group by diet')))
    entry = [ day[1][day[0].index(diet)] if diet in day[0] else '' for diet in diets ]
    entries.append(entry)

worksheet1.write('A1', 'Week %s' % (weeknr))
for day in weekday_order:
    worksheet1.write(row, 0, day)
    row += 1
worksheet1.add_table('B2:D%s' % (len(entries)+2), {'data': entries,
                                'columns': [{'header': 'Normal'},
                                    {'header': 'Vegetarian'},
                                    {'header': 'Vegan'},
                                    ]})

teamOrder = list(db.engine.execute('SELECT team, SUM(monday) + SUM(tuesday) + SUM(wednesday) + SUM(thursday) + SUM(friday) FROM user GROUP BY team ORDER BY team;'))
print(teamOrder)

worksheet2.write('A1', 'Week %s' % (weeknr))
worksheet2.add_table('B2:C%s' % (len(teamOrder)+2), {'data': teamOrder,
                                'columns': [{'header': 'Team'},
                                    {'header': 'Orders'},
                                    ]})

columns = [
    {'header': 'Person'},
    {'header': 'Team'},
    {'header': 'Diet'},
    {'header': 'Monday'},
    {'header': 'Tuesday'},
    {'header': 'Wednesday'},
    {'header': 'Thursday'},
    {'header': 'Friday'},
    {'header': 'Allergy1'},
    {'header': 'Allergy2'},
    {'header': 'Allergy3'},
    {'header': 'Allergy4'},
]
individuals = list(db.engine.execute('select name, team, diet, monday, tuesday, wednesday, thursday, friday, allergy1, allergy2, allergy3, allergy4 from user order by team, name'))
worksheet3.write('A1', 'Week %s' % (weeknr))
worksheet3.add_table('A2:%s%s' % (string.ascii_uppercase[len(columns) - 1], len(individuals)+2), {'data': individuals,
                                'columns': columns})
workbook.close()

import requests
from dotenv import load_dotenv
load_dotenv(".env")
import os
BOT_TOKEN = os.getenv("BOT_TOKEN")

endpoint = "https://slack.com/api/chat.postMessage"
message = "Hi Marvin, the lunch report is ready for you: https://" + os.getenv("APP_URL", "localhost") + "/%s" % filename
slack_data = {'token': BOT_TOKEN, 'text': message, 'channel': '@marvin'}
print(slack_data)

response = requests.post(endpoint, data=slack_data)
