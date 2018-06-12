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
from pymysql.cursors import DictCursor
from utils.email_parser import parse_raw_email
from werkzeug.utils import secure_filename

from lib.database import (
    post, delete, put, read
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

mysql = MySQL(cursorclass=DictCursor)
mysql.init_app(app)

logging.config.fileConfig(CONFIG_PATH)
logger = logging.getLogger(__name__)


def allowed_file(filename):
    """Check if uploaded file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EMAIL_EXTENSIONS


@app.route('/api/v1.0/email', methods=['GET', 'POST'])
def upload_email():
    """Create new entries in database by parsing uploaded emails."""
    db = mysql.connect()
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
                return jsonify({'Response': post(db, parsed)})

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


@app.route('/api/v1.0/email/read', methods=['GET'])
def read_email():
    """Show contents of all joined tables."""
    db = mysql.connect()
    logger.debug('Show aggregate report called')
    return jsonify(read(db))


@app.route('/api/v1.0/email/read/<metadata_id>',
           methods=['GET', 'DELETE', 'PUT'])
def work_with_email_by_id(metadata_id):
    """Show contents of all joined tables."""
    db = mysql.connect()
    if request.method == 'GET':
        logger.debug('Show email for metadata id=%s called', metadata_id)
        result = read(db, metadata_id)
        return jsonify(result)
    elif request.method == 'PUT':
        logger.debug('Update email for metadata id=%s called', metadata_id)
        result = put(db, metadata_id, request.json)
        return jsonify({'Response': result})
    elif request.method == 'DELETE':
        logger.debug('Delete email for metadata id=%s called', metadata_id)
        result = delete(db, metadata_id)
        return jsonify({'Response': result})


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
