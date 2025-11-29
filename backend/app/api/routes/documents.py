from typing import Optional

from fastapi import APIRouter


from starlette.responses import JSONResponse

from app.api.deps import SessionDep
from app.crud.documents import DocumentChunkCRUD
from app.models.documents import SearchQuery
from app.services.pdf_processor import PDFProcessor

router = APIRouter(prefix="/api/docs", tags=["docs"])


@router.get("/parse_docs")
async def parse_docs(
   # session: SessionDep,
   # background_tasks: BackgroundTasks,
):
    # file_path = './app/services/SP-54.pdf'
    # with open(file_path, "rb") as f:
    #     file_binary = f.read()
    #     # Добавляем задачу в фон
    # background_tasks.add_task(
    #     process_pdf_background,
    #     'title', 'СНиП', 'СНиП №', 'example.com'
    # )

    print(333)

    return JSONResponse(
        status_code=202,
        content={
            "message": "Обработка PDF начата в фоновом режиме",
            "status": "processing"
        }
    )


@router.post("/search_query")
async def search_query(
    session: SessionDep,
    search: SearchQuery
):
    processor = PDFProcessor()
    query_embedding = processor.search_query(search.query)
    print(query_embedding)

    document_crud = DocumentChunkCRUD(session)
    result = document_crud.search_similar_chunks_sqlmodel(query_embedding)

    return result
