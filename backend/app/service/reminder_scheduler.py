import logging
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlmodel import select
from app.database import async_session
from app.models.reminder import Reminder
from app.models.family_member import FamilyMember
from app.models.user import User
from app.enums.reminder import ReminderStatus, ReminderFrequency, NotificationType
from app.service.reminder_service import calculate_next_trigger_at
from app.service.notification_service import notification_service

logger = logging.getLogger("reminder_scheduler")

_scheduler = None

def get_scheduler() -> AsyncIOScheduler:
    global _scheduler
    if _scheduler is None:
        _scheduler = AsyncIOScheduler()
    return _scheduler


async def check_due_reminders():
    """
    Background job running every minute to check and trigger due reminders.
    Uses local naive datetime.
    """
    logger.info("Scheduler checking for due reminders...")
    now_local = datetime.now()

    async with async_session() as session:
        try:
            # Query active pending reminders where next_trigger_at is due
            query = select(Reminder).where(
                Reminder.active_yn == True,
                Reminder.status == ReminderStatus.PENDING,
                Reminder.next_trigger_at <= now_local
            )
            res = await session.execute(query)
            due_reminders = res.scalars().all()

            if not due_reminders:
                logger.info("No due reminders found.")
                return

            logger.info(f"Found {len(due_reminders)} due reminders.")

            for reminder in due_reminders:
                family_member = await session.get(FamilyMember, reminder.family_member_id)
                if not family_member:
                    logger.warning(f"FamilyMember not found for reminder {reminder.id}. Disabling reminder.")
                    reminder.active_yn = False
                    reminder.status = ReminderStatus.DISABLED
                    session.add(reminder)
                    continue

                user = await session.get(User, family_member.user_id)
                if not user:
                    logger.warning(f"User not found for family member {family_member.id}. Disabling reminder.")
                    reminder.active_yn = False
                    reminder.status = ReminderStatus.DISABLED
                    session.add(reminder)
                    continue

                recipient_email = family_member.email if family_member.email else user.email
                family_member_name = family_member.name

                message = f"Reminder for {family_member_name}: {reminder.title}"
                if reminder.description:
                    message += f" ({reminder.description})"

                logger.info(f"Triggering reminder {reminder.id} for {family_member_name}")

                # Create In-App Notification
                try:
                    await notification_service.send_in_app(
                        session=session,
                        user_id=user.id,
                        family_member_id=family_member.id,
                        reminder_id=reminder.id,
                        message=message,
                        notification_type=NotificationType.REMINDER
                    )
                except Exception as e:
                    logger.error(f"Failed to save in-app notification for reminder {reminder.id}: {str(e)}")

                # Send Email Notification
                if recipient_email:
                    subject = f"{reminder.type.replace('_', ' ').title()} Reminder"
                    body = f"""
                    <html>
                        <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.6;">
                            <div style="max-width: 600px; margin: 0 auto; border: 1px solid #ddd; padding: 20px; border-radius: 8px;">
                                <h2 style="color: #3E2723; border-bottom: 2px solid #FFD54F; padding-bottom: 10px;">{subject}</h2>
                                <p>Hello,</p>
                                <p>This is a reminder for <strong>{family_member_name}</strong>.</p>
                                <div style="background-color: #f9f9f9; padding: 15px; border-left: 4px solid #FFD54F; margin: 15px 0;">
                                    <p style="margin: 0;"><strong>Topic:</strong> {reminder.title}</p>
                                    {f'<p style="margin: 5px 0 0 0;"><strong>Details:</strong> {reminder.description}</p>' if reminder.description else ''}
                                    <p style="margin: 5px 0 0 0;"><strong>Scheduled Time:</strong> {reminder.time_of_day}</p>
                                </div>
                                <p>Please make sure this action is completed.</p>
                                <hr style="border: 0; border-top: 1px solid #eee; margin: 20px 0;">
                                <p style="font-size: 0.8em; color: #777;">Sent automatically by Parivaar.db Health Reminder Engine.</p>
                            </div>
                        </body>
                    </html>
                    """
                    try:
                        await notification_service.send_email(
                            recipient_email=recipient_email,
                            subject=subject,
                            body=body
                        )
                    except Exception as e:
                        logger.error(f"Scheduler failed to send email to {recipient_email}: {str(e)}")

                # Roll over trigger time
                reminder.last_triggered_at = now_local
                if reminder.frequency == ReminderFrequency.ONCE:
                    reminder.status = ReminderStatus.COMPLETED
                    reminder.active_yn = False
                else:
                    reminder.next_trigger_at = calculate_next_trigger_at(
                        now_local, reminder.time_of_day, reminder.frequency, now_local
                    )
                    reminder.status = ReminderStatus.PENDING

                reminder.updated_at = now_local
                session.add(reminder)

            await session.commit()
            logger.info("Due reminders check completed and rolled over successfully.")

        except Exception as e:
            logger.error(f"Error in scheduler check_due_reminders: {str(e)}")
            await session.rollback()


async def start_scheduler():
    scheduler = get_scheduler()
    if not scheduler.running:
        scheduler.add_job(
            check_due_reminders,
            "interval",
            minutes=1,
            id="check_due_reminders_job",
            replace_existing=True
        )
        scheduler.start()
        logger.info("APScheduler started successfully.")
    else:
        logger.info("APScheduler is already running.")


async def stop_scheduler():
    scheduler = get_scheduler()
    if scheduler.running:
        scheduler.shutdown()
        logger.info("APScheduler stopped successfully.")
