from pgvector.sqlalchemy import Vector
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, LargeBinary, Text
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from pydantic import BaseModel
import uuid


# Базовые классы для временных меток
class TimestampModel(SQLModel):
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# Основные модели БД
class Document(TimestampModel, table=True):
    __tablename__ = "documents"

    id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True
    )
    title: str = Field(index=True)
    doc_type: str = Field(description="Тип документа: СП, СНиП, ГОСТ, Пособие")  # СП, СНиП, ГОСТ
    doc_number: Optional[str] = Field(index=True, description="Номер документа: СП 54.13330.2016")

    # Файловая информация
    file_hash: str = Field(index=True, description="SHA256 хеш файла для отслеживания изменений")
    mime_type: str = Field(default="application/pdf")

    # Файл
    file_binary: Optional[bytes] = Field(
        sa_column=Column(LargeBinary),
        description="Бинарные данные файла (для DATABASE)"
    )
    file_content: str = Field(sa_column=Column(Text), description="Текстовая часть документа")

    # Метаданные источника
    source_url: Optional[str] = Field(description="URL источника документа")

    # Статус документа
    is_active: bool = Field(default=True, description="Активен ли документ")
    last_checked: Optional[datetime] = Field(description="Когда последний раз проверяли обновления", default_factory=datetime.utcnow)

    # Связи
    chunks: List["DocumentChunk"] = Relationship(back_populates="document")


class DocumentChunk(TimestampModel, table=True):
    __tablename__ = "document_chunks"

    id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True
    )
    document_id: uuid.UUID = Field(foreign_key="documents.id", index=True)

    # Содержимое чанка
    content: str = Field(description="Текстовая часть документа")
    chunk_index: int = Field(description="Порядковый номер чанка в документе")
    page_number: int = Field(description="Номер страницы в исходном документе")

    # Векторное представление
    embedding: Optional[Any] = Field(
        sa_type=Vector(384),  # Vector(384) для 384-мерных векторов
        description="Векторное представление текста"
    )

    # Метаданные чанка
    word_count: int = Field(description="Количество слов в чанке")

    # Связи
    document: Document = Relationship(back_populates="chunks")


# Pydantic модели для API
class DocumentCreate(SQLModel):
    title: str
    doc_type: str
    doc_number: Optional[str] = None
    file_hash: str
    source_url: Optional[str] = None
    publication_date: Optional[date] = None
    file_content: str
    file_binary: Optional[bytes] = None


class DocumentChunkCreate(SQLModel):
    title: str
    doc_type: str
    doc_number: Optional[str] = None
    file_hash: str
    source_url: Optional[str] = None
    publication_date: Optional[date] = None


class DocumentResponse(SQLModel):
    title: str
    doc_type: str
    doc_number: Optional[str] = None
    file_hash: str
    source_url: Optional[str] = None
    publication_date: Optional[date] = None
    created_at: datetime
    updated_at: datetime


class SearchQuery(SQLModel):
    query: str
    limit: int = Field(default=5, ge=1, le=20)
    min_similarity: float = Field(default=0.5, ge=0.0, le=1.0)


class SearchResult(SQLModel):
    chunk_id: uuid.UUID
    content: str
    similarity_score: float
    document_title: str
    doc_number: Optional[str]
    page_number: int


class SearchResponse(SQLModel):
    query: str
    results: List[SearchResult]
    total_found: int
    processing_time: float
