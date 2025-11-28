from pydantic import BaseModel


class DetailMessage(BaseModel):
    detail: str

class UnauthorizedMessage(BaseModel):
    detail: str