from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from app.database import get_session
from app.models.user import User
from app.models.family_member import FamilyMember
from pydantic import BaseModel, EmailStr
from app.security import hash_password
from app.dependency import get_current_user
from app.jwt import create_access_token
from app.dependency import get_current_user
from app.service.user_service import create_new_user


# This file defines the API routes related to user management. It includes a Pydantic model for user creation and an APIRouter to handle user-related endpoints.

router = APIRouter(prefix="/users")


# This is a Pydantic model. It defines what data the user must send to your API.
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

# APIRouter: A way to split your app into smaller, manageable files.
# Prefix: Saves you from typing /users over and over.
# BaseModel: A "Contract" that tells the user exactly what data they need to send.

from typing import Annotated

# Creating a shortcut for our session dependency
SessionDep = Annotated[AsyncSession, Depends(get_session)]

@router.post("/create") # This becomes POST /users/
async def create_user(user_data: UserCreate, session: SessionDep):
    # 1. user_data is automatically checked against the UserCreate model
    # 2. session is automatically provided by get_session
    new_user = await create_new_user(session, user_data)
    return new_user

@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user
 