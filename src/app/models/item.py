from typing import Optional
from sqlmodel import Field, SQLModel

class Item(SQLModel, table=True):
    id: str = Field(primary_key=True, description="MeLi Item ID (e.g., MLA12345)")
    user_id: int = Field(foreign_key="user.id", index=True)
    title: str
    price: float
    permalink: str
    thumbnail: Optional[str] = None
    status: str
    official_store_id: Optional[int] = None
    dimensions: Optional[str] = None
