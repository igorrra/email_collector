#!venv/bin/python

"""
RESTful API for email collector
"""


import os
import logging

import logging.config

import mysql.connector

from flask import Flask, jsonify, abort, make_response
from flaskext.mysql import MySQL

APP = Flask(__name__)
MYSQL = MySQL()

# MySQL configurations
APP.config['MYSQL_DATABASE_USER'] = 'root'
APP.config['MYSQL_DATABASE_PASSWORD'] = 'password'
APP.config['MYSQL_DATABASE_DB'] = 'email_collector'
APP.config['MYSQL_DATABASE_HOST'] = 'localhost'

MYSQL.init_app(APP)
DB = MYSQL.connect()

TABLES = [
    'attachments', 'metadata', 'recipients',
    'metadata_attachments', 'metadata_recepients'
]

LOG_CONF_PATH = './log.conf'

if os.path.exists(LOG_CONF_PATH):
    logging.config.fileConfig('log.conf')
else:
    logging.basicConfig(
        format='%(asctime)s %(levelname)s: %(message)s',
        datefmt='%m.%d.%Y %H:%M:%S',
        filename='try_logging_no_config_file.log',
        filemode='w',
        level=logging.DEBUG
    )


@APP.route('/api/v1/tables', methods=['GET'])
def list_tables():
    """Show available tables."""
    cmd = 'show tables'
    try:
        with DB.cursor() as cur:
            cur.execute(cmd)
        logging.debug('Calling "%s" command', cmd)
        rows = [dict((cur.description[i][0], value)
                     for i, value in enumerate(row)) for row in cur.fetchall()]
        return jsonify({'myCollection': rows})
    except mysql.connector.Error as err:
        logging.warning('Something went wrong: %s', err)
        DB.rollback()


@APP.route('/api/v1/tables/<table_name>', methods=['GET'])
def get_table(table_name):
    """Show contents of specified table."""
    if table_name not in TABLES:
        abort(400)
    cmd = 'SELECT * FROM %s' % (table_name, )
    try:
        logging.debug('Calling "%s" command', cmd)
        with DB.cursor() as cur:
            cur.execute(cmd)
        rows = [dict((cur.description[i][0], value)
                     for i, value in enumerate(row)) for row in cur.fetchall()]
        return jsonify({'myCollection': rows})
    except mysql.connector.Error as err:
        logging.warning('Something went wrong: %s', err)
        DB.rollback()


@APP.errorhandler(404)
def not_found(error):
    """Not found error."""
    return make_response(jsonify({'error': 'Not found'}), 404)


if __name__ == '__main__':
    APP.run(debug=True)
