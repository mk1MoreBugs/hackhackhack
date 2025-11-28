from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import SessionDep
from app.core.config import settings
from app.core.security import authenticate_user, create_access_token
from app.models.responses import UnauthorizedMessage
from app.models.tokens import Token


router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


@router.post(
    path="/login",
    response_model= Token,
    responses={401: {"model": UnauthorizedMessage}},
)
async def login(session: SessionDep, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token | HTTPException:
    user = authenticate_user(session=session, username=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token_data = {"sub": user.username}
    access_token = create_access_token(data=access_token_data, expires_delta=access_token_expires)

    return Token(access_token=access_token, token_type="bearer")
