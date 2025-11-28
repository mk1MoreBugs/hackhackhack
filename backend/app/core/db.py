from sqlmodel import create_engine, SQLModel

import app.models
from app.core.config import settings


def get_engine(echo=False):
    return create_engine(url=str(settings.SQLALCHEMY_DATABASE_URI), echo=echo)
