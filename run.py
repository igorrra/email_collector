#!venv/bin/python

"""
RESTful API for email collector
"""

import argparse
import os
import shutil

import logging.config

from ConfigParser import ConfigParser

from flask import Flask, Response
from flask import flash, jsonify, make_response, redirect, request

from flaskext.mysql import MySQL
from utils.email_parser import parse_raw_email
from werkzeug.utils import secure_filename

from lib.database import (
    get_data, post_data, delete_data, put_data, join_report
)

CONFIG_PATH = 'config/config.cfg'
ALLOWED_EMAIL_EXTENSIONS = {'msg', 'txt'}

config = ConfigParser()
config.read(CONFIG_PATH)

app = Flask(__name__)

app.config['DEVELOPMENT'] = config.get('flask', 'development')
app.config['SECRET_KEY'] = config.get('flask', 'secret_key')
app.config['SESSION_TYPE'] = config.get('flask', 'session_type')
app.config['DB_HOST'] = config.get('flask', 'db_host')
app.config['UPLOAD_FOLDER'] = config.get('flask', 'upload_folder')
app.config['MYSQL_DATABASE_USER'] = config.get('mysql', 'user')
app.config['MYSQL_DATABASE_PASSWORD'] = config.get('mysql', 'password')
app.config['MYSQL_DATABASE_DB'] = config.get('mysql', 'db')
app.config['MYSQL_DATABASE_HOST'] = config.get('mysql', 'host')

mysql = MySQL()
mysql.init_app(app)
db = mysql.connect()

logging.config.fileConfig(CONFIG_PATH)
logger = logging.getLogger(__name__)


def allowed_file(filename):
    """Check if uploaded file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EMAIL_EXTENSIONS


@app.route('/api/v1.0/tables/<table_name>', methods=['GET'])
def get_table(table_name):
    """Show contents of specified table."""
    if request.method == 'GET':
        logger.debug('Show "%s" table called', table_name)
        return jsonify({'Response': get_data(db, table_name)})


@app.route('/api/v1.0/tables/<table_name>/<data_id>',
           methods=['GET', 'DELETE', 'PUT'])
def get_table_id(table_name, data_id):
    """Show contents of specified table."""
    if request.method == 'GET':
        logger.debug('Show "%s/%s" table called', table_name, data_id)
        return jsonify({'Response': get_data(db, table_name, data_id)})
    elif request.method == 'PUT':
        logger.debug('Update report by metadata id called')
        return jsonify({'Response': put_data(db, data_id, request.json)})
    elif request.method == 'DELETE':
        logger.debug('Delete "%s/%s" table called', table_name, data_id)
        return jsonify({'Response': delete_data(db, table_name, data_id)})


@app.route('/api/v1.0/email/report', methods=['GET'])
def report():
    """Show contents of all joined tables."""
    logger.debug('Show aggregate report called')
    return jsonify({'Response': join_report(db)})


@app.route('/api/v1.0/email/report/<metadata_id>',
           methods=['GET', 'DELETE', 'PUT'])
def report_by_id(metadata_id):
    """Show contents of all joined tables."""
    if request.method == 'GET':
        logger.debug('Show report by metadata id called')
        return jsonify({'Response': join_report(db, metadata_id)})
    elif request.method == 'PUT':
        logger.debug('Update report by metadata id called')
        return jsonify({'Response': put_data(db, metadata_id, request.json)})
    elif request.method == 'DELETE':
        logger.debug('Delete report for metadata id=%s called', metadata_id)
        return jsonify({'Response': delete_data(db, 'metadata', metadata_id)})


@app.route('/api/v1.0/email', methods=['GET', 'POST'])
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
            if not os.path.exists(app.config['UPLOAD_FOLDER']):
                os.mkdir(app.config['UPLOAD_FOLDER'])
            file_name = secure_filename(uploaded_file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_name)
            uploaded_file.save(file_path)
            logger.debug('Uploaded email file was saved to %s',
                         app.config['UPLOAD_FOLDER'])
            parsed = parse_raw_email(file_path)
            shutil.rmtree((app.config['UPLOAD_FOLDER']))
            if parsed and parsed.get('from'):
                logger.info('Email was parsed successfully')
                logger.debug('POST email data into corresponding tables')
                return jsonify({'Response': post_data(db, parsed)})

            logger.error('Unsupported email content received')
            return jsonify(
                {'Response': 'Unsupported email content received'}
            )
    try:
        with open('app/templates/index.html', 'r') as index:
            content = index.read()
    except IOError as exc:
        content = str(exc)
    return Response(content, mimetype="text/html")


@app.errorhandler(404)
def not_found(error):
    """Not found error."""
    return make_response(jsonify({'Error': 'Not found'}), 404)


def parse_args():
    """Parsing arguments function."""
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
    ARGS = parse_args()
    app.run(debug=ARGS.debug, host=ARGS.host, port=ARGS.port)
