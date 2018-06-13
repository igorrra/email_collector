"""
Database handler module.

Work with DB in order to store and retrieve requested data.
"""

import collections

import pprint

from lib.decorators import db_connection_wrapper


@db_connection_wrapper
def read(db_connection, data_id=None):
    """Show report with all data by joining all tables."""
    cmd = 'SELECT m.id id, sender, recipient, subject, body, ' \
          'timestamp, attachment_name, content_type, ' \
          'path, md5 ' \
          'FROM metadata m ' \
          'LEFT JOIN attachments a ON m.id=a.metadata_id ' \
          'LEFT JOIN recipients r ON m.id=r.metadata_id'
    if data_id:
        cmd += ' WHERE m.id=%s' % (data_id, )
    else:
        cmd += ';'

    cur = db_connection.cursor()
    cur.execute(cmd)
    rows = cur.fetchall()

    result = collections.defaultdict(list)

    if rows:
        for row in rows:
            result[row['id']].append(row)
        result_list = result.values()

        final_result = []

        for item in result_list:
            recipients = set()
            res = {
                'attachments': [],
                'id': item[0].get('id'),
                'sender': item[0].get('sender'),
                'subject': item[0].get('subject'),
                'body': item[0].get('body'),
                'timestamp': item[0].get('timestamp')
            }
            for row in item:
                attachment = {
                    'attachment_name': row.get('attachment_name'),
                    'content_type': row.get('content_type'),
                    'md5': row.get('md5'),
                    'path': row.get('path')
                }
                recipients.add(row.get('recipient'))

                if attachment not in res['attachments']:
                    res['attachments'].append(attachment)
                res['recipients'] = list(recipients)

            final_result.append(res)

        return final_result
    else:
        return None


@db_connection_wrapper
def post(db_connection, params):
    """Insert posted data into database."""
    cur = db_connection.cursor()

    cur.execute('SET NAMES utf8mb4')
    cur.execute("SET CHARACTER SET utf8mb4")
    cur.execute("SET character_set_connection=utf8mb4")

    metadata_cmd = 'INSERT INTO metadata ' \
                   '(sender, subject, body, html, timestamp) ' \
                   'VALUES (%s, %s, %s, %s, %s)'
    cur.execute(metadata_cmd,
                (params.get('from'), params.get('subject'),
                 params.get('body'), params.get('html'),
                 params.get('timestamp'))
                )

    last_id = db_connection.insert_id()

    for recipient in params.get('to'):
        recipients_cmd = 'INSERT INTO recipients ' \
                          '(recipient, metadata_id) ' \
                          'VALUES (%s, %s)'
        cur.execute(recipients_cmd, (recipient, last_id))

    for attachment in params.get('attachments'):
        attachments_cmd = 'INSERT INTO attachments ' \
              '(attachment_name, content_type, md5, path, metadata_id) ' \
              'VALUES (%s, %s, %s, %s, %s)'
        cur.execute(attachments_cmd,
                    (attachment.name, attachment.content_type,
                     attachment.md5, attachment.path, last_id)
                    )

    return 'Affected rows: %s' % (cur.rowcount, )


@db_connection_wrapper
def delete(db_connection, data_id):
    """Delete data with specified id from specified table."""
    cur = db_connection.cursor()
    delete_cmd = 'DELETE FROM metadata ' \
                 'WHERE id=%s'
    cur.execute(delete_cmd, (data_id, ))

    return 'Affected rows: %s' % (cur.rowcount, )


@db_connection_wrapper
def put(db_connection, data_id, params):
    """Update specified data in database."""
    cur = db_connection.cursor()
    for key in params.keys():
        put_cmd = 'UPDATE metadata m ' \
                  'LEFT JOIN attachments a ON m.id=a.metadata_id ' \
                  'LEFT JOIN  recipients r ON m.id=r.metadata_id ' \
                  'SET %s="%s" WHERE m.id="%s";' \
                  % (key, params['%s' % key], data_id)
        cur.execute(put_cmd)

    return 'Affected rows: %s' % (cur.rowcount, )
