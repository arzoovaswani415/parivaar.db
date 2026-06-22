from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlmodel.ext.asyncio.session import AsyncSession
from app.database import get_session
from app.service.medications_service import (
    save_medication_to_db,
    get_medications_from_db,
    update_medication_in_db,
    delete_medication_in_db,
    get_medications_list
)
from app.models.user import User
from app.dependency import get_current_user


router = APIRouter(prefix="/medications")

class MedicationCreate(BaseModel):
    family_member_id: int
    medicine_name: str
    dosage: str | None = None
    frequency: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    notes: str | None = None

@router.get("/")
async def get_medications(current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    user_id = current_user.id
    medications = await get_medications_from_db(user_id, session)
    return {"medications": medications} 


@router.post("/create")
async def create_medication(data: MedicationCreate, current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    user_id = current_user.id
    new_medication = await save_medication_to_db(user_id, data, session)
    return new_medication

@router.put("/{medication_id}")
async def update_medication(medication_id: int, data: MedicationCreate, current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    user_id = current_user.id
    updated_medication = await update_medication_in_db(medication_id, data, user_id, session)
    return updated_medication

@router.put("/{medication_id}/delete")
async def delete_medication(medication_id: int, current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    user_id = current_user.id
    deleted_medication = await delete_medication_in_db(medication_id, user_id, session)
    return deleted_medication

@router.get("/")
async def list_medications(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    family_member_id: int | None = None,
    active: bool | None = None,
    medicine_name: str | None = None,
    page: int = 1,
    page_size: int = 10,
    sort_by: str = "start_date",
    sort_order: str = "desc"
):
    result = await get_medications_list(
        current_user.id,
        session,
        family_member_id,
        active,
        medicine_name,
        page,
        page_size,
        sort_by,
        sort_order
    )
    return result