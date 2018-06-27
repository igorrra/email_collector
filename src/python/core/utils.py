"""Application utils."""


def db_connection_wrapper(func):
    """Database connection decorator"""
    def new_func(connection, *args, **kwargs):
        """Return new decorated function."""
        try:
            value = func(connection, *args, **kwargs)
        except Exception as error:
            connection.rollback()
            return str(error.args[-1]), 500
        else:
            connection.commit()
        finally:
            connection.close()
        return value

    return new_func
