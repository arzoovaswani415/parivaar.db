from fastapi import APIRouter, Depends, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from app.dependency import get_current_user
from app.database import get_session
from app.schemas.family_schema import FamilyCreate, FamilyOut, FamilyUpdate, FamilyJoinRequest
from app.service.family_service import create_family, get_family_by_id, update_family_name, get_family_by_code, join_family

router = APIRouter(prefix="/family", tags=["family"])


@router.post("/create", response_model=FamilyOut)
async def create_family_endpoint(data: FamilyCreate, session: AsyncSession = Depends(get_session), current_user=Depends(get_current_user)):
    if current_user.family_id is not None:
        raise HTTPException(status_code=409, detail="User already belongs to a family.")
    try:
        new_family = await create_family(session, current_user, data.family_name)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # build output
    family = await get_family_by_id(session, new_family.id)
    # load members and users
    members = []
    users = []
    for fm in family.family_members:
        members.append(fm)
        if fm.linked_user_id:
            users.append(fm.user)

    return {
        "id": family.id,
        "family_name": family.family_name,
        "family_code": family.family_code,
        "owner_user_id": family.owner_user_id,
        "members": members,
        "users": users
    }


@router.get("/me", response_model=FamilyOut)
async def get_my_family(session: AsyncSession = Depends(get_session), current_user=Depends(get_current_user)):
    if not current_user.family_id:
        raise HTTPException(status_code=404, detail="User does not belong to a family")

    family = await get_family_by_id(session, current_user.family_id)
    if not family:
        raise HTTPException(status_code=404, detail="Family not found")

    members = []
    users = []
    for fm in family.family_members:
        members.append(fm)
        if fm.linked_user_id:
            users.append(fm.user)

    return {
        "id": family.id,
        "family_name": family.family_name,
        "family_code": family.family_code,
        "owner_user_id": family.owner_user_id,
        "members": members,
        "users": users
    }


@router.put("/update")
async def update_family_endpoint(data: FamilyUpdate, session: AsyncSession = Depends(get_session), current_user=Depends(get_current_user)):
    if not current_user.family_id:
        raise HTTPException(status_code=404, detail="User does not belong to a family")

    family = await get_family_by_id(session, current_user.family_id)
    if not family:
        raise HTTPException(status_code=404, detail="Family not found")

    # Only owner can update
    if family.owner_user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only owner can update family")

    if data.family_name:
        family = await update_family_name(session, family, data.family_name)

    members = []
    users = []
    for fm in family.family_members:
        members.append(fm)
        if fm.linked_user_id:
            users.append(fm.user)

    return {
        "id": family.id,
        "family_name": family.family_name,
        "family_code": family.family_code,
        "owner_user_id": family.owner_user_id,
        "members": members,
        "users": users
    }


@router.post("/join")
async def join_family_endpoint(data: FamilyJoinRequest, session: AsyncSession = Depends(get_session)):
    from app.models.user import User
    from sqlmodel import select
    existing_user_q = await session.exec(select(User).where(User.email == data.email))
    existing_user = existing_user_q.first()
    if existing_user and existing_user.family_id is not None:
        raise HTTPException(status_code=409, detail="User already belongs to a family.")

    family = await get_family_by_code(session, data.family_code)
    if not family:
        raise HTTPException(status_code=404, detail="Family not found")

    try:
        new_user = await join_family(session, family, data.email, data.phone_number, data.name, data.password)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {"status": "success", "user_id": new_user.id}
