#!venv/bin/python

"""
RESTful API for email collector
"""

import argparse

import os
import shutil

from flask import (
    flash, jsonify, make_response, Response, request, redirect
)

from utils.email_parser import parse_raw_email
from werkzeug.utils import secure_filename

from app import ALLOWED_EXTENSIONS, app, db, logger
from lib.database import get_data, post_data, delete_data, join_report


def allowed_file(filename):
    """Check if uploaded file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/api/v1.0/tables/<table_name>', methods=['GET'])
def get_table(table_name):
    """Show contents of specified table."""
    if request.method == 'GET':
        logger.debug('Show "%s table called', table_name)
        return jsonify(get_data(db, table_name))


@app.route('/api/v1.0/tables/<table_name>/<data_id>',
           methods=['GET', 'DELETE', 'PUT'])
def get_table_id(table_name, data_id):
    """Show contents of specified table."""
    if request.method == 'GET':
        logger.debug('Show "%s/%s" table called', table_name, data_id)
        return jsonify(get_data(db, table_name, data_id))
    elif request.method == 'DELETE':
        logger.debug('Delete "%s/%s" table called', table_name, data_id)
        result = delete_data(db, table_name, data_id)
        return jsonify({'Response': result})


@app.route('/api/v1.0/email/report', methods=['GET'])
def report():
    """Show contents of all joined tables."""
    logger.debug('Show aggregate report called')
    return jsonify(join_report(db))


@app.route('/api/v1.0/email/report/<metadata_id>',
           methods=['GET', 'DELETE', 'PUT'])
def report_by_id(metadata_id):
    """Show contents of all joined tables."""
    if request.method == 'GET':
        logger.debug('Show report by metadata id called')
        return jsonify(join_report(db, metadata_id))
    elif request.method == 'DELETE':
        logger.debug('Delete "%s/%s" report called', metadata_id)
        result = delete_data(db, 'metadata', metadata_id)
        return jsonify({'Response': result})


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
                result = post_data(db, parsed)
                return jsonify({'Response': result})
            else:
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
    app.run(debug=args.debug, host=args.host, port=args.port)
