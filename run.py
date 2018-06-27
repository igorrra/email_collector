#!venv/bin/python

"""
RESTful API for email collector
"""

import argparse
import logging.config
import os
import shutil
import uuid
from ConfigParser import ConfigParser

from flask import Flask
from flask import flash, jsonify, make_response, redirect, request, send_file

from flask_httpauth import HTTPBasicAuth
from flaskext.mysql import MySQL
from pymysql.cursors import DictCursor
from utils.email_parser import parse_raw_email
from werkzeug.utils import secure_filename

from src.python.core.database import (
    post, delete, put, read
)
from src.python.core.email_parser import parse_raw_email

CONFIG_PATH = 'etc/config.cfg'
ALLOWED_EMAIL_EXTENSIONS = {'msg', 'txt'}

config = ConfigParser()
config.read(CONFIG_PATH)

app = Flask(__name__)

app.config['DEVELOPMENT'] = config.get('flask', 'development')
app.config['SECRET_KEY'] = config.get('flask', 'secret_key')
app.config['SESSION_TYPE'] = config.get('flask', 'session_type')
app.config['DB_HOST'] = config.get('flask', 'db_host')
app.config['UPLOAD_DIR'] = config.get('flask', 'upload_dir')
app.config['ATTACHMENTS_DIR'] = config.get('flask', 'attachments_dir')
app.config['MYSQL_DATABASE_USER'] = config.get('mysql', 'user')
app.config['MYSQL_DATABASE_PASSWORD'] = config.get('mysql', 'password')
app.config['MYSQL_DATABASE_DB'] = config.get('mysql', 'db')
app.config['MYSQL_DATABASE_HOST'] = config.get('mysql', 'host')

auth = HTTPBasicAuth()

mysql = MySQL(cursorclass=DictCursor)
mysql.init_app(app)

logging.config.fileConfig(CONFIG_PATH)
logger = logging.getLogger(__name__)


@app.route('/api/v1/email', methods=['GET', 'POST'])
@auth.login_required
def upload_email():
    """Create new entries in database by parsing uploaded emails."""
    db = mysql.connect()
    u_id = str(uuid.uuid4())
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        uploaded_file = request.files['file']

        if uploaded_file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if uploaded_file and allowed_file(uploaded_file.filename):
            if not os.path.exists(app.config['UPLOAD_DIR']):
                os.mkdir(app.config['UPLOAD_DIR'])
            os.mkdir(os.path.join(app.config['UPLOAD_DIR'], u_id))
            file_name = secure_filename(uploaded_file.filename)
            file_path = os.path.join(
                app.config['UPLOAD_DIR'], u_id, file_name
            )
            uploaded_file.save(file_path)
            logger.debug('Uploaded email file was saved to %s',
                         app.config['UPLOAD_DIR'])
            parsed = parse_raw_email(
                file_path, u_id, app.config['ATTACHMENTS_DIR']
            )
            if parsed and parsed.get('from'):
                logger.info('Email was parsed successfully')
                logger.debug('POST email data into corresponding tables')
                result, st_code = post(db, parsed)
                return make_response(jsonify({'Response': result}), st_code)

            logger.error('Unsupported email content received')
            return make_response(
                jsonify({'Response': 'Unsupported email content received'}),
                415)
    try:
        with open('www/static/index.html', 'r') as index:
            content = index.read()
    except IOError as exc:
        content = str(exc)
    return make_response(content, 200)


@app.route('/api/v1/email/all', methods=['GET'])
@auth.login_required
def read_email():
    """Show contents of all joined tables."""
    db = mysql.connect()
    logger.debug('Show aggregate report called')
    result, st_code = read(db)
    return make_response(jsonify(result), st_code)


@app.route('/api/v1/email/<int:metadata_id>',
           methods=['GET', 'DELETE', 'PUT'])
@auth.login_required
def work_with_email_by_id(metadata_id):
    """Show contents of all joined tables."""
    db = mysql.connect()
    if request.method == 'GET':
        logger.debug('Show email for metadata id=%s called', metadata_id)
        result, st_code = read(db, metadata_id)
        return make_response(jsonify(result), st_code)
    elif request.method == 'PUT':
        logger.debug('Update email for metadata id=%s called', metadata_id)
        result, st_code = put(db, metadata_id, request.json)
        return make_response(jsonify({'Response': result}), st_code)
    elif request.method == 'DELETE':
        logger.debug('Delete email for metadata id=%s called', metadata_id)
        res, status = read(db, metadata_id)
        if status == 200 and res[0].get('source_email_path'):
            remove_saved_files(
                res[0].get('source_email_path'),
                [
                    app.config['UPLOAD_DIR'],
                    app.config['ATTACHMENTS_DIR']
                ]
            )
        db = mysql.connect()
        result, st_code = delete(db, metadata_id)
        return make_response(jsonify({'Response': result}), st_code)


@app.route('/api/v1/email/<directory>/<subdirectory>/<filename>')
@auth.login_required
def download_file(directory=None, subdirectory=None, filename=None):
    """Download attachment from server."""
    path = os.path.join(directory, subdirectory, filename)

    if request.method == 'GET':
        try:
            if os.path.exists(path):
                logger.debug('Download attachment %s called', path)
                return send_file(path, as_attachment=True)

            logger.debug('Nonexistent path specified %s', path)
            return make_response(
                jsonify({'Response': "Selected path '%s' "
                                     "does not exist" % path}), 400)
        except Exception as error:
            logger.exception(error)
            return make_response(
                jsonify({'Response': error}), 400)


@app.errorhandler(404)
def not_found(error):
    """Not found error."""
    return make_response(jsonify({'Error': 'Not found'}), 404)


@auth.get_password
def get_password(username):
    """Basic authorization."""
    if username == config.get('flask', 'user'):
        return config.get('flask', 'password')
    return None


@auth.error_handler
def unauthorized():
    """Unauthorized error."""
    return make_response(jsonify({'Error': 'Unauthorized access'}), 401)


def allowed_file(filename):
    """Check if uploaded file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EMAIL_EXTENSIONS


def remove_saved_files(param, directories):
    """Remove saved files (uploaded entire email and related
    saved attachments)."""
    if param:
        for directory in directories:
            path = os.path.join(
                directory, param.split('/')[1]
            )
            if path and os.path.exists(path):
                logger.debug('Delete %s called', path)
                shutil.rmtree(path)


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
