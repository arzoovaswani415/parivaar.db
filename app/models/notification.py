from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from app.enums.reminder import NotificationType

class Notification(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)

    user_id: int = Field(foreign_key="user.id")
    family_member_id: int = Field(foreign_key="familymember.id")
    reminder_id: int | None = Field(default=None, foreign_key="reminder.id", nullable=True)

    message: str
    notification_type: NotificationType
    read_yn: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: "User" = Relationship(
        back_populates="notifications",
        sa_relationship_kwargs={"lazy": "selectin"}
    )
    family_member: "FamilyMember" = Relationship(
        back_populates="notifications",
        sa_relationship_kwargs={"lazy": "selectin"}
    )
    reminder: "Reminder" = Relationship()
