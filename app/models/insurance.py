from datetime import datetime, date

from sqlmodel import SQLModel, Field, Relationship


class Insurance(SQLModel, table=True):

    id: int | None = Field(
        default=None,
        primary_key=True
    )

    family_member_id: int = Field(
        foreign_key="familymember.id"
    )

    insurance_company_name: str

    policy_number: str = Field(
        unique=True
    )

    policy_holder_name: str

    coverage_amount: float

    start_date: date

    expiry_date: date

    notes: str | None = None

    is_active: bool = Field(
        default=True
    )

    created_at: datetime = Field(
        default_factory=datetime.utcnow
    )

    updated_at: datetime | None = None

    family_member: "FamilyMember" = Relationship(
        back_populates="insurances"
    )