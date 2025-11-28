from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError

from app.api.deps import reusable_oauth2, SessionDep
from app.api.utils.token_utils import get_token_data_or_raise_exception
from app.core.security import decode_jwt_token, get_password_hash
from app.models.responses import DetailMessage, UnauthorizedMessage
from app.models.tokens import TokenData
from app.models.users import UserUpload, UserInDb
from app.crud import users


router = APIRouter(
    prefix="/users",
    tags = ["users"],
)


@router.get(
    path="/me",
    response_model=TokenData,
    responses={401: {"model": UnauthorizedMessage}},
)
async def get_user_info(token: Annotated[str, Depends(reusable_oauth2)]) -> TokenData:
    return get_token_data_or_raise_exception(token=token)


@router.post(
    path="/create",
    status_code=status.HTTP_201_CREATED,
    response_model=dict[str, str],
    responses={409: {"model": DetailMessage}},
)
async def create_user(session: SessionDep, user_upload: UserUpload) -> dict[str, str]:
    users_for_write_db = UserInDb(
        **dict(user_upload),
        hashed_password=get_password_hash(password=user_upload.plain_password),
        photo_file_name="path/to/file"
    )
    try:
        users.create_user(session=session, user=users_for_write_db)
        return {"status": "created"}

    except IntegrityError:
        raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="username already exists",
        )
