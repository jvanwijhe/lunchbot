#!/usr/bin/env python3

from app import db, weekday_order, diets

import datetime
import xlsxwriter
import string

def transpose_matrix(matrix):
    return list(map(list, zip(*matrix)))

next_week = datetime.datetime.now().date().isocalendar()[1] + 1
this_week = datetime.datetime.now().date().isocalendar()[1]

filename = 'reports/lunch-report-wk%s.xlsx' % (this_week)
workbook = xlsxwriter.Workbook(filename)
worksheet1 = workbook.add_worksheet('Dashboard')
worksheet2 = workbook.add_worksheet('Next Week')
worksheet3 = workbook.add_worksheet('Last Week')
teams = [tup[0] for tup in db.engine.execute('select team from user group by team')]
entries = []
individuals = []
balances = []
team_totals = []
row = 2

# Create formatting
format_monday = workbook.add_format({'bg_color': '#eeb6ad'})
format_tuesday = workbook.add_format({'bg_color': '#fff2c7'})
format_wednesday = workbook.add_format({'bg_color': '#d5ebd1'})
format_thursday = workbook.add_format({'bg_color': '#cbe3f5'})
format_friday = workbook.add_format({'bg_color': '#dbd2eb'})

# Query db for diet totals per day
orders_nextweek = list(db.engine.execute('select diet, sum(monday), sum(tuesday), sum(wednesday), sum(thursday), sum(friday) from user where diet is not null group by diet'))
totals = list(db.engine.execute('select "totals", sum(monday), sum(tuesday), sum(wednesday), sum(thursday), sum(friday) from user where diet is not null'))
orders_nextweek.append(totals[0])


worksheet1.write('A1', 'Week %s' % (next_week))
worksheet1.add_table('B2:G%s' % (len(orders_nextweek)+2), {'data': orders_nextweek, 'banded_rows': False,
                                'columns': [{'header': 'Preference'},
                                    {'header': 'Monday'},
                                    {'header': 'Tuesday'},
                                    {'header': 'Wednesday'},
                                    {'header': 'Thursday'},
                                    {'header': 'Friday'},
                                    ]})


worksheet1.set_column('C2:C', 0, format_monday)
worksheet1.set_column('D2:D', 20, format_tuesday)
worksheet1.set_column('E2:E', 20, format_wednesday)
worksheet1.set_column('F2:F', 20, format_thursday)
worksheet1.set_column('G2:G', 20, format_friday)
                                
# Query DB for individual

individuals = list(db.engine.execute('select name, team, diet, monday, tuesday, wednesday, thursday, friday, (user.monday + user.tuesday + user.wednesday + user.thursday + user.friday) as "Total", allergy1, allergy2, allergy3, allergy4 from user order by team, name'))

formula1 = '=SUM(Table2[@[Monday]:[Friday]])'

columns1 = [
    {'header': 'Person'},
    {'header': 'Team'},
    {'header': 'Preference'},
    {'header': 'Monday'},
    {'header': 'Tuesday'},
    {'header': 'Wednesday'},
    {'header': 'Thursday'},
    {'header': 'Friday'},
    {'header': 'Total'},
    {'header': 'Allergy1'},
    {'header': 'Allergy2'},
    {'header': 'Allergy3'},
    {'header': 'Allergy4'},
]

# Write individuals to worksheet
worksheet2.write('A1', 'Week %s' % (next_week))
worksheet2.add_table('A2:%s%s' % (string.ascii_uppercase[len(columns1) - 1], len(individuals)+2), {'data': individuals,
                                'columns': columns1
                                })

worksheet2.set_column('D2:D', 20, format_monday)
worksheet2.set_column('E2:E', 20, format_tuesday)
worksheet2.set_column('F2:F', 20, format_wednesday)
worksheet2.set_column('G2:G', 20, format_thursday)
worksheet2.set_column('H2:H', 20, format_friday)

# Query DB for list of individuals & schedules
balances = list(db.engine.execute('select user.name, user.team, user.diet, `order`.monday, `order`.tuesday, `order`.wednesday, `order`.thursday, `order`.friday, (`order`.monday + `order`.tuesday + `order`.wednesday + `order`.thursday + `order`.friday) as "Total", count(`transaction`.id) from `user` join `transaction` on `transaction`.user_id = user.id join `order` on `order`.user_id = user.id where `order`.week=' + str(this_week) + ' and `transaction`.date > DATETIME("now", "-6 days") group by user.id order by team, name;'))

# Initialize formula
formula2 = '=(SUM(Table3[@[Monday]:[Friday]])-(Table3[@[Redeemed]]))'
columns2 = [
    {'header': 'Person'},
    {'header': 'Team'},
    {'header': 'Preference'},
    {'header': 'Monday'},
    {'header': 'Tuesday'},
    {'header': 'Wednesday'},
    {'header': 'Thursday'},
    {'header': 'Friday'},
    {'header': 'Total'},
    {'header': 'Redeemed'},
    {'header': 'Differential',
        'formula':formula2},
]

endrow = str(len(balances) + 2)

worksheet3.write('A1', 'Week %s' % (this_week))
worksheet3.add_table('A2:%s%s' % (string.ascii_uppercase[len(columns2) - 1], len(balances)+2), {'data': balances,
                                'columns': columns2})

worksheet3.set_column('D2:D', 20, format_monday)
worksheet3.set_column('E2:E', 20, format_tuesday)
worksheet3.set_column('F2:F', 20, format_wednesday)
worksheet3.set_column('G2:G', 20, format_thursday)
worksheet3.set_column('H2:H', 20, format_friday)

# format RED bg for below zero
format1 = workbook.add_format({'bg_color': '#FFC7CE'})

# format GREEN bg for above zero
format2 = workbook.add_format({'bg_color': '#C6EFCE'})
worksheet3.conditional_format('K3:K' + endrow, {'type':     'cell',
                                        'criteria': '<',
                                        'value':    0,
                                        'format':   format1})

worksheet3.conditional_format('K3:K' + endrow, {'type':     'cell',
                                        'criteria': '>=',
                                        'value':    0,
                                        'format':   format2})

worksheet1.set_column('C:C', 20,format1)
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

#response = requests.post(endpoint, data=slack_data)
