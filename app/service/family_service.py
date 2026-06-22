from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from app.models import Family, FamilyMember, User
from app.security import hash_password
from datetime import datetime
from typing import Optional


async def generate_family_code() -> str:
    # Format: FAM-XXXXXX using uuid
    import uuid
    code = uuid.uuid4().hex.upper()[0:6]
    return f"FAM-{code}"


async def create_family(session: AsyncSession, current_user: User, family_name: str) -> Family:
    # Verify user does not already own a family
    result = await session.exec(select(Family).where(Family.owner_user_id == current_user.id))
    existing = result.first()
    if existing:
        raise ValueError("User already owns a family")

    # generate unique family_code
    while True:
        family_code = await generate_family_code()
        q = await session.exec(select(Family).where(Family.family_code == family_code))
        if not q.first():
            break

    new_family = Family(family_name=family_name, family_code=family_code, owner_user_id=current_user.id)
    session.add(new_family)
    await session.commit()
    await session.refresh(new_family)

    # Update current_user.family_id
    current_user.family_id = new_family.id
    session.add(current_user)
    await session.commit()

    # Create self FamilyMember if not exists
    fm_q = await session.exec(
        select(FamilyMember).where(
            FamilyMember.family_id == new_family.id,
            FamilyMember.linked_user_id == current_user.id
        )
    )
    fm = fm_q.first()
    if not fm:
        self_member = FamilyMember(
            user_id=current_user.id,
            linked_user_id=current_user.id,
            name=current_user.name,
            relation="self",
            is_primary=True,
            phone_number=None,
            family_id=new_family.id,
            email=current_user.email,
            invite_status="accepted"
        )
        session.add(self_member)
        await session.commit()

    return new_family


async def get_family_by_id(session: AsyncSession, family_id: int) -> Optional[Family]:
    result = await session.exec(select(Family).where(Family.id == family_id))
    return result.first()


async def get_family_by_code(session: AsyncSession, family_code: str) -> Optional[Family]:
    result = await session.exec(select(Family).where(Family.family_code == family_code))
    return result.first()


async def update_family_name(session: AsyncSession, family: Family, new_name: str) -> Family:
    family.family_name = new_name
    family.updated_at = datetime.utcnow()
    session.add(family)
    await session.commit()
    await session.refresh(family)
    return family


async def join_family(session: AsyncSession, family: Family, email: str, phone_number: str, name: str, password: str) -> User:
    # Find FamilyMember by family_id and email
    fm_q = await session.exec(
        select(FamilyMember).where(
            FamilyMember.family_id == family.id,
            FamilyMember.email == email
        )
    )
    family_member = fm_q.first()
    if not family_member:
        raise ValueError("Family member not found")

    # Validate phone number
    if (family_member.phone_number or "") != phone_number:
        raise ValueError("Phone number does not match")

    # Check linked_user_id
    if family_member.linked_user_id is not None:
        raise ValueError("Family member already joined")

    # Check user email uniqueness
    existing_user_q = await session.exec(select(User).where(User.email == email))
    if existing_user_q.first():
        raise ValueError("Email already registered")

    # Create User
    user_name = name if name else family_member.name
    new_user = User(name=user_name, email=email, password_hash=hash_password(password), family_id=family.id)
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)

    # Update FamilyMember
    family_member.linked_user_id = new_user.id
    family_member.invite_status = "accepted"
    session.add(family_member)
    await session.commit()

    return new_user
