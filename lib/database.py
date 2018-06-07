"""
Database handler module.

Work with DB in order to store and retrieve requested data.
"""

import pymysql


def get_data(db_connection, table_name, data_id=None):
    """Show contents of specified table."""
    if table_name and not data_id:
        cmd = 'SELECT * FROM %s' % (table_name, )
    elif table_name and data_id:
        cmd = 'SELECT * FROM %s where id=%s' \
              % (table_name, data_id)
    else:
        cmd = 'show tables'

    with db_connection.cursor() as cur:
        try:
            cur.execute(cmd)
        except pymysql.err.InternalError as error:
            db_connection.rollback()
            return 'Error: %s' % error[:-1]
        rows = [
            dict((cur.description[i][0], value)
                 for i, value in enumerate(row)) for row in cur.fetchall()
        ]
        return rows


def join_report(db_connection, data_id=None):
    """Show report with all data by joining all tables."""
    cmd = 'SELECT m.id metadata_id, sender, recipient, subject, body, ' \
          'html, timestamp, name attachment, content_type attachment_type, ' \
          'path, md5 ' \
          'FROM metadata m ' \
          'JOIN attachments a ON m.id=a.metadata_id ' \
          'JOIN recipients r ON m.id=r.metadata_id'
    if data_id:
        cmd += ' WHERE m.id=%s' % (data_id, )
    else:
        cmd += ';'

    with db_connection.cursor() as cur:
        try:
            cur.execute(cmd)
        except pymysql.err.InternalError as error:
            db_connection.rollback()
            return 'Error: %s' % error
        rows = [
            dict((cur.description[i][0], value)
                 for i, value in enumerate(row)) for row in cur.fetchall()
        ]
        return rows


def post_data(db_connection, params):
    """Insert posted data into database."""
    with db_connection.cursor() as cur:
        metadata_cmd = 'INSERT INTO metadata ' \
                       '(sender, subject, body, html, timestamp) ' \
                       'VALUES (\'%s\', \'%s\', \'%s\', \'%s\', \'%s\')' \
                       % (params.get('from'), params.get('subject'),
                          params.get('body'), params.get('html'),
                          params.get('timestamp'))
        try:
            cur.execute(metadata_cmd)
        except pymysql.err.InternalError as error:
            db_connection.rollback()
            return 'Error: %s' % error

        last_id = db_connection.insert_id()

        for recipient in params.get('to'):
            recipients_cmd = 'INSERT INTO recipients ' \
                              '(recipient, metadata_id) ' \
                              'VALUES (\'%s\', \'%s\')' \
                              % (recipient, last_id)
            cur.execute(recipients_cmd)

        for attachment in params.get('attachments'):
            attachments_cmd = 'INSERT INTO attachments ' \
                  '(name, content_type, md5, path, metadata_id) ' \
                  'VALUES (\'%s\', \'%s\',\'%s\', \'%s\', \'%s\')' \
                  % (attachment.name, attachment.content_type,
                     attachment.md5, attachment.path, last_id)
            try:
                cur.execute(attachments_cmd)
            except pymysql.err.InternalError as error:
                db_connection.rollback()
                return 'Error: %s' % error
            db_connection.commit()
            return 'Affected rows: %s' % (cur.rowcount, )


def delete_data(db_connection, table_name, data_id):
    """Delete data with specified id from specified table."""
    with db_connection.cursor() as cur:
        delete_cmd = 'DELETE FROM %s ' \
                     'WHERE id=%s' % (table_name, data_id)
        try:
            cur.execute(delete_cmd)
        except pymysql.err.InternalError as error:
            db_connection.rollback()
            return 'Error: %s' % error
        db_connection.commit()
        return 'Affected rows: %s' % (cur.rowcount, )


def put_data(db_connection, data_id, params):
    """Update specified data in database."""
    non_existent = []
    response = join_report(db_connection, data_id)
    print response
    if response:
        for key in params.keys():
            if key not in response[0]:
                non_existent.append(key)
        if non_existent:
            return 'Error: Non existent key(s) specified: %s' \
                   % (non_existent, )
    else:
        return 'Non existent id specified: %s' % (data_id, )
    with db_connection.cursor() as cur:
        for key in params.keys():
            put_cmd = 'UPDATE metadata m ' \
                      'JOIN attachments a ON m.id=a.metadata_id ' \
                      'JOIN  recipients r ON m.id=r.metadata_id ' \
                      'SET %s="%s" WHERE m.id="%s";' \
                      % (key, params['%s' % key], data_id)
            try:
                cur.execute(put_cmd)
            except pymysql.err.InternalError as error:
                db_connection.rollback()
                return 'Error: %s' % error[-1:]
        db_connection.commit()
        return 'Affected rows: %s' % (cur.rowcount, )
