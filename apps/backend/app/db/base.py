# START_MODULE_CONTRACT
#   PURPOSE: SQLAlchemy declarative base shared by all ORM models.
#   SCOPE: Metadata and naming conventions for Alembic.
#   DEPENDS: none
#   LINKS: M-DB, V-M-DB
# END_MODULE_CONTRACT
#
# START_MODULE_MAP
#   NAMING_CONVENTION - constraint naming convention for Alembic
#   Base              - declarative base
# END_MODULE_MAP
from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase

NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)
