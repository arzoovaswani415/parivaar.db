import os
import uuid

import easyocr

from fastapi import UploadFile
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.prescription import (
    PrescriptionDocument,
    PrescriptionMedicine
)

from app.utility.fuzzy_matcher import (
    find_best_medicine_match
)
from app.schemas.prescription_schema import PrescriptionVerificationRequest , VerifiedMedicine
from app.models.family_member import FamilyMember
from app.models.user import User
from fastapi import HTTPException
from app.dependency import get_current_user
from sqlmodel import select
from app.database import get_session

from app.service.family_member_service import get_family_member_by_id
from app.models.medications import Medications




UPLOAD_FOLDER = "uploads/prescriptions"

reader = None

def get_reader():
    global reader

    if reader is None:
        reader = easyocr.Reader(["en"])

    return reader


async def upload_prescription_service(
    family_member_id: int,
    doctor_visit_id: int,
    file: UploadFile,
    session: AsyncSession
):

    os.makedirs(
        UPLOAD_FOLDER,
        exist_ok=True
    )

    # --------------------------------------------------
    # 1. Save Image
    # --------------------------------------------------

    extension = file.filename.split(".")[-1]

    filename = (
        f"{uuid.uuid4()}.{extension}"
    )

    file_path = os.path.join(
        UPLOAD_FOLDER,
        filename
    )

    contents = await file.read()

    with open(file_path, "wb") as f:
        f.write(contents)

    # --------------------------------------------------
    # 2. OCR
    # --------------------------------------------------

    ocr_results = get_reader().readtext(file_path)

    extracted_lines = []

    confidence_scores = []

    for result in ocr_results:

        text = result[1]

        confidence = result[2]

        extracted_lines.append(text)

        confidence_scores.append(
            confidence
        )

    extracted_text = "\n".join(
        extracted_lines
    )

    overall_confidence = (
        sum(confidence_scores)
        / len(confidence_scores)
        if confidence_scores
        else 0
    )

    # --------------------------------------------------
    # 3. Create Prescription Document
    # --------------------------------------------------

    prescription = PrescriptionDocument(
        family_member_id=family_member_id,
        doctor_visit_id=doctor_visit_id,
        image_path=file_path,
        extracted_text=extracted_text,
        overall_confidence=round(
            overall_confidence * 100,
            2
        ),
        is_verified=False
    )

    session.add(prescription)

    await session.commit()

    await session.refresh(
        prescription
    )

    # --------------------------------------------------
    # 4. Fuzzy Matching
    # --------------------------------------------------

    candidate_lines = []

    current_line = ""

    for line in extracted_lines:

        clean_line = line.strip()

        if not clean_line:
            continue

        if clean_line.lower().startswith(
            (
                "syp",
                "tab",
                "tablet",
                "cap",
                "capsule",
                "inj",
                "drops"
            )
        ):

            if current_line:
                candidate_lines.append(current_line)

            current_line = clean_line

        elif current_line:

            current_line += " " + clean_line

        else:
            candidate_lines.append(clean_line)

    if current_line:
        candidate_lines.append(current_line)

    # --------------------------------------------------
    # 5. Candidate Detection + Fuzzy Matching
    # --------------------------------------------------

    medicines = []

    predicted_medicines = []

    for line in candidate_lines:

        match_result = find_best_medicine_match(line)

        if match_result is None:
            continue

        medicine = PrescriptionMedicine(
            prescription_id=prescription.id,
            raw_text=match_result["raw_text"],
            suggested_name=match_result["suggested_name"],
            confidence_score=match_result["confidence_score"]
        )

        predicted_medicines.append(medicine)

        medicines.append(
            {
                "raw_text": match_result["raw_text"],
                "suggested_name": match_result["suggested_name"],
                "confidence_score": match_result["confidence_score"],
                "needs_review": match_result["needs_review"]
            }
        )

    session.add_all(predicted_medicines)

    await session.commit()
    # --------------------------------------------------
    # 5. Return Verification Screen Data
    # --------------------------------------------------

    return {
        "prescription_id":
            prescription.id,

        "image_path":
            prescription.image_path,

        "is_verified":
            prescription.is_verified,

        "overall_confidence":
            prescription.overall_confidence,

        "medicines":
            medicines
    }

async def verify_prescription_service(
    prescription_id: int,
    data: PrescriptionVerificationRequest,
    user_id: int,
    session: AsyncSession
):

    prescription = await session.get(
        PrescriptionDocument,
        prescription_id
    )

    if not prescription:
        raise HTTPException(
            status_code=404,
            detail="Prescription not found"
        )

    family_member = await session.get(
        FamilyMember,
        prescription.family_member_id
    )

    if not family_member:
        raise HTTPException(
            status_code=404,
            detail="Family member not found"
        )

    if family_member.user_id != user_id:
        raise HTTPException(
            status_code=403,
            detail="Not authorized"
        )

    if prescription.is_verified:
        raise HTTPException(
            status_code=400,
            detail="Prescription already verified"
        )

    medications_to_create = []

    for item in data.medicines:

        medication = Medication(
            family_member_id=family_member.id,
            medicine_name=item.medicine_name,
            dosage=item.dosage,
            frequency=item.frequency
        )

        medications_to_create.append(
            medication
        )

    session.add_all(
        medications_to_create
    )

    prescription.is_verified = True

    session.add(
        prescription
    )

    await session.commit()

    return {
        "message":
        "Prescription verified successfully"
    }