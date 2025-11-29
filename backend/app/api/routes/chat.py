
from fastapi import APIRouter

from app.api.deps import SessionDep, PDFProcessorDep
from app.api.schemas import GenerateAnswerQuery
from app.api.utils.chat_api import user_query_summarizer, create_final_answer
from app.api.utils.doc_search_query import doc_search_query


router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("/generate_answer")
async def generate_answer(
    session: SessionDep,
    processor: PDFProcessorDep,
    qenerate_answer_query: GenerateAnswerQuery
):
    summary_query = user_query_summarizer(qenerate_answer_query.query)
    docs = doc_search_query(session, summary_query, processor)
    final_result = create_final_answer(qenerate_answer_query.query, docs)

    return {'summary_query':summary_query, 'decision': final_result}
