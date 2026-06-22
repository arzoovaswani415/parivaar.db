from app.dependency import get_current_user
from fastapi import APIRouter
from pydantic import BaseModel
from datetime import date
from sqlmodel.ext.asyncio.session import AsyncSession
from app.database import get_session
from app.service.family_member_service import save_family_member_to_db
from app.models.user import User
from app.models.family_member import FamilyMember
from app.service.family_member_service import get_family_members_from_db, update_family_member_in_db, delete_family_member_in_db
from fastapi import Depends, HTTPException

router = APIRouter(prefix="/family-members")

class FamilyMemberCreate(BaseModel):
    name: str
    relation: str  # self, father, mother, child
    date_of_birth: date | None = None
    gender: str | None = None
    blood_group: str | None = None
    allergies: str | None = None
    chronic_conditions: str | None = None
    phone_number: str | None = None
    email: str | None = None


@router.get("/get_all")
async def get_family_members(current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    # User = await get_current_user()
    # Calls function manually (no token passed)
    # Returns None or error because get_current_user expects a token in the header and we are not providing it here.
    # instead we will do current_user = Depends(get_current_user)
    # in this FastAPI injects dependency + extracts token from header
    # Returns TokenData with user_id, then we can use that user_id to fetch family members from the database.
    
    user_id = current_user.id
    family_members = await get_family_members_from_db(user_id, session)
    return {"family_members": family_members}

@router.post("/create")
async def create_family_member(data: FamilyMemberCreate, current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    user_id = current_user.id
    new_family_member = await save_family_member_to_db(user_id, data, session)
    return new_family_member

@router.put("/{member_id}")
async def update_family_member(member_id: int, data: FamilyMemberCreate, current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    user_id = current_user.id
    new_family_member = await update_family_member_in_db(member_id, data, user_id, session)
    return new_family_member

@router.put("/{member_id}/delete")
async def delete_family_member(member_id: int, current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    user_id = current_user.id
    new_family_member = await delete_family_member_in_db(member_id, user_id, session)
    return new_family_member
