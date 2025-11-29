from collections.abc import Generator
from typing import Annotated

from fastapi import Depends
from sqlmodel import Session

from app.api.utils.CustomOAuth2PasswordBearer import CustomOAuth2PasswordBearer
from app.core.config import settings
from app.core.db import get_engine
from app.services.pdf_processor import PDFProcessor

reusable_oauth2 = CustomOAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login"
)

def get_db() -> Generator[Session, None, None]:
    with Session(get_engine()) as session:
        yield session

def get_processor():
    return PDFProcessor()

SessionDep = Annotated[Session, Depends(get_db)]

TokenDep = Annotated[str, Depends(reusable_oauth2)]

PDFProcessorDep = Annotated[PDFProcessor, Depends(get_processor)]
