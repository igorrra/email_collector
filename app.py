#!venv/bin/python

"""
RESTful API for email collector
"""

import argparse
import os
import logging

import logging.config

from flaskext.mysql import MySQL

from flask import Flask, flash, jsonify, make_response, request, redirect
from werkzeug.utils import secure_filename

from db_handler import show_tables, show_table, add_data, retrieve_data
from parse_email import parse_raw_email

APP = Flask(__name__)
APP.config.from_object('config.Config')
MYSQL = MySQL()
MYSQL.init_app(APP)
DB = MYSQL.connect()

LOG_CONF_PATH = './log.conf'
ALLOWED_EXTENSIONS = {'msg', 'txt'}

logging.config.fileConfig('log.conf')


def allowed_file(filename):
    """Check if uploaded file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@APP.route('/api/v1.0/tables', methods=['GET'])
def list_tables():
    """Show available tables."""
    logging.debug('List all tables called')
    return jsonify({'AvailableTables': show_tables(DB)})


@APP.route('/api/v1.0/tables/<table_name>', methods=['GET'])
def get_table(table_name):
    """Show contents of specified table."""
    logging.debug('Show "%s" table called', table_name)
    return jsonify({'TableContents': show_table(DB, table_name)})


@APP.route('/api/v1.0/report', methods=['GET'])
def get_data():
    """Show contents of all joined tables."""
    logging.debug('Show all joined tables. called')
    return jsonify({'TableContents': retrieve_data(DB)})


@APP.route('/api/v1.0/upload', methods=['GET', 'POST'])
def add_email():
    """Create new entry."""
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        uploaded_file = request.files['file']

        if uploaded_file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if uploaded_file and allowed_file(uploaded_file.filename):
            filename = secure_filename(uploaded_file.filename)
            uploaded_file.save(os.path.join(APP.config['UPLOAD_FOLDER'], filename))
            logging.debug('email file saved into %s', APP.config['UPLOAD_FOLDER'])
            parsed = parse_raw_email(os.path.join(APP.config['UPLOAD_FOLDER'], filename))
            if parsed.get('from'):
                logging.info('Email was parsed successfully')
            else:
                logging.error('Something went wrong')
            logging.debug('POST email data into corresponding tables called')
            result = add_data(DB, parsed)
            print result
            return jsonify({'Response': 'Email was parsed successfully'})
    return '''
        <!doctype html>
        <title>Upload new File</title>
        <h1>Upload new File</h1>
        <form method=post enctype=multipart/form-data>
          <input type=file name=file>
          <input type=submit value=Upload>
        </form>
        '''


@APP.errorhandler(404)
def not_found(error):
    """Not found error."""
    return make_response(jsonify({'error': 'Not found'}), 404)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-H', '--host',
                        default='127.0.0.1',
                        help='Hostname for the Flask application')
    parser.add_argument('-P', '--port',
                        default='5000',
                        help='Port for the Flask application')
    parser.add_argument('-d', '--debug',
                        action='store_true',
                        help=argparse.SUPPRESS)

    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    APP.run(debug=args.debug, host=args.host, port=args.port)
