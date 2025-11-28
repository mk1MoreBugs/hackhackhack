from datetime import datetime, timedelta, timezone
import bcrypt
import jwt
from jwt.exceptions import InvalidTokenError

from app.api.deps import SessionDep
from app.core.config import settings
from app.crud.users import get_user_by_username
from app.models.users import UserInDb
from app.models.tokens import TokenData


ALGORITHM = "HS256"

def create_access_token(data: dict, expires_delta: timedelta) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    plain_password_bytes = __string_to_bytes(plain_password)
    hashed_password_bytes = __string_to_bytes(hashed_password)
    return bcrypt.checkpw(plain_password_bytes, hashed_password_bytes)


def get_password_hash(password: str) -> str:
    password_bytes = __string_to_bytes(password)
    # Generate a salt and hash the password
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password_bytes, salt)
    return __bytes_to_string(hashed_password)


def authenticate_user(session: SessionDep, username: str, password: str) -> UserInDb | None:
    user = get_user_by_username(session=session, username=username)
    if user is None:
        return None
    if not verify_password(plain_password=password, hashed_password=user.hashed_password):
        return None
    return user


def decode_jwt_token(token: str) -> TokenData | None:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
        return TokenData(username=username)
    except InvalidTokenError:
        return None


def __string_to_bytes(string: str) -> bytes:
    return string.encode('utf-8')


def __bytes_to_string(str_bytes: bytes) -> str:
    return str_bytes.decode('utf-8')
