from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime


class FamilyCreate(BaseModel):
    family_name: str


class FamilyUpdate(BaseModel):
    family_name: Optional[str] = None


class FamilyMemberOut(BaseModel):
    id: int
    name: str
    relation: str
    date_of_birth: Optional[datetime] = None
    gender: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[EmailStr] = None
    linked_user_id: Optional[int] = None
    invite_status: Optional[str] = None
    is_primary: bool

    class Config:
        orm_mode = True


class FamilyUserOut(BaseModel):
    id: int
    name: str
    email: EmailStr

    class Config:
        orm_mode = True


class FamilyOut(BaseModel):
    id: int
    family_name: str
    family_code: str
    owner_user_id: int
    members: List[FamilyMemberOut] = []
    users: List[FamilyUserOut] = []

    class Config:
        orm_mode = True


class FamilyJoinRequest(BaseModel):
    family_code: str
    email: EmailStr
    phone_number: str
    name: str
    password: str
