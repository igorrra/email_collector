"""
Parse email module.
Return the necessary email attributes:
from, to, subject, timestamp, body, html, attachments
"""

import hashlib
import os
import time
import uuid

import email

from email.Header import decode_header
from email.utils import parseaddr


from StringIO import StringIO

import dateutil.parser

ATT_TEMPLATE = '%s/%s'
PATH = 'attachments/%s' % (str(uuid.uuid4()),)


class NotSupportedMailFormat(Exception):
    """
    NotSupportedMailFormat exception is raised when
    unsupported email file contents received
    """
    def __init__(self, custom_message):
        msg = '%s' % (custom_message, )
        Exception.__init__(self, msg)


def parse_raw_email(path):
    """Parse email content.

    Get email attributes and file attachments."""
    try:
        with open(path, 'r') as work_file:
            msgobj = email.message_from_file(work_file)
            if 'Received' not in msgobj:
                raise NotSupportedMailFormat(
                    'Unsupported email content received'
                )

        if msgobj.get('Subject'):
            decode_frag = decode_header(msgobj.get('Subject'))
            subj_fragments = []
            for subj, enc in decode_frag:
                if enc:
                    subj = unicode(subj, enc).encode('utf8', 'replace')
                subj_fragments.append(subj)
            subject = ''.join(subj_fragments)
        else:
            subject = None

        date = msgobj.get('Date')
        if date:
            datetime = dateutil.parser.parse(date)
            timestamp = time.mktime(datetime.timetuple())
        else:
            timestamp = None

        attachments = []
        body = None
        html = None
        for part in msgobj.walk():
            attachment = parse_attachment(part)
            if attachment:
                attachments.append(attachment)
            elif part.get_content_type() == 'text/plain':
                if body is None:
                    body = ""
                body += unicode(
                    part.get_payload(decode=True),
                    part.get_content_charset(),
                    'replace'
                ).encode('utf8', 'replace')
            elif part.get_content_type() == 'text/html':
                if html is None:
                    html = ""
                html += unicode(
                    part.get_payload(decode=True),
                    part.get_content_charset(),
                    'replace'
                ).encode('utf8', 'replace')

        return {
            'subject': subject,
            'timestamp': timestamp,
            'body': body,
            'html': html,
            'from': parseaddr(msgobj.get('From'))[1],
            'to': parseaddr(msgobj.get('To'))[1],
            'attachments': attachments
        }

    except NotSupportedMailFormat:
        print 'Not supported email format'
        return None


def parse_attachment(message_part):
    """Function to work with file attachments.

    Get and decode attachment.
    Save attachment to a file."""

    if not os.path.exists(PATH):
        os.mkdir(PATH)

    content_disposition = message_part.get('Content-Disposition')

    if content_disposition:
        dispositions = content_disposition.strip().split(";")
        if bool(content_disposition
                and "attachment" in dispositions[0].lower()):

            file_data = message_part.get_payload(decode=True)
            attachment = StringIO(file_data)
            attachment.content_type = message_part.get_content_type()
            attachment.name = None
            attachment.path = None
            attachment.md5 = None

            for param in dispositions[1:]:
                name, value = param.split('=')
                name = name.lower()

                if 'filename' in name:
                    attachment.name = value.replace('"', '')
                    file_path = ATT_TEMPLATE % (PATH, attachment.name)
                    with open(file_path, 'wb') as destination_file:
                        destination_file.write(file_data)
                    attachment.path = file_path
                    md5_obj = hashlib.md5()
                    md5_obj.update(file_data)
                    attachment.md5 = md5_obj.hexdigest()

            return attachment

    return None
