from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime


class RefreshToken(SQLModel, table=True):
    
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    token: str 
    expires_at: datetime
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    user: "User" = Relationship(back_populates="refresh_tokens")