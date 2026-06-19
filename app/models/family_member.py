from datetime import datetime, date
from sqlmodel import SQLModel, Field, Relationship
from typing import List


class FamilyMember(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)

    user_id: int = Field(foreign_key="user.id")

    name: str
    relation: str  # self, father, mother, child
    date_of_birth: date | None = None
    gender: str | None = None
    blood_group: str | None = None

    allergies: str | None = None
    chronic_conditions: str | None = None

    is_primary: bool = Field(default=False)
    # is_primary should be true if relation is self, and there should only be one family member with relation self for each user. We can enforce this in the service layer when creating or updating family members.

    is_active: bool = Field(default=True)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime | None = None
    phone_number: str | None = None
    linked_user_id: int | None = Field(
        default=None,
        foreign_key="user.id"
    )
    emergency_contact_name: str | None = None
    emergency_contact_phone: str | None = None

    user: "User" = Relationship(back_populates="family_members")
    health_record: List["HealthRecord"] = Relationship(back_populates="family_member")
    doctors_visits: List["DoctorsVisit"] = Relationship(back_populates="family_member")
    medications: List["Medications"] = Relationship(back_populates="family_member")
    appointments: List["Appointment"] = Relationship(back_populates="family_member")
    prescription_documents: List["PrescriptionDocument"] = Relationship(
    back_populates="family_member"
)
    medical_history: List["MedicalHistory"] = Relationship(back_populates="family_member")
    vaccinations: List["Vaccination"] = Relationship(back_populates="family_member")
