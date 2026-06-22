from fastapi import APIRouter, Depends, Query
from sqlmodel.ext.asyncio.session import AsyncSession
from app.database import get_session
from app.dependency import get_current_user
from app.models.user import User
from app.schemas.reminder import ReminderCreate
from app.service.reminder_service import (
    create_reminder_in_db,
    get_reminders_from_db,
    get_upcoming_reminders_from_db,
    complete_reminder_in_db,
    delete_reminder_in_db
)

router = APIRouter(prefix="/reminders", tags=["reminders"])

def format_reminder_response(reminder) -> dict:
    return {
        "id": reminder.id,
        "familyMemberId": reminder.family_member_id,
        "familyMemberName": reminder.family_member.name if reminder.family_member else None,
        "title": reminder.title,
        "description": reminder.description,
        "type": reminder.type,
        "frequency": reminder.frequency,
        "timeOfDay": reminder.time_of_day,
        "startDate": reminder.start_date.isoformat() if reminder.start_date else None,
        "nextTriggerAt": reminder.next_trigger_at.isoformat() if reminder.next_trigger_at else None,
        "lastTriggeredAt": reminder.last_triggered_at.isoformat() if reminder.last_triggered_at else None,
        "status": reminder.status,
        "active": reminder.active_yn,
        "createdAt": reminder.created_at.isoformat() if reminder.created_at else None,
        "updatedAt": reminder.updated_at.isoformat() if reminder.updated_at else None,
    }

@router.post("")
async def create_reminder(
    data: ReminderCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    reminder = await create_reminder_in_db(current_user.id, data, session)
    return {"success": True, "data": format_reminder_response(reminder)}

@router.get("")
async def get_reminders(
    familyMemberId: int | None = Query(None),
    active: bool | None = Query(None),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    reminders = await get_reminders_from_db(
        current_user.id,
        session,
        family_member_id=familyMemberId,
        active=active
    )
    return {"success": True, "data": [format_reminder_response(r) for r in reminders]}

@router.get("/upcoming")
async def get_upcoming_reminders(
    limit: int = Query(5),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    reminders = await get_upcoming_reminders_from_db(current_user.id, session, limit=limit)
    return {"success": True, "data": [format_reminder_response(r) for r in reminders]}

@router.put("/{id}/complete")
async def complete_reminder(
    id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    reminder = await complete_reminder_in_db(id, current_user.id, session)
    return {"success": True, "data": format_reminder_response(reminder)}

@router.delete("/{id}")
async def delete_reminder(
    id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    res = await delete_reminder_in_db(id, current_user.id, session)
    return res
