from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlmodel.ext.asyncio.session import AsyncSession
from app.database import get_session
from app.service.insurance_service import (
    save_insurance_to_db,
    get_insurance_by_id,
    get_all_insurance_for_family_member,
    update_insurance_in_db,
    delete_insurance_in_db
)
from app.models.user import User
from app.dependency import get_current_user
from datetime import date


class InsuranceCreate(BaseModel):
    family_member_id: int
    insurance_company_name: str
    policy_number: str
    policy_holder_name: str
    coverage_amount: float
    start_date: date
    expiry_date: date
    notes: str | None = None


class InsuranceUpdate(BaseModel):
    insurance_company_name: str
    policy_number: str
    policy_holder_name: str
    coverage_amount: float
    start_date: date
    expiry_date: date
    notes: str | None = None
    is_active: bool = True


router = APIRouter(prefix="/insurance")


@router.post("/create")
async def create_insurance(data: InsuranceCreate, current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    new_insurance = await save_insurance_to_db(data, current_user.id, session)
    return new_insurance


@router.get("/{insurance_id}")
async def get_insurance(insurance_id: int, current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    insurance = await get_insurance_by_id(insurance_id, current_user.id, session)
    return insurance


@router.get("/family-member/{family_member_id}")
async def get_insurance_by_family_member(
    family_member_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    page: int = 1,
    page_size: int = 10,
    sort_by: str = "created_at",
    sort_order: str = "desc"
):
    result = await get_all_insurance_for_family_member(
        family_member_id,
        current_user.id,
        session,
        page,
        page_size,
        sort_by,
        sort_order
    )
    return result


@router.put("/{insurance_id}")
async def update_insurance(insurance_id: int, data: InsuranceUpdate, current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    updated_insurance = await update_insurance_in_db(insurance_id, data, current_user.id, session)
    return updated_insurance


@router.delete("/{insurance_id}")
async def delete_insurance(insurance_id: int, current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    await delete_insurance_in_db(insurance_id, current_user.id, session)
    return {"message": "Insurance record deleted successfully"}
