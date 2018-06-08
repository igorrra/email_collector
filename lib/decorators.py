from flask import Flask

from flaskext.mysql import MySQL


app = Flask(__name__)

app.config.from_object('config.config.Config')
mysql = MySQL()
mysql.init_app(app)


def with_connection(f):
    def with_connection_(*args, **kwargs):
        db_conn = mysql.connect()
        try:
            rv = f(db_conn, *args, **kwargs)
            print rv
        except Exception, e:
            db_conn.rollback()
            raise
        else:
            db_conn.commit()
        finally:
            db_conn.close()

        return rv

    return with_connection_
