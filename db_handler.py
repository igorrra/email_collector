"""
Database handler module.

Work with DB in order to store and retrieve requested data
"""

import mysql.connector

from flask import abort

TABLES = [
    'attachments', 'metadata', 'recipients',
    'metadata_attachments', 'metadata_recipients'
]


def show_tables(db_connection):
    """Show available tables."""
    cmd = 'show tables'
    try:
        with db_connection.cursor() as cur:
            cur.execute(cmd)
        rows = [dict((cur.description[i][0], value)
                     for i, value in enumerate(row)) for row in cur.fetchall()]
        return rows
    except mysql.connector.Error as err:
        db_connection.rollback()


def show_table(db_connection, table_name):
    """Show contents of specified table."""
    if table_name not in TABLES:
        abort(400)
    cmd = 'SELECT * FROM %s' % (table_name, )
    try:
        # logging.debug('Calling "%s" command', cmd)
        with db_connection.cursor() as cur:
            cur.execute(cmd)
            rows = [dict((cur.description[i][0], value)
                         for i, value in enumerate(row)) for row in cur.fetchall()]
            return rows
    except mysql.connector.Error as err:
        logging.warning('Something went wrong: %s', err)
        db_connection.rollback()


def write_data(db_connection, params):
    """Show contents of specified table."""

    cmd = 'INSERT INTO email_collector.metadata ' \
          '(sender, subject, body, html) ' \
          'VALUES (\'%s\', \'%s\', \'%s\', \'%s\')'\
          % (params.get('from'), params.get('subject'),
             params.get('body'), params.get('html'))
    try:
        with db_connection.cursor() as cur:
            cur.execute(cmd)
            rows = [dict((cur.description[i][0], value)
                         for i, value in enumerate(row)) for row in cur.fetchall()]
            db_connection.commit()
            return rows
    except mysql.connector.Error as err:
        logging.warning('Something went wrong: %s', err)
        db_connection.rollback()
