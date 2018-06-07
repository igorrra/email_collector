"""Configuration module."""

import logging.config

from flask import Flask

from flaskext.mysql import MySQL


app = Flask(__name__)
app.config.from_object('config.config.Config')
mysql = MySQL()
mysql.init_app(app)
db = mysql.connect()

LOG_CONF_PATH = './config/log.conf'
ALLOWED_EXTENSIONS = {'msg', 'txt'}

logging.config.fileConfig(LOG_CONF_PATH)
logger = logging.getLogger(__name__)
