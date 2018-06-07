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
        try:
            rv = f(cnn, *args, **kwargs)
        except Exception, e:
            cnn.rollback()
            raise
        else:
            cnn.commit() # or maybe not
        finally:
            cnn.close()

        return rv

    return with_connection_


@with_connection
def do_some_job(cnn, arg1, arg2=None):
    cur = cnn.cursor()
    cur.execute('SELECT 1+1;', (arg1, arg2)) # or something else


def main():
    cnn = mysql.connect()
    do_some_job(cnn, arg2='hi')


if __name__ == '__main__':
    main()
