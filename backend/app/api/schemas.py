from pydantic import BaseModel


class UploadFileMeta(BaseModel):
    title: str
    doc_type: str
    doc_number: str = None
    source_url: str = None

class GenerateAnswerQuery(BaseModel):
    query: str
