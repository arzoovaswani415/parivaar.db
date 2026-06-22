from fastapi import HTTPException
from sqlmodel import select, func
from app.models.vaccination import Vaccination
from app.models.family_member import FamilyMember
from sqlmodel.ext.asyncio.session import AsyncSession
from datetime import date


async def save_vaccination_to_db(data, user_id: int, session: AsyncSession):
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

    new_vaccination = Vaccination.from_orm(data)
    session.add(new_vaccination)
    await session.commit()
    await session.refresh(new_vaccination)
    return new_vaccination


async def get_vaccination_by_id(vaccination_id: int, user_id: int, session: AsyncSession):
    result = await session.execute(
        select(Vaccination).join(FamilyMember).where(
            Vaccination.id == vaccination_id,
            FamilyMember.user_id == user_id,
            FamilyMember.is_active == True
        )
    )
    vaccination = result.scalar_one_or_none()

    if not vaccination:
        raise HTTPException(status_code=404, detail="Vaccination record not found")

    return vaccination


async def get_all_vaccinations_for_family_member(
    family_member_id: int,
    user_id: int,
    session: AsyncSession,
    page: int = 1,
    page_size: int = 10,
    sort_by: str = "administered_on",
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

    allowed_sort_fields = {"administered_on", "next_due_date", "vaccine_name"}
    if sort_by not in allowed_sort_fields:
        sort_by = "administered_on"
    if sort_order not in ["asc", "desc"]:
        sort_order = "desc"

    query = select(Vaccination).where(Vaccination.family_member_id == family_member_id)

    if sort_order == "desc":
        query = query.order_by(getattr(Vaccination, sort_by).desc())
    else:
        query = query.order_by(getattr(Vaccination, sort_by).asc())

    total_result = await session.execute(select(func.count(Vaccination.id)).where(Vaccination.family_member_id == family_member_id))
    total = total_result.scalar()

    page_size = min(page_size, 100)
    offset = (page - 1) * page_size

    query = query.offset(offset).limit(page_size)
    result = await session.execute(query)
    vaccinations = result.scalars().all()

    total_pages = (total + page_size - 1) // page_size

    return {
        "items": vaccinations,
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": total_pages
    }


async def update_vaccination_in_db(vaccination_id: int, data, user_id: int, session: AsyncSession):
    vaccination = await get_vaccination_by_id(vaccination_id, user_id, session)

    vaccination.vaccine_name = data.vaccine_name
    vaccination.administered_on = data.administered_on
    vaccination.next_due_date = data.next_due_date
    vaccination.notes = data.notes
    vaccination.is_active = data.is_active

    session.add(vaccination)
    await session.commit()
    await session.refresh(vaccination)
    return vaccination


async def delete_vaccination_in_db(vaccination_id: int, user_id: int, session: AsyncSession):
    vaccination = await get_vaccination_by_id(vaccination_id, user_id, session)
    await session.delete(vaccination)
    await session.commit()
    return {"message": "Vaccination record deleted successfully"}
