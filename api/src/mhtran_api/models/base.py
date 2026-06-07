# api/src/mhtran_api/models/base.py
# Role: shared declarative base for ORM models
# Author: Dennies Bor

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass