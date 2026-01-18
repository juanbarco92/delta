from typing import Optional
from sqlmodel import Field, SQLModel

class MeliCredential(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    access_token: str
    refresh_token: str
    expires_at: int
    user_id: int = Field(foreign_key="user.id")
