import io
import uuid
from typing import List, Dict, Optional
from sqlmodel import Session
import pdfplumber
from sentence_transformers import SentenceTransformer
import hashlib
from app.models.documents import Document, DocumentChunk, DocumentCreate
from app.crud.documents import DocumentCRUD, DocumentChunkCRUD


class PDFProcessor:
    def __init__(self):
        self.embedding_model = SentenceTransformer('ai-forever/sbert_large_nlu_ru') # sentence-transformers/all-MiniLM-L6-v2

    def search_query(self, query:str):
        return self.embedding_model.encode([query])[0].tolist()

    # Шаг 1: Чтение PDF файла
    def read_pdf_from_binary(self, file_binary: bytes) -> tuple[str, List[Dict]]:
        """
        Читает PDF файл и возвращает текст и метаданные страниц

        Returns:
            tuple: (полный_текст, список_страниц_с_метаданными)
        """
        full_text = ""
        pages_data = []

        try:
            with pdfplumber.open(io.BytesIO(file_binary)) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    page_text = page.extract_text() or ""
                    full_text += page_text + "\n"

                    pages_data.append({
                        'page_number': page_num,
                        'text': page_text,
                        'bbox': page.bbox if page.bbox else None,
                        'width': page.width,
                        'height': page.height
                    })

        except Exception as e:
            raise Exception(f"Ошибка чтения PDF: {str(e)}")

        return full_text.strip(), pages_data

    # Шаг 2: Разбивка текста на чанки
    def split_text_into_chunks(
            self,
            text: str,
            pages_data: List[Dict],
            chunk_size: int = 500,
            overlap: int = 50
    ) -> List[Dict]:
        """
        Разбивает текст на семантические чанки с учетом границ страниц

        Args:
            text: Полный текст документа
            pages_data: Метаданные страниц
            chunk_size: Максимальное количество слов в чанке
            overlap: Перекрытие между чанками в словах

        Returns:
            List[Dict]: Список чанков с метаданными
        """
        words = text.split()
        chunks = []
        chunk_index = 0

        # Создаем маппинг позиций в тексте к номерам страниц
        page_boundaries: List[Dict] = self._create_page_boundaries(pages_data)

        i = 0
        while i < len(words):
            # Берем chunk_size слов для чанка
            chunk_words = words[i:i + chunk_size]
            chunk_text = ' '.join(chunk_words)

            if not chunk_text.strip():
                i += chunk_size - overlap
                continue

            # Определяем номер страницы для этого чанка
            start_pos = i
            page_number = self._find_page_for_position(start_pos, page_boundaries)

            chunk_data = {
                'content': chunk_text,
                'chunk_index': chunk_index,
                'page_number': page_number,
                'word_count': len(chunk_words),
                'start_position': start_pos,
                'end_position': i + len(chunk_words) - 1
            }

            chunks.append(chunk_data)
            chunk_index += 1

            # Перемещаемся с учетом overlap
            i += chunk_size - overlap

        return chunks

    def _create_page_boundaries(self, pages_data: List[Dict]) -> List[Dict]:
        """Создает границы страниц для маппинга позиций"""
        boundaries = []
        current_position = 0

        for page in pages_data:
            page_word_count = len(page['text'].split())
            boundaries.append({
                'page_number': page['page_number'],
                'start_position': current_position,
                'end_position': current_position + page_word_count - 1
            })
            current_position += page_word_count

        return boundaries

    def _find_page_for_position(self, position: int, boundaries: List[Dict]) -> int:
        """Находит номер страницы для позиции в тексте"""
        for boundary in boundaries:
            if boundary['start_position'] <= position <= boundary['end_position']:
                return boundary['page_number']
        return 1  # fallback

    # Шаг 3: Вычисление эмбеддингов
    def compute_embeddings(self, chunks: List[Dict]) -> List[Dict]:
        """
        Вычисляет эмбеддинги для всех чанков

        Args:
            chunks: Список чанков без эмбеддингов

        Returns:
            List[Dict]: Чанки с добавленными эмбеддингами
        """
        texts = [chunk['content'] for chunk in chunks]

        # Вычисляем эмбеддинги батчами для оптимизации памяти
        batch_size = 32
        embeddings = []

        for i in range(0, len(texts), batch_size):
            print(i)
            batch_texts = texts[i:i + batch_size]
            batch_embeddings = self.embedding_model.encode(batch_texts)
            embeddings.extend(batch_embeddings.tolist())

        # Добавляем эмбеддинги к чанкам
        for chunk, embedding in zip(chunks, embeddings):
            chunk['embedding'] = embedding
        print('chunks', len(chunks), 'embeddings', len(embeddings))
        return chunks

    # Шаг 4: Вычисление хеша из бинарных данных
    def compute_binary_hash(self, file_binary: bytes) -> str:
        """Вычисляет SHA256 хеш из бинарных данных"""
        sha256_hash = hashlib.sha256()
        sha256_hash.update(file_binary)
        return sha256_hash.hexdigest()

    # Шаг 5: Сохранение в базу данных
    def save_doc_and_embeddings_to_database(
            self,
            session: Session,
            file_binary: bytes,
            title: str,
            doc_type: str,
            doc_number: Optional[str] = None,
            source_url: Optional[str] = None
    ) -> Document:
        """
        Полный пайплайн: читает PDF, обрабатывает и сохраняет в БД
        """
        # Шаг 1: Чтение файла
        full_text, pages_data = self.read_pdf_from_binary(file_binary)

        # Шаг 2: Вычисление хеша
        file_hash = self.compute_binary_hash(file_binary)

        # Шаг 4: Создание документа в БД
        document_data = DocumentCreate(
            title=title,
            doc_type=doc_type,
            doc_number=doc_number,
            file_hash=file_hash,
            source_url=source_url,
            file_binary=file_binary,
            file_content=full_text
        )

        document_crud = DocumentCRUD(session)
        document = document_crud.create_document(document_data)

        # Шаг 5: Разбивка на чанки
        chunks = self.split_text_into_chunks(full_text, pages_data)

        # Шаг 6: Вычисление эмбеддингов
        chunks_with_embeddings = self.compute_embeddings(chunks)

        # Шаг 7: Сохранение чанков
        self._save_chunks_to_db(session, document.id, chunks_with_embeddings)

        return document

    def _save_chunks_to_db(
            self,
            session: Session,
            document_id: uuid.UUID,
            chunks: List[Dict]
    ):
        """Сохраняет чанки в базу данных"""

        chunk_crud = DocumentChunkCRUD(session)

        for chunk_data in chunks:
            chunk = DocumentChunk(
                document_id=document_id,
                content=chunk_data['content'],
                chunk_index=chunk_data['chunk_index'],
                page_number=chunk_data['page_number'],
                embedding=chunk_data['embedding'],
                word_count=chunk_data['word_count']
            )
            chunk_crud.create_chunk_document(chunk)
