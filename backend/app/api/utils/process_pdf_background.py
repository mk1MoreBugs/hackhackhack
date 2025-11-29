from sqlmodel import Session
from app.core.db import get_engine
from app.services.pdf_processor import PDFProcessor

def process_pdf_background(title, doc_type, doc_number, source_url):
    """Фоновая задача для обработки PDF"""

    file_path_list = [
        'SP-54.pdf',
        'глава-4-ЖК-РФ.pdf',
        'Постановление Правительства РФ от 28.01.2006 N 47.pdf',
        'СП 255.1325800.2016.pdf'
    ]

    for file_path in file_path_list:
        with open('./app/services/baza_doc/' + file_path, "rb") as f:
            file_binary = f.read()
        # Создаем новую сессию внутри фоновой задачи
        with Session(get_engine()) as session:
            try:
                print('Обработка...')
                processor = PDFProcessor()
                document = processor.save_doc_and_embeddings_to_database(
                    session=session,
                    file_binary=file_binary,
                    title=file_path,
                    doc_type=doc_type,
                    doc_number=file_path,
                    source_url=source_url
                )
                print(f"PDF обработан: {document.title}, чанков: {len(document.chunks)}")
            except Exception as e:
                print(f"Ошибка обработки PDF: {str(e)}")
