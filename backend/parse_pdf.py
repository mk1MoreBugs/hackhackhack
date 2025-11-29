from sqlalchemy import text

from app.api.utils.process_pdf_background import process_pdf_background
from sqlmodel import SQLModel, Session
import app.models.documents
from app.core.db import get_engine


def main():
    print('back startup')


    SQLModel.metadata.drop_all(get_engine())
    SQLModel.metadata.create_all(get_engine())

    # Запускаем обработку
    process_pdf_background('title', 'СНиП', 'СНиП №', 'example.com')

    print("Ожидание завершения обработки...")

    print("Скрипт завершен")

if __name__ == "__main__":
    main()
