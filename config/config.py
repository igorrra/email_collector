"""Flask application config class."""


class Config(object):
    """Flask application configuration"""
    DEVELOPMENT = True
    SECRET_KEY = 'super secret key'
    SESSION_TYPE = 'filesystem'
    DB_HOST = 'database'
    UPLOAD_FOLDER = 'uploaded_emails'
    MYSQL_DATABASE_USER = 'root'
    MYSQL_DATABASE_PASSWORD = 'password'
    MYSQL_DATABASE_DB = 'email_collector'
    MYSQL_DATABASE_HOST = 'localhost'
