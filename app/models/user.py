from typing import  List
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)

    name: str
    email: str = Field(index=True, unique=True)
    password_hash: str
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime | None = None
    invite_code: str | None = Field(
        default=None,
        unique=True
    )


    family_members: List["FamilyMember"] = Relationship(back_populates="user")
    # This line is used within an SQLModel (or SQLAlchemy) class to define a Relationship between two database tables. It doesn’t create a column in the database itself; instead, it acts as a "shortcut" for Python to pull related data.
    # In this case, it indicates that a User can have multiple FamilyMembers associated with it. The back_populates="user" part tells SQLModel that the FamilyMember class will have a corresponding relationship back to the User class, allowing for easy access to related data in both directions.

    refresh_tokens: List["RefreshToken"] = Relationship(back_populates="user")
    # Similar to the family_members relationship, this line indicates that a User can have multiple RefreshTokens associated with it. The back_populates="user" part tells SQLModel that the RefreshToken class will have a corresponding relationship back to the User class, allowing for easy access to related data in both directions. This is useful for managing user sessions and authentication in the application.