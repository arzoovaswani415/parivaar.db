from fastapi import HTTPException
from sqlmodel import select
from app.models.appointment import Appointment
from app.models.user import User
from app.models.family_member import FamilyMember
from sqlmodel.ext.asyncio.session import AsyncSession 
from datetime import date

async def save_appointment_in_db(user_id: int, data: Appointment, session: AsyncSession):
    # Check if the family member belongs to the user
    family_member = await session.get(FamilyMember, data.family_member_id)
    if not family_member or family_member.user_id != user_id or not family_member.is_active:
        raise HTTPException(status_code=404, detail="Family member not found or does not belong to the user")

    new_appointment = Appointment(
        family_member_id=data.family_member_id,
        doctor_name=data.doctor_name,
        appointment_date=data.appointment_date,
        appointment_time=data.appointment_time,
        reason=data.reason,
        notes=data.notes
    )
    
    session.add(new_appointment)
    await session.commit()
    await session.refresh(new_appointment)
    return new_appointment

async def get_appointments_from_db(user_id: int, session: AsyncSession):
    result = await session.execute(
        select(Appointment).join(FamilyMember).where(
            FamilyMember.user_id == user_id,
            FamilyMember.is_active == True
        )
    )
    if not result:
        raise HTTPException(status_code=404, detail="No appointments found for the user")
    appointments = result.scalars().all()
    return appointments

async def update_appointment_in_db(appointment_id: int, data: Appointment, user_id: int, session: AsyncSession):
    result=await get_appointment_db(appointment_id, user_id, session)
    # update the appointment with the new data
    result.family_member_id = data.family_member_id
    result.doctor_name = data.doctor_name
    result.appointment_date = data.appointment_date
    result.appointment_time = data.appointment_time
    result.reason = data.reason
    result.notes = data.notes
    await session.commit()
    await session.refresh(result)
    return result

async def delete_appointment_in_db(appointment_id: int, user_id: int, session: AsyncSession):
    result=await get_appointment_db(appointment_id, user_id, session)
    await session.delete(result)
    await session.commit()
    return {"detail": "Appointment deleted successfully"}


async def get_appointments_list(
    user_id: int,
    session: AsyncSession,
    family_member_id: int | None = None,
    upcoming: bool | None = None,
    completed: bool | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    page: int = 1,
    page_size: int = 10,
    sort_by: str = "appointment_date",
    sort_order: str = "desc"
):
    allowed_sort_fields = {"appointment_date", "doctor_name"}
    if sort_by not in allowed_sort_fields:
        sort_by = "appointment_date"
    if sort_order not in ["asc", "desc"]:
        sort_order = "desc"

    query = select(Appointment).join(FamilyMember).where(
        FamilyMember.user_id == user_id,
        FamilyMember.is_active == True
    )

    if family_member_id is not None:
        query = query.where(Appointment.family_member_id == family_member_id)

    if upcoming is not None and upcoming:
        query = query.where(Appointment.status == "Scheduled")

    if completed is not None and completed:
        query = query.where(Appointment.status == "Completed")

    if start_date is not None:
        query = query.where(Appointment.appointment_date >= start_date)

    if end_date is not None:
        query = query.where(Appointment.appointment_date <= end_date)

    total_result = await session.execute(
        select(func.count(Appointment.id)).select_from(Appointment).join(FamilyMember).where(
            FamilyMember.user_id == user_id,
            FamilyMember.is_active == True
        )
    )
    total = total_result.scalar()

    if sort_order == "desc":
        query = query.order_by(getattr(Appointment, sort_by).desc())
    else:
        query = query.order_by(getattr(Appointment, sort_by).asc())

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