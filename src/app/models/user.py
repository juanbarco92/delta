from typing import Optional
from sqlmodel import Field, SQLModel

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True)
    meli_user_id: int = Field(unique=True, index=True)
    is_active: bool = Field(default=True)
