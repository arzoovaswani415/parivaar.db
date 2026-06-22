from fastapi import APIRouter, Depends
from pydantic import BaseModel
from datetime import date
from sqlmodel.ext.asyncio.session import AsyncSession
from app.database import get_session
from app.service.medical_history_service import (
    save_medical_history_to_db,
    delete_medical_history as delete_medical_history_db,
    update_medical_history as update_medical_history_db,
    get_medical_history_db,
    get_medical_history_list
)
from app.models.user import User
from app.dependency import get_current_user
from app.models.medical_history import MedicalHistory

class MedicalHistoryCreate(BaseModel):
    family_member_id: int
    category: str
    title: str
    description: str | None = None
    diagnosed_on: date | None = None
    source: str | None = None

router = APIRouter(prefix="/medical_history")

@router.post("/create")
async def create_medical_history(data: MedicalHistoryCreate, current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    new_medical_history = await save_medical_history_to_db(data, current_user.id, session)
    return new_medical_history

@router.get("/{medical_history_id}")
async def get_medical_history(medical_history_id: int, current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    medical_history = await get_medical_history_db(medical_history_id, current_user.id, session)
    return medical_history

@router.put("/{medical_history_id}")
async def update_medical_history(medical_history_id: int, data: MedicalHistoryCreate, current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    updated_medical_history = await update_medical_history_db(medical_history_id, data, current_user.id, session)
    return updated_medical_history

@router.delete("/{medical_history_id}")
async def delete_medical_history(medical_history_id: int, current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    await delete_medical_history_db(medical_history_id, current_user.id, session)
    return {"message": "Medical history deleted successfully"}


@router.get("/")
async def list_medical_history(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    family_member_id: int | None = None,
    category: str | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    page: int = 1,
    page_size: int = 10,
    sort_by: str = "created_at",
    sort_order: str = "desc"
):
    result = await get_medical_history_list(
        current_user.id,
        session,
        family_member_id,
        category,
        start_date,
        end_date,
        page,
        page_size,
        sort_by,
        sort_order
    )
    return result