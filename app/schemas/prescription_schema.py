from pydantic import BaseModel

class VerifiedMedicine(BaseModel):
    medicine_name: str
    dosage: str
    frequency: str
    duration: str


class PrescriptionVerificationRequest(BaseModel):
    medicines: list[VerifiedMedicine]