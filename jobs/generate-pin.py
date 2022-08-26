from app import User
import click
import sqlite3
import string
import random
from flask import g, Flask, request, make_response, Response, send_from_directory, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from slackclient import SlackClient

from dotenv import load_dotenv
load_dotenv(".env")

@click.command()
@click.option('--amount', default=1, help='number of pins to generate.')
@click.option('--company', default=False, is_flag=True)
def generate_pin(amount, company):
    pins = []
    company_ids = []
    ids_pins = {}
    while len(pins) < amount:
        pin = str(random.randint(0, 10**4)).zfill(4)
        while User.query.filter(User.pin==pin).first():
            pin = str(random.randint(0, 10**4)).zfill(4)
        pins.append(pin)
        if company:
            company_ids.append('T' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8)))
        ids_pins = dict(zip(company_ids, pins)) 
    if ids_pins:
        click.echo(ids_pins)    
    else:
        click.echo(pins)
    
if __name__ == '__main__':
    generate_pin()
