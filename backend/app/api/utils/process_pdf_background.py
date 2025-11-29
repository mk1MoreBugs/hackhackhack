from sqlmodel import Session
from app.core.db import get_engine
from app.services.pdf_processor import PDFProcessor

def process_pdf_background(title, doc_type, doc_number, source_url):
    """Фоновая задача для обработки PDF"""
    print(4)

    file_path = './app/services/SP-54.pdf'
    with open(file_path, "rb") as f:
        file_binary = f.read()

    print(5)

    # Создаем новую сессию внутри фоновой задачи
    with Session(get_engine()) as session:
        try:
            print('Обработка...')
            processor = PDFProcessor()
            document = processor.save_doc_and_embeddings_to_database(
                session=session,
                file_binary=file_binary,
                title=title,
                doc_type=doc_type,
                doc_number=doc_number,
                source_url=source_url
            )
            print(f"PDF обработан: {document.title}, чанков: {len(document.chunks)}")
        except Exception as e:
            print(f"Ошибка обработки PDF: {str(e)}")