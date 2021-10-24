from typing import List
from sqlmodel import SQLModel, Field, ARRAY, FLOAT, Column


class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str

class Picture(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    encode: List[float] = Field(sa_column=Column(ARRAY(FLOAT)))
    pic_addr: str

