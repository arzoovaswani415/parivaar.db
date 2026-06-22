from datetime import datetime, timedelta
import calendar
from fastapi import HTTPException
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from app.models.reminder import Reminder
from app.models.family_member import FamilyMember
from app.schemas.reminder import ReminderCreate
from app.enums.reminder import ReminderStatus, ReminderFrequency

def calculate_next_trigger_at(start_date: datetime, time_of_day, frequency: str, current_time: datetime) -> datetime:
    """
    Calculates the next trigger time in local time.
    If the computed trigger time is in the past compared to current_time, 
    it rolls forward based on frequency.
    """
    if start_date.tzinfo is not None:
        start_date = start_date.replace(tzinfo=None)
    if current_time.tzinfo is not None:
        current_time = current_time.replace(tzinfo=None)

    hour = time_of_day.hour
    minute = time_of_day.minute
        
    trigger = start_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
    
    # If initial trigger has passed, roll forward based on frequency
    if trigger <= current_time:
        if frequency == ReminderFrequency.ONCE:
            pass
        elif frequency == ReminderFrequency.DAILY:
            while trigger <= current_time:
                trigger += timedelta(days=1)
        elif frequency == ReminderFrequency.WEEKLY:
            while trigger <= current_time:
                trigger += timedelta(weeks=1)
        elif frequency == ReminderFrequency.MONTHLY:
            while trigger <= current_time:
                month = trigger.month + 1
                year = trigger.year
                if month > 12:
                    month = 1
                    year += 1
                days_in_month = calendar.monthrange(year, month)[1]
                day = min(trigger.day, days_in_month)
                trigger = trigger.replace(year=year, month=month, day=day)
                
    return trigger


async def create_reminder_in_db(user_id: int, data: ReminderCreate, session: AsyncSession) -> Reminder:
    family_member = await session.get(FamilyMember, data.family_member_id)
    if not family_member or family_member.user_id != user_id or not family_member.is_active:
        raise HTTPException(status_code=404, detail="Family member not found or does not belong to the user")

    now_local = datetime.now()
    start_date = data.start_date if data.start_date else now_local
    if start_date.tzinfo is not None:
        start_date = start_date.replace(tzinfo=None)

    # 1. Start date < today -> reject
    if start_date.date() < now_local.date():
        raise HTTPException(
            status_code=400,
            detail="Start date cannot be in the past. Please choose today or a future date."
        )

    # 2. Check ONCE reminder time already passed
    scheduled_datetime = datetime.combine(start_date.date(), data.time_of_day)
    if data.frequency == ReminderFrequency.ONCE and scheduled_datetime < now_local:
        raise HTTPException(
            status_code=400,
            detail="For 'Once' frequency, the scheduled date and time must be in the future. Please choose a future date/time."
        )

    next_trigger = calculate_next_trigger_at(start_date, data.time_of_day, data.frequency, now_local)

    db_reminder = Reminder(
        family_member_id=data.family_member_id,
        title=data.title,
        description=data.description,
        type=data.type,
        frequency=data.frequency,
        time_of_day=data.time_of_day,
        start_date=start_date,
        next_trigger_at=next_trigger,
        status=ReminderStatus.PENDING,
        active_yn=True
    )

    session.add(db_reminder)
    await session.commit()
    await session.refresh(db_reminder)
    return db_reminder


async def get_reminders_from_db(
    user_id: int, 
    session: AsyncSession, 
    family_member_id: int | None = None, 
    active: bool | None = None,
    status: ReminderStatus | None = None
) -> list[Reminder]:
    query = select(Reminder).join(FamilyMember).where(
        FamilyMember.user_id == user_id,
        FamilyMember.is_active == True,
        Reminder.active_yn == True
    )

    if family_member_id is not None:
        query = query.where(Reminder.family_member_id == family_member_id)
    if active is not None:
        query = query.where(Reminder.active_yn == active)
    if status is not None:
        query = query.where(Reminder.status == status)

    query = query.order_by(Reminder.next_trigger_at.asc())
    result = await session.execute(query)
    return list(result.scalars().all())


async def get_upcoming_reminders_from_db(user_id: int, session: AsyncSession, limit: int = 5) -> list[Reminder]:
    query = select(Reminder).join(FamilyMember).where(
        FamilyMember.user_id == user_id,
        FamilyMember.is_active == True,
        Reminder.active_yn == True,
        Reminder.status == ReminderStatus.PENDING
    ).order_by(Reminder.next_trigger_at.asc()).limit(limit)

    result = await session.execute(query)
    return list(result.scalars().all())


async def complete_reminder_in_db(reminder_id: int, user_id: int, session: AsyncSession) -> Reminder:
    query = select(Reminder).join(FamilyMember).where(
        Reminder.id == reminder_id,
        FamilyMember.user_id == user_id
    )
    res = await session.execute(query)
    reminder = res.scalar_one_or_none()

    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")

    now_local = datetime.now()

    # Prevent multiple completions for the same occurrence
    if reminder.last_triggered_at:
        last_trig_naive = reminder.last_triggered_at.replace(tzinfo=None) if reminder.last_triggered_at.tzinfo else reminder.last_triggered_at
        if reminder.frequency == ReminderFrequency.DAILY:
            if last_trig_naive.date() == now_local.date():
                raise HTTPException(
                    status_code=400,
                    detail="Reminder already completed today"
                )
        elif reminder.frequency == ReminderFrequency.WEEKLY:
            next_trig_naive = reminder.next_trigger_at.replace(tzinfo=None) if reminder.next_trigger_at.tzinfo else reminder.next_trigger_at
            if (now_local - last_trig_naive).days < 7 and next_trig_naive > now_local:
                raise HTTPException(
                    status_code=400,
                    detail="Reminder already completed this week"
                )
        elif reminder.frequency == ReminderFrequency.MONTHLY:
            if last_trig_naive.year == now_local.year and last_trig_naive.month == now_local.month:
                raise HTTPException(
                    status_code=400,
                    detail="Reminder already completed this month"
                )

    reminder.last_triggered_at = now_local

    if reminder.frequency == ReminderFrequency.ONCE:
        reminder.status = ReminderStatus.COMPLETED
        reminder.active_yn = False
    else:
        next_trig_naive = reminder.next_trigger_at.replace(tzinfo=None) if reminder.next_trigger_at.tzinfo else reminder.next_trigger_at
        if next_trig_naive > now_local:
            base_date = next_trig_naive
            current_limit = next_trig_naive
        else:
            base_date = next_trig_naive
            current_limit = now_local

        reminder.next_trigger_at = calculate_next_trigger_at(
            base_date, reminder.time_of_day, reminder.frequency, current_limit
        )
        reminder.status = ReminderStatus.PENDING

    reminder.updated_at = now_local
    session.add(reminder)
    await session.commit()
    await session.refresh(reminder)
    return reminder


async def delete_reminder_in_db(reminder_id: int, user_id: int, session: AsyncSession) -> dict:
    query = select(Reminder).join(FamilyMember).where(
        Reminder.id == reminder_id,
        FamilyMember.user_id == user_id,
        FamilyMember.is_active == True
    )
    res = await session.execute(query)
    reminder = res.scalar_one_or_none()

    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")

    reminder.active_yn = False
    reminder.status = ReminderStatus.DISABLED
    reminder.updated_at = datetime.now()

    session.add(reminder)
    await session.commit()
    return {"success": True, "message": "Reminder deleted successfully"}
