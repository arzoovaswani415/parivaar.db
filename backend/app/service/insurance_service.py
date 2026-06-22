from fastapi import HTTPException
from sqlmodel import select, func
from app.models.insurance import Insurance
from app.models.family_member import FamilyMember
from sqlmodel.ext.asyncio.session import AsyncSession
from datetime import date


async def save_insurance_to_db(data, user_id: int, session: AsyncSession):
    family_member_id = data.family_member_id
    result = await session.execute(
        select(FamilyMember).where(
            FamilyMember.id == family_member_id,
            FamilyMember.user_id == user_id,
            FamilyMember.is_active == True
        )
    )
    family_member = result.scalar_one_or_none()

    if not family_member:
        raise HTTPException(status_code=404, detail="Family member not found")

    new_insurance = Insurance.from_orm(data)
    session.add(new_insurance)
    await session.commit()
    await session.refresh(new_insurance)
    return new_insurance


async def get_insurance_by_id(insurance_id: int, user_id: int, session: AsyncSession):
    result = await session.execute(
        select(Insurance).join(FamilyMember).where(
            Insurance.id == insurance_id,
            FamilyMember.user_id == user_id,
            FamilyMember.is_active == True
        )
    )
    insurance = result.scalar_one_or_none()

    if not insurance:
        raise HTTPException(status_code=404, detail="Insurance record not found")

    return insurance


async def get_all_insurance_for_family_member(
    family_member_id: int,
    user_id: int,
    session: AsyncSession,
    page: int = 1,
    page_size: int = 10,
    sort_by: str = "created_at",
    sort_order: str = "desc"
):
    result = await session.execute(
        select(FamilyMember).where(
            FamilyMember.id == family_member_id,
            FamilyMember.user_id == user_id,
            FamilyMember.is_active == True
        )
    )
    family_member = result.scalar_one_or_none()

    if not family_member:
        raise HTTPException(status_code=404, detail="Family member not found")

    allowed_sort_fields = {"created_at", "updated_at", "expiry_date", "start_date", "coverage_amount"}
    if sort_by not in allowed_sort_fields:
        sort_by = "created_at"
    if sort_order not in ["asc", "desc"]:
        sort_order = "desc"

    query = select(Insurance).where(Insurance.family_member_id == family_member_id)

    if sort_order == "desc":
        query = query.order_by(getattr(Insurance, sort_by).desc())
    else:
        query = query.order_by(getattr(Insurance, sort_by).asc())

    total_result = await session.execute(select(func.count(Insurance.id)).where(Insurance.family_member_id == family_member_id))
    total = total_result.scalar()

    page_size = min(page_size, 100)
    offset = (page - 1) * page_size

    query = query.offset(offset).limit(page_size)
    result = await session.execute(query)
    insurances = result.scalars().all()

    total_pages = (total + page_size - 1) // page_size

    return {
        "items": insurances,
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": total_pages
    }


async def update_insurance_in_db(insurance_id: int, data, user_id: int, session: AsyncSession):
    insurance = await get_insurance_by_id(insurance_id, user_id, session)

    insurance.insurance_company_name = data.insurance_company_name
    insurance.policy_number = data.policy_number
    insurance.policy_holder_name = data.policy_holder_name
    insurance.coverage_amount = data.coverage_amount
    insurance.start_date = data.start_date
    insurance.expiry_date = data.expiry_date
    insurance.notes = data.notes
    insurance.is_active = data.is_active
    insurance.updated_at = __import__('datetime').datetime.utcnow()

    session.add(insurance)
    await session.commit()
    await session.refresh(insurance)
    return insurance


async def delete_insurance_in_db(insurance_id: int, user_id: int, session: AsyncSession):
    insurance = await get_insurance_by_id(insurance_id, user_id, session)
    await session.delete(insurance)
    await session.commit()
    return {"message": "Insurance record deleted successfully"}
