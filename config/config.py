[FLASK]
DEVELOPMENT = True
SECRET_KEY = 'super secret key'
SESSION_TYPE = 'filesystem'
DB_HOST = 'database'
UPLOAD_FOLDER = 'uploaded_emails'
MYSQL_DATABASE_USER = 'root'
MYSQL_DATABASE_PASSWORD = 'password'
MYSQL_DATABASE_DB = 'email_collector'
MYSQL_DATABASE_HOST = 'localhost'


[LOGGER]
[loggers]
keys=root

[handlers]
keys=FileHandler,consoleHandler

[formatters]
keys=customFormatter

[logger_root]
level=DEBUG
handlers=FileHandler,consoleHandler

[handler_FileHandler]
class=FileHandler
level=DEBUG
formatter=customFormatter
args=('email_collector.log', 'w')

[handler_consoleHandler]
class=StreamHandler
level=WARNING
formatter=customFormatter
args=(sys.stdout,)

[formatter_customFormatter]
format=%(asctime)s %(levelname)s %(name)s: %(message)s
datefmt=%m.%d.%Y %H:%M:%S
