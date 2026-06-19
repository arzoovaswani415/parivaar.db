from datetime import date
from sqlmodel import SQLModel, Field, Relationship

class Vaccination(SQLModel, table=True):

    id: int | None = Field(default=None, primary_key=True)

    family_member_id: int = Field(
        foreign_key="familymember.id"
    )

    vaccine_name: str

    administered_on: date

    next_due_date: date | None = None

    notes: str | None = None

    family_member: "FamilyMember" = Relationship(back_populates="vaccinations")