from sqlmodel import SQLModel, Field, Relationship

class Medications(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    family_member_id: int = Field(foreign_key="familymember.id")

    medicine_name: str
    dosage: str | None = None
    frequency: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    notes: str | None = None
    
    

    family_member: "FamilyMember" = Relationship(back_populates="medications")