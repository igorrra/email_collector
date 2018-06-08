from flask import Flask

from flaskext.mysql import MySQL


app = Flask(__name__)

app.config.from_object('config.config.Config')
mysql = MySQL()
mysql.init_app(app)


def with_connection(f):
    def with_connection_(*args, **kwargs):
        # or use a pool, or a factory function...
        cnn = mysql.connect()
        print cnn
        try:
            rv = f(cnn, *args, **kwargs)
            print rv
        except Exception, e:
            cnn.rollback()
            raise
        else:
            cnn.commit() # or maybe not
        finally:
            cnn.close()

        return rv

    return with_connection_
