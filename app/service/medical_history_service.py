from fastapi import HTTPException
from sqlmodel import select, func
from datetime import date
from app.models.medical_history import MedicalHistory
from app.models.family_member import FamilyMember
from app.models.user import User
from sqlmodel.ext.asyncio.session import AsyncSession
from app.dependency import get_current_user

async def save_medical_history_to_db(data: MedicalHistory, user_id: int, session: AsyncSession):
    family_member_id = data.family_member_id
    result = await session.execute(
        select(FamilyMember).where(
            FamilyMember.id == family_member_id,
            FamilyMember.user_id == user_id,
            FamilyMember.is_active == True
        )
    )
    family_member = result.scalar_one_or_none()

    if not family_member:
        raise HTTPException(status_code=404, detail="Family member not found")

    new_medical_history = MedicalHistory.from_orm(data)
    session.add(new_medical_history)
    await session.commit()
    await session.refresh(new_medical_history)
    return new_medical_history

async def get_medical_history_db(medical_history_id:int, user_id:int,session:AsyncSession):
   # medical_history_id, current_user.id, session
    result = await session.execute(
        select(MedicalHistory).join(FamilyMember).where(
            MedicalHistory.id == medical_history_id,
            FamilyMember.user_id == user_id,
            FamilyMember.is_active == True
        )
    )
    medical_history = result.scalars().all()
    if not medical_history:
        raise HTTPException(status_code=404, detail="medical record not found")

    return medical_history

async def delete_medical_history(medical_history_id: int, user_id: int, session: AsyncSession):
    medical_history = await get_medical_history_db(medical_history_id, user_id, session)
    await session.delete(medical_history)
    await session.commit()  

async def update_medical_history(medical_history_id: int, data: MedicalHistory, user_id: int, session: AsyncSession):
    medical_history = await get_medical_history_db(medical_history_id, user_id, session)
    updated_medical_history= MedicalHistory.from_orm(data)
    session.add(updated_medical_history)
    await session.commit()
    await session.refresh(updated_medical_history)
    # we refresh the health_record instance after committing the changes to the database to ensure that we have the most up-to-date data from the database, including any changes that may have been made by triggers or other processes in the database. This is especially important if there are any fields in the HealthRecord model that are automatically updated by the database, such as a last_updated timestamp or an auto-incrementing version number. By refreshing the instance, we can ensure that we have the latest values for all fields in the health record before returning it to the client.
    return updated_medical_history    


async def get_medical_history_list(
    user_id: int,
    session: AsyncSession,
    family_member_id: int | None = None,
    category: str | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    page: int = 1,
    page_size: int = 10,
    sort_by: str = "created_at",
    sort_order: str = "desc"
):
    allowed_sort_fields = {"created_at", "updated_at", "diagnosed_on"}
    if sort_by not in allowed_sort_fields:
        sort_by = "created_at"
    if sort_order not in ["asc", "desc"]:
        sort_order = "desc"

    query = select(MedicalHistory).join(FamilyMember).where(
        FamilyMember.user_id == user_id,
        FamilyMember.is_active == True
    )

    if family_member_id is not None:
        query = query.where(MedicalHistory.family_member_id == family_member_id)

    if category is not None:
        query = query.where(MedicalHistory.category == category)

    if start_date is not None:
        query = query.where(MedicalHistory.diagnosed_on >= start_date)

    if end_date is not None:
        query = query.where(MedicalHistory.diagnosed_on <= end_date)

    total_result = await session.execute(
        select(func.count(MedicalHistory.id)).select_from(MedicalHistory).join(FamilyMember).where(
            FamilyMember.user_id == user_id,
            FamilyMember.is_active == True
        )
    )
    total = total_result.scalar()

    if sort_order == "desc":
        query = query.order_by(getattr(MedicalHistory, sort_by).desc())
    else:
        query = query.order_by(getattr(MedicalHistory, sort_by).asc())

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

    

    