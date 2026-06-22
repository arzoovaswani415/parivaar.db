import logging
from sqlmodel import select, func
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi_mail import FastMail, MessageSchema, MessageType
from app.mail import conf
from app.models.notification import Notification
from app.enums.reminder import NotificationType

logger = logging.getLogger("notification_service")
fastmail = FastMail(conf)

class NotificationService:
    async def send_in_app(
        self,
        session: AsyncSession,
        user_id: int,
        family_member_id: int,
        reminder_id: int | None,
        message: str,
        notification_type: NotificationType = NotificationType.REMINDER
    ) -> Notification:
        """
        Creates and stores an in-app notification in the database.
        """
        notification = Notification(
            user_id=user_id,
            family_member_id=family_member_id,
            reminder_id=reminder_id,
            message=message,
            notification_type=notification_type,
            read_yn=False
        )
        session.add(notification)
        await session.commit()
        await session.refresh(notification)
        return notification

    async def send_email(self, recipient_email: str, subject: str, body: str) -> None:
        """
        Sends an email using FastAPI-Mail configuration.
        """
        try:
            message = MessageSchema(
                subject=subject,
                recipients=[recipient_email],
                body=body,
                subtype=MessageType.html
            )
            await fastmail.send_message(message)
            logger.info(f"Email sent successfully to {recipient_email}")
        except Exception as e:
            logger.error(f"Failed to send email to {recipient_email}: {str(e)}")
            raise e

    async def send_whatsapp(self, recipient_phone: str, message: str) -> None:
        """
        Placeholder method for future WhatsApp integration.
        """
        logger.warning(f"WhatsApp sending placeholder triggered for {recipient_phone}. Not implemented.")
        raise NotImplementedError("WhatsApp sending is not implemented in this phase.")

    async def get_notifications_from_db(self, user_id: int, session: AsyncSession) -> list[Notification]:
        query = select(Notification).where(Notification.user_id == user_id).order_by(Notification.created_at.desc())
        res = await session.execute(query)
        return list(res.scalars().all())

    async def mark_notification_read(self, notification_id: int, user_id: int, session: AsyncSession) -> Notification:
        query = select(Notification).where(Notification.id == notification_id, Notification.user_id == user_id)
        res = await session.execute(query)
        notification = res.scalar_one_or_none()
        if not notification:
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Notification not found")
        notification.read_yn = True
        session.add(notification)
        await session.commit()
        await session.refresh(notification)
        return notification

    async def mark_all_notifications_read(self, user_id: int, session: AsyncSession) -> None:
        query = select(Notification).where(Notification.user_id == user_id, Notification.read_yn == False)
        res = await session.execute(query)
        unread = res.scalars().all()
        for notification in unread:
            notification.read_yn = True
            session.add(notification)
        await session.commit()

    async def get_unread_notifications_count(self, user_id: int, session: AsyncSession) -> int:
        query = select(func.count(Notification.id)).where(Notification.user_id == user_id, Notification.read_yn == False)
        res = await session.execute(query)
        return res.scalar() or 0

# Singleton instance for app-wide use
notification_service = NotificationService()

