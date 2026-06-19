from fastapi import HTTPException
from sqlmodel import select
from app.models.medical_history import MedicalHistory
from app.models.family_member import FamilyMember
from app.models.user import User
from sqlmodel.ext.asyncio.session import AsyncSession
from app.dependency import get_current_user
from app.models.family_member import FamilyMember

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


    