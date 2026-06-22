from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from app.enums.appointmentStatus import AppointmentStatus

class Appointment(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)

    family_member_id: int = Field(foreign_key="familymember.id")

    doctor_name: str

    appointment_date: datetime

    purpose: str

    status: AppointmentStatus
    # Scheduled
    # Completed
    # Cancelled

    family_member: "FamilyMember" = Relationship(back_populates="appointments")
    #relation between doctors visit and appointment is one to one. A doctors visit can have only one appointment and an appointment can have only one doctors visit. We can enforce this in the service layer when creating or updating doctors visits and appointments.