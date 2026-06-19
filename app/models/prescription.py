from sqlmodel import SQLModel, Field, Relationship, Column, Text
from datetime import datetime
from app.models.family_member import FamilyMember
from app.models.doctors_visit import DoctorsVisit
from typing import List

# class PrescriptionDocument(SQLModel, table=True):

#     id: int = Field(default=None, primary_key=True)
#     image_path: str = Field(default=None) # Where the file is stored on your server
#     is_verified: bool = Field(default=False)  # Becomes True when human clicks save

class PrescriptionDocument(SQLModel, table=True):

    id: int | None = Field(default=None, primary_key=True)

    family_member_id: int = Field(
        foreign_key="familymember.id"
    )

    doctor_visit_id: int = Field(
        foreign_key="doctorsvisit.id"
    )

    image_path: str
    extracted_text: str | None = Field(
        default=None,
        sa_column=Column(Text)
    )
    overall_confidence: float | None = None
    is_verified: bool = False
    uploaded_at: datetime = Field(
        default_factory=datetime.utcnow
    )

    family_member: "FamilyMember" = Relationship(back_populates="prescription_documents")
    doctors_visit: "DoctorsVisit" = Relationship(back_populates="prescription")
    prescription_medicines: list["PrescriptionMedicine"] = Relationship(back_populates="prescription_document")
    medical_history: list["MedicalHistory"] = Relationship(back_populates="prescription_document")

class PrescriptionMedicine(SQLModel, table=True):

    id: int = Field(default=None, primary_key=True)
    prescription_id: int = Field(foreign_key="prescriptiondocument.id")

    raw_text: str 

    # What the AI *thinks* it saw - ocr+ rapidfuzz
    suggested_name: str = Field(default=None)
    confidence_score: float = Field(default=None)  # Example: 0.82 (which means 82%) generated from RapidFuzz.

    # What the human actually *approved* (starts empty, filled on verification)
    final_medicine_name: str | None = None

    final_dosage: str | None = None

    final_frequency: str | None = None

    final_duration: str | None = None

    prescription_document: "PrescriptionDocument" = Relationship(
    back_populates="prescription_medicines"
)
