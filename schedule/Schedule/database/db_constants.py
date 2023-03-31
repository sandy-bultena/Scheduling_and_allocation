""" Database connection constants """
from dotenv import dotenv_values

info = dotenv_values()

if 'DB_NAME' not in info or \
        'HOST' not in info or \
        'USERNAME' not in info or \
        'PASSWD' not in info or \
        'PROVIDER' not in info:
    raise ConnectionError("Required connection information not found in .env file")

DB_NAME = info['DB_NAME']
HOST = info['HOST']
USERNAME = info['USERNAME']
PASSWD = info['PASSWD']
PROVIDER = info['PROVIDER']