"""
Parse email module.
Return the necessary email attributes:
from, to, subject, timestamp, body, html, attachments
"""

import hashlib
import os
import re
import time
import uuid
from StringIO import StringIO
from email.utils import parseaddr

import dateutil.parser
from email.Header import decode_header

import email

ATT_TEMPLATE = '%s/%s'
ATT_PATH = 'attachments/'
ADDR_FIELDS = ['To', 'Cc', 'Bcc']


class NotSupportedMailFormat(Exception):
    """
    NotSupportedMailFormat exception is raised when
    unsupported email file contents received.
    """
    def __init__(self, custom_message):
        msg = '%s' % (custom_message, )
        Exception.__init__(self, msg)


def parse_raw_email(path):
    """Parse raw email file (RFC 822).

    Get and return email attributes and file attachments."""
    try:
        with open(path, 'r') as work_file:
            msgobj = email.message_from_file(work_file)
            if 'MIME-Version' not in msgobj:
                raise NotSupportedMailFormat(
                    'Unsupported email content received'
                )

        subject, timestamp, recipients = parse_header(msgobj)
        attachments, body, html = parse_content(msgobj)

        return {
            'subject': subject,
            'timestamp': timestamp,
            'body': body,
            'html': html,
            'from': parseaddr(msgobj.get('From'))[1],
            'to': recipients,
            'attachments': attachments
        }

    except NotSupportedMailFormat:
        print 'Not supported email format'
        return None


def parse_header(msgobj):
    """Parse email header.

    Return subject, timestamp and recipients."""
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

    recipients = []
    for address in ADDR_FIELDS:
        if msgobj.get(address):
            recipient = re.findall(
                r'[\w\.,]+@[\w\.,]+\.\w+', msgobj.get(address)
            )
            for item in recipient:
                recipients.append(item)
    return subject, timestamp, recipients


def parse_content(msgobj):
    """Parse email content.

    Return attachments, body, html."""
    attachments = parse_attachments(msgobj)
    body = None
    html = None

    for part in msgobj.walk():
        if part.get_content_type() == 'text/plain':
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

    return attachments, body, html


def parse_attachments(msgobj):
    """Get and decode file attachments.

    Save attachments to corresponding files."""
    u_id = str(uuid.uuid4())
    if not os.path.exists(ATT_PATH):
        os.mkdir(ATT_PATH)
    if not os.path.exists(ATT_PATH + u_id):
        os.mkdir(ATT_PATH + u_id)

    attachments = []

    for part in msgobj.walk():

        content_disposition = part.get('Content-Disposition')

        if content_disposition:
            dispositions = content_disposition.strip().split(";")
            if bool(content_disposition
                    and "attachment" in dispositions[0].lower()):

                file_data = part.get_payload(decode=True)
                attachment = StringIO(file_data)
                attachment.content_type = part.get_content_type()
                attachment.name = None
                attachment.path = None
                attachment.md5 = None

                for param in dispositions[1:]:
                    name, value = param.split('=')
                    name = name.lower()

                    if 'filename' in name:
                        attachment.name = value.replace('"', '')
                        file_path = ATT_TEMPLATE % (ATT_PATH + u_id, attachment.name)
                        with open(file_path, 'wb') as destination_file:
                            destination_file.write(file_data)
                        attachment.path = file_path
                        md5_obj = hashlib.md5()
                        md5_obj.update(file_data)
                        attachment.md5 = md5_obj.hexdigest()
                        attachments.append(attachment)
    return attachments
