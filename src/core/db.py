import databases
import sqlalchemy

import ormar

from src.config import settings

database = databases.Database(settings.DATABASE_URL)
metadata = sqlalchemy.MetaData()


class BaseMeta(ormar.ModelMeta):
    database = database
    metadata = metadata
