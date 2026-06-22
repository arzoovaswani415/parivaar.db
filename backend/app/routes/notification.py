from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from app.database import get_session
from app.dependency import get_current_user
from app.models.user import User
from app.service.notification_service import notification_service

router = APIRouter(prefix="/notifications", tags=["notifications"])

def format_notification_response(n) -> dict:
    return {
        "id": n.id,
        "userId": n.user_id,
        "familyMemberId": n.family_member_id,
        "familyMemberName": n.family_member.name if n.family_member else None,
        "reminderId": n.reminder_id,
        "message": n.message,
        "notificationType": n.notification_type,
        "read": n.read_yn,
        "createdAt": n.created_at.isoformat() if n.created_at else None,
    }

@router.get("")
async def get_notifications(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    notifications = await notification_service.get_notifications_from_db(current_user.id, session)
    return {"success": True, "data": [format_notification_response(n) for n in notifications]}

@router.put("/{id}/read")
async def mark_read(
    id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    notification = await notification_service.mark_notification_read(id, current_user.id, session)
    return {"success": True, "data": format_notification_response(notification)}

@router.put("/read-all")
async def mark_all_read(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    await notification_service.mark_all_notifications_read(current_user.id, session)
    return {"success": True}

@router.get("/unread-count")
async def get_unread_count(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    count = await notification_service.get_unread_notifications_count(current_user.id, session)
    return {"success": True, "count": count}
