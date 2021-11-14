from typing import List
from sqlmodel import SQLModel, Field, ARRAY, FLOAT, Column


class UserBase(SQLModel):
    name: str

class User(UserBase, table=True):
    id: int = Field(default=None, primary_key=True)


class PictureBase(SQLModel):
    user_id: int = Field(foreign_key="user.id")
    pic_addr: str

class Picture(PictureBase, table=True):
    id: int = Field(default=None, primary_key=True)
    encode: List[float] = Field(sa_column=Column(ARRAY(FLOAT)))
