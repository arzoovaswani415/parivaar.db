from sqlalchemy.ext.asyncio import AsyncSession
from app.models import FamilyMember
from app.models.family_member import FamilyMember
from fastapi import HTTPException
from sqlmodel import select


async def save_family_member_to_db(user_id: int, data: FamilyMember, session: AsyncSession):
    if data.relation and data.relation.lower() == "self":
        raise HTTPException(status_code=400, detail="Cannot manually create a family member with relation 'self'.")

    from app.models.user import User
    user = await session.get(User, user_id)
    family_id = user.family_id if user else None

    email = getattr(data, "email", None)
    if email:
        # Check 1: User already registered in another family
        existing_user_q = await session.execute(
            select(User).where(User.email == email)
        )
        existing_user = existing_user_q.scalar_one_or_none()
        if existing_user and existing_user.family_id and existing_user.family_id != family_id:
            raise HTTPException(
                status_code=400,
                detail="This email is already associated with another family."
            )

        # Check 2: Already invited elsewhere
        existing_member_q = await session.execute(
            select(FamilyMember).where(FamilyMember.email == email)
        )
        existing_member = existing_member_q.scalar_one_or_none()
        if existing_member and existing_member.family_id != family_id:
            raise HTTPException(
                status_code=400,
                detail="This email has already been invited to another family."
            )

    family_member = FamilyMember(
        user_id=user_id,
        family_id=family_id,
        name=data.name,
        relation=data.relation,
        date_of_birth=data.date_of_birth,
        gender=data.gender,
        blood_group=data.blood_group,
        allergies=data.allergies,
        chronic_conditions=data.chronic_conditions,
        phone_number=getattr(data, "phone_number", None),
        email=getattr(data, "email", None),
        is_primary=False,
        is_active=True
    )
    session.add(family_member)
    await session.commit()
    await session.refresh(family_member)
    return family_member

async def get_family_members_from_db(user_id: int, session: AsyncSession):
    from app.models.user import User
    user = await session.get(User, user_id)
    if user and user.family_id:
        result = await session.execute(
            select(FamilyMember).where(
                FamilyMember.family_id == user.family_id,
                FamilyMember.is_active == True
            )
        )
    else:
        result = await session.execute(
            select(FamilyMember).where(
                FamilyMember.user_id == user_id,
                FamilyMember.is_active == True
            )
        )
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

    if hasattr(data, "phone_number") and data.phone_number is not None:
        family_member.phone_number = data.phone_number

    if hasattr(data, "email") and data.email is not None:
        email = data.email
        if email:
            from app.models.user import User
            existing_user_q = await session.execute(
                select(User).where(User.email == email)
            )
            existing_user = existing_user_q.scalar_one_or_none()
            if existing_user and existing_user.family_id and existing_user.family_id != family_member.family_id:
                raise HTTPException(
                    status_code=400,
                    detail="This email is already associated with another family."
                )

            existing_member_q = await session.execute(
                select(FamilyMember).where(
                    FamilyMember.email == email,
                    FamilyMember.id != member_id
                )
            )
            existing_member = existing_member_q.scalar_one_or_none()
            if existing_member and existing_member.family_id != family_member.family_id:
                raise HTTPException(
                    status_code=400,
                    detail="This email has already been invited to another family."
                )
        family_member.email = data.email

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