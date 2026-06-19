from datetime import datetime, date
from sqlmodel import SQLModel, Field, Relationship
from typing import List
from app.enums.medicalHistoryCategory import MedicalHistoryCategory


# Your models/medical_history.py file should split its data into four clear, easy-to-read categories:📑 List Layout
# Chronic Conditions: Long-term issues like Diabetes, Asthma, or Hypertension (pulled automatically from doctors_visit).
# Allergies: Dangerous triggers like Peanut allergies or Penicillin sensitivity (critical for the prescription OCR to check against!).
# Surgeries & Hospitalizations: Past operations and dates.
# Family Medical History: Genetic conditions (e.g., "Father had heart disease"). This is the only section the user should type manually during onboarding.
# Vaccination History: Record of vaccines received, including dates and next due dates.

class MedicalHistory(SQLModel, table=True):

    id: int | None = Field(default=None, primary_key=True)

    family_member_id: int = Field(
        foreign_key="familymember.id"
    )

    category: MedicalHistoryCategory = Field(
        sa_column_kwargs={"nullable": False}
    )
    # CHRONIC_CONDITION
    # ALLERGY
    # SURGERY
    # FAMILY_HISTORY
    # VACCINATION

    # sa_column_kwargs means that the column is not nullable in the database, ensuring that every record has a category assigned.

    title: str

    description: str | None = None

    diagnosed_on: date | None = None

    source: str = "MANUAL"
    # MANUAL
    # DOCTOR_VISIT - ex: type 2 diabetes, asthma, hypertension, etc. diagnosed by a doctor during a visit
    # PRESCRIPTION - ex: prescription for penicillin, amoxicillin, etc. that indicates an allergy

    linked_visit_id: int | None = Field(
        default=None,
        foreign_key="doctorsvisit.id"
    )

    linked_prescription_id: int | None = Field(
        default=None,
        foreign_key="prescriptiondocument.id"
    )

    is_confirmed: bool = Field(
        default=True
    )

    created_at: datetime = Field(
        default_factory=datetime.utcnow
    )
    family_member: "FamilyMember" = Relationship(back_populates="medical_history")
    doctors_visit: "DoctorsVisit" = Relationship(back_populates="medical_history")
    prescription_document: "PrescriptionDocument" = Relationship(back_populates="medical_history")
   
    # examples - Medical History in frontend

    # ▼ Chronic Conditions
    #     Diabetes
    #     Asthma

    # ▼ Allergies
    #     Penicillin

    # ▼ Surgeries
    #     Appendix Removal

    # ▼ Family History
    #    Heart Disease

    # ▼ Vaccinations
    #     COVID
    #     Flu