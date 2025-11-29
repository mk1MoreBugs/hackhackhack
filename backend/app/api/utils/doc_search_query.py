from sqlmodel import Session

from app.crud.documents import DocumentChunkCRUD
from app.services.pdf_processor import PDFProcessor


def doc_search_query(session: Session, query: str, processor: PDFProcessor):
    query_embedding = processor.search_query(query)

    document_crud = DocumentChunkCRUD(session)
    result = document_crud.search_similar_chunks_sqlmodel(query_embedding)
    return result
