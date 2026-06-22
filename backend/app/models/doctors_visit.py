from sqlmodel import SQLModel, Field, Relationship
from datetime import date

class DoctorsVisit(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    family_member_id: int = Field(foreign_key="familymember.id")
   
    doctor_name: str
    hospital_name: str
    visit_date: date
    diagnosis: str | None = None
    notes: str | None = None
    follow_up_date: date | None = None

    family_member: "FamilyMember" = Relationship(back_populates="doctors_visits")
    prescription: "PrescriptionDocument" = Relationship(back_populates="doctors_visit"
)
    medical_history: "MedicalHistory" = Relationship(back_populates="doctors_visit")

