from sqlmodel import Session, select, update, and_, desc
from datetime import datetime


from sqlalchemy import Update, func
from typing import List, Optional
import uuid
from app.models.documents import Document, DocumentChunk, DocumentCreate, DocumentResponse


class DocumentCRUD:
    def __init__(self, session: Session):
        self.session = session

    # CREATE операции
    def create_document(self, document_data: DocumentCreate) -> Document:
        """Создает новый документ"""
        document_data = Document(**document_data.model_dump())
        self.session.add(document_data)
        self.session.commit()
        self.session.refresh(document_data)
        return document_data

    # READ операции
    def get_document_by_title(self, title: str) -> Optional[Document]:
        """Получает документ по точному совпадению title"""
        statement = select(Document).where(Document.title == title)
        return self.session.exec(statement).first()

    def get_documents_by_title_like(self, title_pattern: str) -> List[Document]:
        """Ищет документы по частичному совпадению title"""
        statement = select(Document).where(Document.title.ilike(f"%{title_pattern}%"))
        return list(self.session.exec(statement).all())

    def get_documents_by_type(self, doc_type: str) -> List[Document]:
        """Получает документы по типу"""
        statement = select(Document).where(Document.doc_type == doc_type)
        return list(self.session.exec(statement).all())

    # UPDATE операции
    def update_document_by_title(self, title: str, update_data: dict) -> Optional[Document]:
        """Обновляет документ по title"""
        document = self.get_document_by_title(title)
        if not document:
            return None

        for key, value in update_data.items():
            if hasattr(document, key):
                setattr(document, key, value)

        document.updated_at = datetime.now()
        self.session.add(document)
        self.session.commit()
        self.session.refresh(document)
        return document

    # DELETE операции
    def delete_document_by_title(self, title: str) -> bool:
        """Удаляет документ по title"""
        document = self.get_document_by_title(title)
        if not document:
            return False

        self.session.delete(document)
        self.session.commit()
        return True


class DocumentChunkCRUD:
    def __init__(self, session: Session):
        self.session = session

    def create_chunk_document(self, chunk_data: DocumentChunk) -> DocumentChunk:
        """Создает новый чанк"""
        self.session.add(chunk_data)
        self.session.commit()
        self.session.refresh(chunk_data)
        return chunk_data

    def get_chunks_by_document_title(self, title: str) -> List[DocumentChunk]:
        """Получает все чанки документа по его title"""
        statement = select(DocumentChunk).join(Document).where(Document.title == title)
        return list(self.session.exec(statement).all())

    def get_chunks_by_document_id(self, document_id: uuid.UUID) -> List[DocumentChunk]:
        """Получает все чанки документа по его ID"""
        statement = select(DocumentChunk).where(DocumentChunk.document_id == document_id)
        return list(self.session.exec(statement).all())

    def delete_chunks_by_document_title(self, title: str) -> int:
        """Удаляет все чанки документа по его title"""
        chunks = self.get_chunks_by_document_title(title)

        count = 0
        for chunk in chunks:
            self.session.delete(chunk)
            count += 1

        self.session.commit()
        return count


    def search_similar_chunks_sqlmodel(
            self,
            query_embedding: List[float],
            limit: int = 5,
            min_similarity: float = 0.5,
            doc_type: Optional[str] = None
    ) -> List[dict]:
        """
        Семантический поиск чанков с использованием SQLModel
        """
        statement = (
            select(
                DocumentChunk.id,
                DocumentChunk.content,
                DocumentChunk.page_number,
                Document.title.label("document_title"),
                Document.doc_number,
                (1.0 - DocumentChunk.embedding.cosine_distance(query_embedding)).label("similarity")
            )
            .join(Document)
            .order_by((1.0 - DocumentChunk.embedding.cosine_distance(query_embedding)).desc())
            .limit(limit)
        )
        print(statement)
        results = self.session.exec(statement).all()

        return [
            {
                "id": row.id,
                "content": row.content,
                "page_number": row.page_number,
                "document_title": row.document_title,
                "doc_number": row.doc_number,
                "similarity": float(row.similarity)
            }
            for row in results if float(row.similarity) <= min_similarity
        ]
