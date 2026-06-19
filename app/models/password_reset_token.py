from sqlmodel import SQLModel, Field
from datetime import datetime

class Password_Reset_Token(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    token: str = Field(index=True)
    expires_at: datetime
    is_used: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)