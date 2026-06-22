from datetime import datetime,timezone , time
# pyrefly: ignore [missing-import]
from sqlmodel import SQLModel, Field, Relationship
from app.enums.reminder import ReminderType, ReminderFrequency, ReminderStatus

class Reminder(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)

    family_member_id: int = Field(foreign_key="familymember.id")

    title: str
    description: str | None = None
    type: ReminderType
    frequency: ReminderFrequency
    time_of_day:time   # Format: "HH:MM" in UTC
    start_date: datetime = Field(
        default_factory=datetime.now
    )
    next_trigger_at: datetime = Field(
        default_factory=datetime.now
    )
    last_triggered_at: datetime | None = None
    status: ReminderStatus = Field(default=ReminderStatus.PENDING)
    active_yn: bool = Field(default=True)

    created_at: datetime = Field(
        default_factory=datetime.now
    )
    updated_at: datetime | None = None

    # Relationship to FamilyMember
    family_member: "FamilyMember" = Relationship(
        back_populates="reminders",
        sa_relationship_kwargs={"lazy": "selectin"}
    )
