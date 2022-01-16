#

import os
import logging
from time import time, sleep
import psycopg2

CHECK_TIMEOUT_SEC = 30
CHECK_INTERVAL_SEC = 1

db_config = {
    'dbname': os.getenv('SQL_DATABASE', ''),
    'user': os.getenv('SQL_USER', ''),
    'password': os.getenv('SQL_PASSWORD', ''),
    'host': os.getenv('SQL_HOST', 'db'),
}

logger = logging.getLoger()
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())

start_time = time()


def pg_isready(host, user, password, dbname):
    while time() - start_time < CHECK_TIMEOUT_SEC:
        try:
            conn = psycopg2.connect(**vars())
            conn.close()
            logger.info('Postgres is ready!')
            return True
        except psycopg2.OperationalError:
            logger.info(f'Postgrs is\'nt ready. Waiting for {CHECK_INTERVAL_SEC} second(s)')
            sleep(CHECK_INTERVAL_SEC)

    logger.error(f'We could not connect to Postgres within {CHECK_TIMEOUT_SEC} seconds.')
    return False


pg_isready(**db_config)
