from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlmodel.ext.asyncio.session import AsyncSession
from app.database import get_session
from app.service.appointment_service import (
    save_appointment_in_db,
    get_appointments_from_db,
    update_appointment_in_db,
    delete_appointment_in_db,
    get_appointments_list
)
from app.models.user import User
from app.dependency import get_current_user
from app.models.appointment import Appointment
from datetime import date

router = APIRouter(prefix="/appointments")

class AppointmentCreate(BaseModel):
    family_member_id: int
    doctor_name: str
    appointment_date: str
    appointment_time: str
    reason: str | None = None
    notes: str | None = None

@router.get("/")
async def get_appointments(current_user: User = Depends(get_current_user), session: AsyncSession=Depends(get_session)):
    user_id = current_user.id
    appointments = await get_appointments_from_db(user_id, session)
    return {"appointments": appointments}   

@router.post("/create")
async def create_appointment(data: AppointmentCreate, current_user: User = Depends(get_current_user), session: AsyncSession=Depends(get_session)):
    user_id = current_user.id
    new_appointment = await save_appointment_in_db(user_id, data, session)
    return {"appointment": new_appointment}

@router.put("/{appointment_id}")
async def update_appointment(appointment_id: int, data: AppointmentCreate, current_user: User = Depends(get_current_user), session: AsyncSession=Depends(get_session)):
    user_id = current_user.id
    updated_appointment = await update_appointment_in_db(appointment_id, data, user_id, session)
    return {"appointment": updated_appointment}

@router.put("/{appointment_id}/delete")
async def delete_appointment(appointment_id: int, current_user: User = Depends(get_current_user), session: AsyncSession=Depends(get_session)):
    user_id = current_user.id
    result = await delete_appointment_in_db(appointment_id, user_id, session)
    return result  


@router.get("/")
async def list_appointments(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
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
    result = await get_appointments_list(
        current_user.id,
        session,
        family_member_id,
        upcoming,
        completed,
        start_date,
        end_date,
        page,
        page_size,
        sort_by,
        sort_order
    )
    return result