from fastapi import HTTPException
from sqlmodel import select
from app.models.medications import Medications
from app.models.user import User
from app.models.family_member import FamilyMember
from sqlmodel.ext.asyncio.session import AsyncSession 
  

async def save_medication_to_db(user_id: int, data: Medications, session: AsyncSession):
    # Check if the family member belongs to the user
    family_member = await session.get(FamilyMember, data.family_member_id)
    if not family_member or family_member.user_id != user_id or not family_member.is_active:
        raise HTTPException(status_code=404, detail="Family member not found or does not belong to the user")
    # instead of this we can join the family member table and check if the user_id matches, but this is simpler and more efficient.

    # new_medication = Medications(
    #     family_member_id=data.family_member_id,
    #     name=data.name,
    #     dosage=data.dosage,
    #     frequency=data.frequency,
    #     start_date=data.start_date,
    #     end_date=data.end_date,
    #     notes=data.notes
    # )

    # or 
    new_medication = Medications.from_orm(data)
    
    session.add(new_medication)
    await session.commit()
    await session.refresh(new_medication)
    return new_medication

async def get_medications_from_db(user_id: int, session: AsyncSession):
    result = await session.execute(
        select(Medications).join(FamilyMember).where(
            FamilyMember.user_id == user_id,
            FamilyMember.is_active == True
        )
    )
    if not result:
        raise HTTPException(status_code=404, detail="No medications found for the user")
    medications = result.scalars().all()
    return medications

async def update_medication_in_db(medication_id: int, data: Medications, user_id: int, session: AsyncSession):
    result=await get_medication_db(medication_id, user_id, session)
    # update the medication with the new data
    result.family_member_id = data.family_member_id
    result.medicine_name = data.medicine_name
    result.dosage = data.dosage
    result.frequency = data.frequency
    result.start_date = data.start_date
    result.end_date = data.end_date
    result.notes = data.notes
    await session.commit()
    await session.refresh(result)
    return result

async def delete_medication_in_db(medication_id: int, user_id: int, session: AsyncSession):
    result=await get_medication_db(medication_id, user_id, session)
    await session.delete(result)
    await session.commit()
    return {"detail": "Medication deleted successfully"}
