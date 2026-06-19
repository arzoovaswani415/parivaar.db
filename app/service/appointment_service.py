from fastapi import HTTPException
from sqlmodel import select
from app.models.appointment import Appointment
from app.models.user import User
from app.models.family_member import FamilyMember
from sqlmodel.ext.asyncio.session import AsyncSession 

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
