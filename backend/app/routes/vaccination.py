from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlmodel.ext.asyncio.session import AsyncSession
from app.database import get_session
from app.service.vaccination_service import (
    save_vaccination_to_db,
    get_vaccination_by_id,
    get_all_vaccinations_for_family_member,
    update_vaccination_in_db,
    delete_vaccination_in_db
)
from app.models.user import User
from app.dependency import get_current_user
from datetime import date


class VaccinationCreate(BaseModel):
    family_member_id: int
    vaccine_name: str
    administered_on: date
    next_due_date: date | None = None
    notes: str | None = None


class VaccinationUpdate(BaseModel):
    vaccine_name: str
    administered_on: date
    next_due_date: date | None = None
    notes: str | None = None
    is_active: bool = True


router = APIRouter(prefix="/vaccinations")


@router.post("/create")
async def create_vaccination(data: VaccinationCreate, current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    new_vaccination = await save_vaccination_to_db(data, current_user.id, session)
    return new_vaccination


@router.get("/{vaccination_id}")
async def get_vaccination(vaccination_id: int, current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    vaccination = await get_vaccination_by_id(vaccination_id, current_user.id, session)
    return vaccination


@router.get("/family-member/{family_member_id}")
async def get_vaccinations_by_family_member(
    family_member_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    page: int = 1,
    page_size: int = 10,
    sort_by: str = "administered_on",
    sort_order: str = "desc"
):
    result = await get_all_vaccinations_for_family_member(
        family_member_id,
        current_user.id,
        session,
        page,
        page_size,
        sort_by,
        sort_order
    )
    return result


@router.put("/{vaccination_id}")
async def update_vaccination(vaccination_id: int, data: VaccinationUpdate, current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    updated_vaccination = await update_vaccination_in_db(vaccination_id, data, current_user.id, session)
    return updated_vaccination


@router.delete("/{vaccination_id}")
async def delete_vaccination(vaccination_id: int, current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    await delete_vaccination_in_db(vaccination_id, current_user.id, session)
    return {"message": "Vaccination record deleted successfully"}
