from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from app.models import User,FamilyMember
from app.security import hash_password

async def get_user_by_email(session: AsyncSession, email: str) -> User | None:
    result = await session.exec(
        select(User).where(User.email == email)
    )
    return result.first()

async def get_user_by_id(session: AsyncSession, user_id: int) -> User | None:
    result = await session.exec(
        select(User).where(User.id == user_id)
    )
    return result.first()

async def create_new_user(session: AsyncSession, data: User) -> User:
    new_user = User(
        name=data.name,
        email=data.email,
        password_hash=hash_password(data.password)
    )
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    # what about other parameters like allergies 
    self_member = FamilyMember(
        user_id=new_user.id,
        name=new_user.name,
        relation="self",
        is_primary=True
    )
    session.add(self_member)
    await session.commit()
    return new_user