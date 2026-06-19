from fastapi import (
    APIRouter,
    Depends,
    UploadFile,
    File,
    HTTPException,
    status
)

from sqlmodel.ext.asyncio.session import AsyncSession

from app.database import get_session
from app.dependency import get_current_user

from app.models.user import User
from app.models.family_member import FamilyMember

from app.service.family_member_service import get_family_member_by_id

from app.service.prescription_service import (
    upload_prescription_service,
    verify_prescription_service
)
from app.schemas.prescription_schema import PrescriptionVerificationRequest , VerifiedMedicine



router = APIRouter(prefix="/prescriptions")



ALLOWED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp"
}

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


@router.post(
    "/upload",
    status_code=status.HTTP_201_CREATED
)
async def upload_prescription(
    family_member_id: int,
    doctor_visit_id: int,
    file: UploadFile = File(...),

    current_user: User = Depends(get_current_user),

    session: AsyncSession = Depends(get_session)
):
    """
    Upload prescription image.

    Flow:
    User -> Upload Image
         -> Validate
         -> Service Layer
         -> OCR
         -> Fuzzy Matching
         -> Save DB
    """

    # ------------------------------
    # 1. File exists?
    # ------------------------------

    if not file:
        raise HTTPException(
            status_code=400,
            detail="Prescription image is required"
        )

    # ------------------------------
    # 2. File name exists?
    # ------------------------------

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Invalid file name"
        )

    # ------------------------------
    # 3. Extension validation
    # ------------------------------

    filename = file.filename.lower()

    if not any(
        filename.endswith(ext)
        for ext in ALLOWED_EXTENSIONS
    ):
        raise HTTPException(
            status_code=400,
            detail=(
                "Only JPG, JPEG, PNG and WEBP files are allowed"
            )
        )

    # ------------------------------
    # 4. Size validation
    # ------------------------------

    contents = await file.read()

    if len(contents) == 0:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty"
        )

    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="File size exceeds 10 MB limit"
        )

    # reset pointer
    await file.seek(0)

    # ------------------------------
    # 5. Validate family member
    # ------------------------------

    family_member = await get_family_member_by_id(
        family_member_id,
        current_user.id,
        session
    )

    if not family_member:
        raise HTTPException(
            status_code=404,
            detail="Family member not found"
        )

    # ------------------------------
    # 6. Ownership validation
    # ------------------------------

    if family_member.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Not authorized"
        )

    # ------------------------------
    # 7. Call service
    # ------------------------------

    try:

        result = await upload_prescription_service(
            family_member_id=family_member_id,
            doctor_visit_id=doctor_visit_id,
            file=file,
            session=session
        )

        return result

    except HTTPException:
        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Prescription upload failed: {str(e)}"
        )

@router.post("/{prescription_id}/verify")
async def verify_prescription(
    prescription_id: int,
    data: PrescriptionVerificationRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    return await verify_prescription_service(
        prescription_id,
        data,
        current_user.id,
        session
    )