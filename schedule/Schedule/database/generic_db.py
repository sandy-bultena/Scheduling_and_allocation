"""Access to a generic db without relying on db specifications. Intended for use in decoupling"""
from .PonyDatabaseConnection import *
from .db_constants import *

REQUIRES_LOGIN = True

if PROVIDER.lower() == 'sqlite':
    REQUIRES_LOGIN = False


def create_db(name=DB_NAME) -> Database:
    """Creates a DB and returns the object"""
    try:
        if PROVIDER.lower() == "sqlite":
            return define_database(provider=PROVIDER, filename=name, create_db=CREATE_DB)
        elif PROVIDER.lower() == "mysql":
            return define_database(host=HOST, passwd=PASSWD, db=name, provider=PROVIDER, user=USERNAME)
    # DB already exists
    except BindingError:
        return db
