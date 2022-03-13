import json

from sqlalchemy import create_engine, MetaData
from sqlalchemy.schema import CreateSchema
from sqlalchemy.orm import sessionmaker
from databases import Database

from api.db import global_metadata

with open("api/config.json") as config_file:
    config = json.loads(config_file.read())


DATABASE_BASE_URL = f"postgresql://{config['DATABASES']['PLACEMENTS']['user']}:{config['DATABASES']['PLACEMENTS']['password']}@{config['DATABASES']['PLACEMENTS']['host']}:{config['DATABASES']['PLACEMENTS']['port']}"
DATABASE_URL = f'{DATABASE_BASE_URL}/{config["DATABASES"]["PLACEMENTS"]["database"]}'
database = Database(DATABASE_URL)
engine = create_engine(DATABASE_URL)
if not engine.dialect.has_schema(engine, 'global'):
    engine.execute(CreateSchema('global'))

Session = sessionmaker(bind=engine)
session = Session()

global_metadata.create_all(engine)
