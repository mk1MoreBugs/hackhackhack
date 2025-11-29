from sqlalchemy import text
from sqlmodel import create_engine, SQLModel

import app.models
from app.core.config import settings


def get_engine(echo=False):
    engine = create_engine(url=str(settings.SQLALCHEMY_DATABASE_URI), echo=echo)
    # Получаем сырое соединение из engine
    with engine.connect() as conn:
        conn.execute(text('CREATE EXTENSION IF NOT EXISTS vector'))
        conn.commit()

        print("✅ Расширение vector включено")
    return engine
