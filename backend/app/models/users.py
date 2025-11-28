from typing import Optional

from sqlmodel import Field, SQLModel, Relationship


class BaseUser(SQLModel):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(max_length=42, unique=True)


class UserInDb(BaseUser, table=True):
    __tablename__ = "users"

    hashed_password: str
    photo_file_name: str

class UserUpload(BaseUser):
    plain_password: str
    photo_file: bytes