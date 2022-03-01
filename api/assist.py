import os
from sqlalchemy import create_engine
from sqlalchemy import (
    MetaData,
    Table,
    Column,
    Integer,
    String,
    Boolean,
    Numeric,
    DateTime,
    text,
)
from sqlalchemy import select
from sqlalchemy import or_

from datetime import datetime
from sqlalchemy.sql import func
import  json
import time

basedir = os.path.realpath(".")
# print("connecting...")
# pg_engine = create_engine(
#     "postgresql://postgres:root@localhost:5432/placements")
# pg_conn = pg_engine.connect()

with open("api/config.json") as config_file:
    config = json.loads(config_file.read())

DATABASE_BASE_URL = f"postgresql://{config['DATABASES']['PLACEMENTS_PROD']['user']}:{config['DATABASES']['PLACEMENTS_PROD']['password']}@{config['DATABASES']['PLACEMENTS_PROD']['host']}:{config['DATABASES']['PLACEMENTS_PROD']['port']}"
DATABASE_URL = f'{DATABASE_BASE_URL}/{config["DATABASES"]["PLACEMENTS_PROD"]["database"]}'

pg_engine = create_engine(DATABASE_URL)
pg_conn = pg_engine.connect()

# pg_engine_inside = create_engine(
#     "postgresql://postgres:postgres@localhost:5433/kredo-tools-1"
# )
# pg_conn_inside = pg_engine_inside.connect()


def drop_tables():
    pg_conn.execute("DROP schema global cascade;")


def insert_rows():
    pg_conn.execute(
        """INSERT INTO global.stream(stream_name) VALUES 
        ('BSc. Hons Computer Science'),
        ('BCOM Hons.'),
        ('BSc. Hons Mathematics'),
        ('BSc. Hons Physics'),
        ('BSc. Hons Chemistry'),
        ('Bachelors of  Management Studies')
        """)


# drop_tables()
# insert_rows()
# print('Done')
