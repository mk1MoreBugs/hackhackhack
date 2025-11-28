from fastapi import HTTPException, status

from app.core.security import decode_jwt_token
from app.models.tokens import TokenData


def get_token_data_or_raise_exception(token: str) -> TokenData | None:
    token_data: TokenData | None = decode_jwt_token(token=token)
    if token_data is None:
        __raise_unauthorized_exception()
    return token_data


def check_token_data(token: str) -> None:
    if not is_correct_token_data(token=token):
        __raise_unauthorized_exception()


def __raise_unauthorized_exception():
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


def is_correct_token_data(token: str) -> bool:
    token_data: TokenData | None = decode_jwt_token(token=token)
    if token_data is None:
        return False
    else:
        return True
