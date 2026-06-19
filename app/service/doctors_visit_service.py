from fastapi import HTTPException
from sqlmodel import select
from app.models.doctors_visit import DoctorsVisit
from app.models.family_member import FamilyMember
from sqlmodel.ext.asyncio.session import AsyncSession
from app.dependency import get_current_user


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

    if data.follow_up_date < data.visit_date:
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
    