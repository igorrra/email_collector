"""
Database handler module.

Work with DB in order to store and retrieve requested data.
"""

from lib.decorators import db_connection_wrapper


@db_connection_wrapper
def get_data(db_connection, table_name, data_id=None):
    """Show contents of specified table."""
    if table_name and not data_id:
        cmd = 'SELECT * FROM %s' % (table_name, )
    elif table_name and data_id:
        cmd = 'SELECT * FROM %s where id=%s' \
              % (table_name, data_id)
    else:
        cmd = 'show tables'

    cur = db_connection.cursor()
    cur.execute(cmd)
    rows = [
        dict((cur.description[i][0], value)
             for i, value in enumerate(row)) for row in cur.fetchall()
    ]
    return rows


@db_connection_wrapper
def join_report(db_connection, data_id=None):
    """Show report with all data by joining all tables."""
    cmd = 'SELECT m.id metadata_id, sender, recipient, subject, body, ' \
          'html, timestamp, attachment_name, content_type, ' \
          'path, md5 ' \
          'FROM metadata m ' \
          'JOIN attachments a ON m.id=a.metadata_id ' \
          'JOIN recipients r ON m.id=r.metadata_id'
    if data_id:
        cmd += ' WHERE m.id=%s' % (data_id, )
    else:
        cmd += ';'

    cur = db_connection.cursor()
    cur.execute(cmd)
    rows = [
        dict((cur.description[i][0], value)
             for i, value in enumerate(row)) for row in cur.fetchall()
    ]
    return rows


@db_connection_wrapper
def post_data(db_connection, params):
    """Insert posted data into database."""
    cur = db_connection.cursor()
    metadata_cmd = 'INSERT INTO metadata ' \
                   '(sender, subject, body, html, timestamp) ' \
                   'VALUES (\'%s\', \'%s\', \'%s\', \'%s\', \'%s\')' \
                   % (params.get('from'), params.get('subject'),
                      params.get('body'), params.get('html'),
                      params.get('timestamp'))
    cur.execute(metadata_cmd)

    last_id = db_connection.insert_id()

    for recipient in params.get('to'):
        recipients_cmd = 'INSERT INTO recipients ' \
                          '(recipient, metadata_id) ' \
                          'VALUES (\'%s\', \'%s\')' \
                          % (recipient, last_id)
        cur.execute(recipients_cmd)

    for attachment in params.get('attachments'):
        attachments_cmd = 'INSERT INTO attachments ' \
              '(attachment_name, content_type, md5, path, metadata_id) ' \
              'VALUES (\'%s\', \'%s\',\'%s\', \'%s\', \'%s\')' \
              % (attachment.name, attachment.content_type,
                 attachment.md5, attachment.path, last_id)

        cur.execute(attachments_cmd)

    return 'Affected rows: %s' % (cur.rowcount, )


@db_connection_wrapper
def delete_data(db_connection, table_name, data_id):
    """Delete data with specified id from specified table."""
    delete_cmd = 'DELETE FROM %s ' \
                 'WHERE id=%s' % (table_name, data_id)
    cur = db_connection.cursor()
    cur.execute(delete_cmd)
    return 'Affected rows: %s' % (cur.rowcount, )


@db_connection_wrapper
def put_data(db_connection, data_id, params):
    """Update specified data in database."""
    cur = db_connection.cursor()
    for key in params.keys():
        put_cmd = 'UPDATE metadata m ' \
                  'JOIN attachments a ON m.id=a.metadata_id ' \
                  'JOIN  recipients r ON m.id=r.metadata_id ' \
                  'SET %s="%s" WHERE m.id="%s";' \
                  % (key, params['%s' % key], data_id)
        cur.execute(put_cmd)

    return 'Affected rows: %s' % (cur.rowcount, )
