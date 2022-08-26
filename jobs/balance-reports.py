from app import db, weekday_order, diets

import datetime
import xlsxwriter
import string

def transpose_matrix(matrix):
    return list(map(list, zip(*matrix)))

individuals = []
weeknr = datetime.datetime.now().date().isocalendar()[1]

# Query DB for list of individuals & schedules
individuals = list(db.engine.execute('select user.name, user.team, `order`.monday, `order`.tuesday, `order`.wednesday, `order`.thursday, `order`.friday, count(`transaction`.id) from `user` join `transaction` on `transaction`.user_id = user.id join `order` on `order`.user_id = user.id where `order`.week=' + weeknr + ' and `transaction`.date > DATETIME("now", "-6 days") group by user.id order by team, name;'))

# Initialize formula and worksheet 
formula = '=(SUM(Table1[@[Monday]:[Friday]])-(Table1[@[Redeemed]]))'
columns = [
    {'header': 'Person'},
    {'header': 'Team'},
    {'header': 'Monday'},
    {'header': 'Tuesday'},
    {'header': 'Wednesday'},
    {'header': 'Thursday'},
    {'header': 'Friday'},
    {'header': 'Redeemed'},
    {'header': 'Differential',
        'formula':formula},
]

endrow = str(len(individuals) + 2)

filename = 'reports/balances-wk%s.xlsx' % (weeknr)
workbook = xlsxwriter.Workbook(filename)
worksheet1 = workbook.add_worksheet('Balances')


worksheet1.write('A1', 'Week %s' % (weeknr))
worksheet1.add_table('A2:%s%s' % (string.ascii_uppercase[len(columns) - 1], len(individuals)+2), {'data': individuals,
                                'columns': columns})
# format RED bg for below zero
format1 = workbook.add_format({'bg_color': '#FFC7CE'})

# format GREEN bg for above zero
format2 = workbook.add_format({'bg_color': '#C6EFCE'})
worksheet1.conditional_format('I3:I' + endrow, {'type':     'cell',
                                        'criteria': '<',
                                        'value':    0,
                                        'format':   format1})

worksheet1.conditional_format('I3:I' + endrow, {'type':     'cell',
                                        'criteria': '>=',
                                        'value':    0,
                                        'format':   format2})
workbook.close()

