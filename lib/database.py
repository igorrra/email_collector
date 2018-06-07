"""
Database handler module.

Work with DB in order to store and retrieve requested data
"""

import MySQLdb


def get_data(db_connection, table_name, data_id=None):
    """Show contents of specified table."""
    if table_name and not data_id:
        cmd = 'SELECT * FROM email_collector.%s' % (table_name, )
    elif table_name and data_id:
        cmd = 'SELECT * FROM email_collector.%s where id=%s' \
              % (table_name, data_id)
    else:
        cmd = 'show tables'

    try:
        with db_connection.cursor() as cur:
            cur.execute(cmd)
            rows = [
                dict((cur.description[i][0], value)
                     for i, value in enumerate(row)) for row in cur.fetchall()
            ]
            return rows
    except MySQLdb.DatabaseError:
        db_connection.rollback()


def join_report(db_connection, data_id=None):
    """Show all data by joining all tables."""
    cmd = 'SELECT m.id email_id, sender, email recipient, subject, body, ' \
          'html, timestamp, name attachment, content_type attachment_type, ' \
          'path, md5 ' \
          'FROM metadata m ' \
          'JOIN attachments a ON m.id=a.metadata_id ' \
          'JOIN recipients r ON m.id=r.metadata_id'
    if data_id:
        cmd += ' WHERE m.id=%s' % (data_id, )
    else:
        cmd += ';'
    try:
        with db_connection.cursor() as cur:
            if data_id:
                cur.execute(cmd)
            else:
                cur.execute(cmd)
            rows = [
                dict((cur.description[i][0], value)
                     for i, value in enumerate(row)) for row in cur.fetchall()
            ]
            return rows
    except MySQLdb.DatabaseError:
        db_connection.rollback()


def post_data(db_connection, params):
    """Show contents of specified table."""
    try:
        with db_connection.cursor() as cur:
            metadata_cmd = 'INSERT INTO email_collector.metadata ' \
                           '(sender, subject, body, html, timestamp) ' \
                           'VALUES (\'%s\', \'%s\', \'%s\', \'%s\', \'%s\')' \
                           % (params.get('from'), params.get('subject'),
                              params.get('body'), params.get('html'),
                              params.get('timestamp'))
            cur.execute(metadata_cmd)

            last_id = db_connection.insert_id()

            for recipient in params.get('to'):
                recipients_cmd = 'INSERT INTO email_collector.recipients ' \
                                  '(email, metadata_id) ' \
                                  'VALUES (\'%s\', \'%s\')' \
                                  % (recipient, last_id)
                cur.execute(recipients_cmd)

            for attachment in params.get('attachments'):
                attachments_cmd = 'INSERT INTO email_collector.attachments ' \
                      '(name, content_type, md5, path, metadata_id) ' \
                      'VALUES (\'%s\', \'%s\',\'%s\', \'%s\', \'%s\')' \
                      % (attachment.name, attachment.content_type,
                         attachment.md5, attachment.path, last_id)
                cur.execute(attachments_cmd)
            db_connection.commit()
            return 'Affected rows: %s' % (cur.rowcount,)

    except Exception as error:
        db_connection.rollback()
        return error


def delete_data(db_connection, table_name, data_id):
    try:
        with db_connection.cursor() as cur:
            delete_cmd = 'DELETE FROM email_collector.%s ' \
                         'WHERE id=%s' % (table_name, data_id)
            cur.execute(delete_cmd)
            db_connection.commit()
            return 'Affected rows: %s' % (cur.rowcount, )

    except Exception as error:
        db_connection.rollback()
        return error


def put_data(db_connection, table, params):
    try:
        with db_connection.cursor() as cur:
            put_cmd = ''

    except Exception as error:
        db_connection.rollback()
        return error
