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

import time

basedir = os.path.realpath(".")
# print("connecting...")
pg_engine = create_engine(
    "postgresql://postgres:root@localhost:5432/placements")
pg_conn = pg_engine.connect()

# pg_engine_inside = create_engine(
#     "postgresql://postgres:postgres@localhost:5433/kredo-tools-1"
# )
# pg_conn_inside = pg_engine_inside.connect()


def drop_tables():
    pg_conn.execute("DROP schema global cascade;")


def insert_rows():
    pg_conn.execute(
        """INSERT INTo global.stream(stream_name) VALUES 
        ('BSc. Hons Computer Science'),
        ('BSc. Hons ABC'),
        ('BSc. Hons DEF'),
        ('BSc. Hons GHI'),
        ('BSc. Hons JKL'),
        ('BSc. Hons MNO')
        """)


# drop_tables()
# insert_rows()
# print('Done')
