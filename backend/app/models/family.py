from datetime import datetime
from typing import List

from sqlmodel import SQLModel, Field, Relationship


class Family(SQLModel, table=True):

    id: int | None = Field(
        default=None,
        primary_key=True
    )

    family_name: str

    family_code: str = Field(
        unique=True,
        index=True
    )

    owner_user_id: int = Field(
        foreign_key="user.id"
    )

    is_active: bool = Field(
        default=True
    )

    created_at: datetime = Field(
        default_factory=datetime.utcnow
    )

    updated_at: datetime | None = None

    # Relationships

    users: List["User"] = Relationship(
        back_populates="family",
        sa_relationship_kwargs={"foreign_keys": "[User.family_id]"}
    )

    family_members: List["FamilyMember"] = Relationship(
        back_populates="family",
        sa_relationship_kwargs={"lazy": "selectin"}
    )