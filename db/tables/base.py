from sqlalchemy import MetaData
from sqlalchemy.ext.declarative import declarative_base

meta = MetaData(
    naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }
)

# The function declarative_base() returns a class which is used to create database tables.
# docs: https://fastapi.tiangolo.com/tutorial/sql-databases/#create-a-base-class
BaseTable = declarative_base(metadata=meta)  # type: ignore
