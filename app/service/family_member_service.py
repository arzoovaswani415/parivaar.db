from sqlalchemy.ext.asyncio import AsyncSession
from app.models import FamilyMember
from app.models.family_member import FamilyMember
from fastapi import HTTPException
from sqlmodel import select


async def save_family_member_to_db(user_id: int, data: FamilyMember, session: AsyncSession):
    family_member = FamilyMember(
        user_id=user_id,
        name=data.name,
        relation=data.relation,
        date_of_birth=data.date_of_birth,
        gender=data.gender,
        blood_group=data.blood_group,
        allergies=data.allergies,
        chronic_conditions=data.chronic_conditions,
        is_primary=False,
        # to ensure one primary member per user, we can check if there's already a primary member for this user before setting is_primary to true. If data.relation is "self", we can set is_primary to true, but we should also check if there's already a primary member for this user and handle that case (e.g., by raising an error or updating the existing primary member).
        is_active=True
        
    )
    session.add(family_member)
    await session.commit()
    await session.refresh(family_member)
    return family_member

async def get_family_members_from_db(user_id: int, session: AsyncSession):
    result = await session.execute(select(FamilyMember).where(FamilyMember.user_id == user_id, FamilyMember.is_active == True))
    family_members = result.scalars().all()
    return family_members
    

async def update_family_member_in_db(
    member_id: int,
    data: FamilyMember,
    user_id: int,
    session: AsyncSession
):
    result = await session.execute(
        select(FamilyMember).where(
            FamilyMember.id == member_id,
            FamilyMember.user_id == user_id
        )
    )
    family_member = result.scalar_one_or_none()

    if not family_member:
        raise HTTPException(status_code=404, detail="Family member not found")

    # Prevent modifying primary relation
    if family_member.is_primary:
        if data.relation and data.relation.lower() != "self":
            raise HTTPException(
                status_code=400,
                detail="Cannot change primary member relation"
            )

    # Prevent creating another self
    if data.relation and data.relation.lower() == "self":
        raise HTTPException(
            status_code=400,
            detail="Cannot assign 'self' relation"
        )

    # Partial updates
    if data.name is not None:
        family_member.name = data.name

    if data.relation is not None:
        family_member.relation = data.relation

    if data.date_of_birth is not None:
        family_member.date_of_birth = data.date_of_birth

    if data.gender is not None:
        family_member.gender = data.gender

    if data.blood_group is not None:
        family_member.blood_group = data.blood_group

    if data.allergies is not None:
        family_member.allergies = data.allergies

    if data.chronic_conditions is not None:
        family_member.chronic_conditions = data.chronic_conditions

    await session.commit()
    await session.refresh(family_member)

    return family_member

async def delete_family_member_in_db(member_id: int, user_id: int, session: AsyncSession):
    result = await session.execute(
        select(FamilyMember).where(
            FamilyMember.id == member_id,
            FamilyMember.user_id == user_id,
            FamilyMember.is_active == True
        )
    )
    family_member = result.scalar_one_or_none()

    if not family_member:
        raise HTTPException(status_code=404, detail="Family member not found")

    if family_member.is_primary:
        raise HTTPException(status_code=400, detail="Cannot delete primary member")

    family_member.is_active = False
    await session.commit()
    await session.refresh(family_member)

    return family_member

async def get_family_member_by_id(member_id: int, user_id: int, session: AsyncSession):
    result = await session.execute(
        select(FamilyMember).where(
            FamilyMember.id == member_id,
            FamilyMember.user_id == user_id,
            FamilyMember.is_active == True
        )
    )
    family_member = result.scalar_one_or_none()

    if not family_member:
        raise HTTPException(status_code=404, detail="Family member not found")

    return family_member