from fastapi import HTTPException
from sqlmodel import select
from app.models.doctors_visit import DoctorsVisit
from app.models.family_member import FamilyMember
from sqlmodel.ext.asyncio.session import AsyncSession
from app.dependency import get_current_user
from datetime import date


async def save_doctors_visit_to_db(user_id: int, data: DoctorsVisit, session: AsyncSession):
    family_member_id = data.family_member_id
    #  family_member_id is a foreign key referencing the FamilyMember table
    result = await session.execute(
        select(FamilyMember).where(
            FamilyMember.id == family_member_id,
            FamilyMember.user_id == user_id,
            FamilyMember.is_active == True
        )
    )
    family_member = result.scalar_one_or_none()
    # result.scalar_one_or_none() is used to get a single result from the query. If there is no result, it returns None. If there are multiple results, it raises an exception. In this case, we expect either one family member or none, so scalar_one_or_none() is appropriate.

    if not family_member:
        raise HTTPException(status_code=404, detail="Family member not found")

    if  data.follow_up_date is not None and data.follow_up_date < data.visit_date:
        raise HTTPException(status_code=400, detail="Follow-up date cannot be before visit date")

    new_doctors_visit = DoctorsVisit.from_orm(data)
    session.add(new_doctors_visit)
    await session.commit()
    await session.refresh(new_doctors_visit)
    return new_doctors_visit

async def get_doctors_visits_from_db(user_id: int, session: AsyncSession):
    result = await session.execute(
        select(DoctorsVisit).join(FamilyMember).where(
            DoctorsVisit.family_member_id == FamilyMember.id,
            FamilyMember.user_id == user_id,
            FamilyMember.is_active == True
        )
    )
    doctors_visits = result.scalars().all()
    if not doctors_visits:
        raise HTTPException(status_code=404, detail="Doctors visits not found")
    return doctors_visits
 
async def get_doctors_visit_by_id(visit_id: int, user_id: int, session: AsyncSession):
    result = await session.execute(
        select(DoctorsVisit).join(FamilyMember).where(
            DoctorsVisit.family_member_id == FamilyMember.id,
            FamilyMember.user_id == user_id,
            FamilyMember.is_active == True,
            DoctorsVisit.id == visit_id
        )
    )
    doctors_visit = result.scalar_one_or_none()
    if not doctors_visit:
        raise HTTPException(status_code=404, detail="Doctors visit not found")
    return doctors_visit 

async def update_doctors_visit_in_db(visit_id: int, data: DoctorsVisit, user_id: int, session: AsyncSession):
    doctors_visit=await get_doctors_visit_by_id(visit_id, user_id, session)

    doctors_visit.doctor_name = data.doctor_name
    doctors_visit.hospital_name = data.hospital_name
    doctors_visit.visit_date = data.visit_date
    doctors_visit.diagnosis = data.diagnosis
    doctors_visit.prescription_notes = data.prescription_notes
    doctors_visit.follow_up_date = data.follow_up_date  

    session.add(doctors_visit)
    await session.commit()
    await session.refresh(doctors_visit)
    return doctors_visit

async def delete_doctors_visit_in_db(visit_id: int, user_id: int, session: AsyncSession):
    doctors_visit = await get_doctors_visit_by_id(visit_id, user_id, session)
    await session.delete(doctors_visit)
    await session.commit()  
    return {"message": "Doctors visit deleted successfully"}


async def get_doctors_visits_list(
    user_id: int,
    session: AsyncSession,
    family_member_id: int | None = None,
    doctor_name: str | None = None,
    visit_date: date | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    page: int = 1,
    page_size: int = 10,
    sort_by: str = "visit_date",
    sort_order: str = "desc"
):
    allowed_sort_fields = {"visit_date", "doctor_name", "hospital_name"}
    if sort_by not in allowed_sort_fields:
        sort_by = "visit_date"
    if sort_order not in ["asc", "desc"]:
        sort_order = "desc"

    query = select(DoctorsVisit).join(FamilyMember).where(
        FamilyMember.user_id == user_id,
        FamilyMember.is_active == True
    )

    if family_member_id is not None:
        query = query.where(DoctorsVisit.family_member_id == family_member_id)

    if doctor_name is not None:
        query = query.where(DoctorsVisit.doctor_name.ilike(f"%{doctor_name}%"))

    if visit_date is not None:
        query = query.where(DoctorsVisit.visit_date == visit_date)

    if start_date is not None:
        query = query.where(DoctorsVisit.visit_date >= start_date)

    if end_date is not None:
        query = query.where(DoctorsVisit.visit_date <= end_date)

    total_result = await session.execute(
        select(func.count(DoctorsVisit.id)).select_from(DoctorsVisit).join(FamilyMember).where(
            FamilyMember.user_id == user_id,
            FamilyMember.is_active == True
        )
    )
    total = total_result.scalar()

    if sort_order == "desc":
        query = query.order_by(getattr(DoctorsVisit, sort_by).desc())
    else:
        query = query.order_by(getattr(DoctorsVisit, sort_by).asc())

    page_size = min(page_size, 100)
    offset = (page - 1) * page_size

    query = query.offset(offset).limit(page_size)
    result = await session.execute(query)
    items = result.scalars().all()

    total_pages = (total + page_size - 1) // page_size

    return {
        "items": items,
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": total_pages
    }