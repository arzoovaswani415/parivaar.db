from datetime import datetime
from sqlmodel import SQLModel, Field
from .family_member import FamilyMember
from sqlmodel import Relationship

class HealthRecord(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    family_member_id: int = Field(foreign_key="familymember.id")

    # vitals
    blood_pressure: str | None = None
    heart_rate: int | None = None
    weight: float | None = None
    body_temperature: float | None = None
    sugar_level: float | None = None

    # other health records
    note: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    family_member: "FamilyMember" = Relationship(back_populates="health_record")

