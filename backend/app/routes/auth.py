from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlmodel.ext.asyncio.session import AsyncSession
from datetime import datetime
from app.database import get_session
from app.service.user_service import get_user_by_email, get_user_by_id
from app.security import verify_password, hash_password
from app.service.auth_service import create_password_reset_token, validate_token, create_and_store_reset_token,refresh_token_service
from app.service.email_service import send_password_reset_email
from app.jwt import create_access_token
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(prefix="/auth")

# Pydantic models for request bodies we write these here because we want to have a clear structure for the data we expect from the client. This also allows us to easily validate the incoming data and provide clear error messages if the data is not in the expected format. For example, if the email is not a valid email address, Pydantic will automatically raise a validation error.
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

class ForgotPassword(BaseModel):
    email: EmailStr

class RefreshTokenRequest(BaseModel):
    refresh_token: str

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), session: AsyncSession = Depends(get_session)):
    user = await get_user_by_email(session, form_data.username)

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(user.id)
    refresh_token = await create_and_store_reset_token(user.id, session)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/forgot-password")
async def forgot_password(data: ForgotPassword, session: AsyncSession = Depends(get_session)):
    user = await get_user_by_email(session, data.email)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Generate a password reset token and send it via email
    token = await create_password_reset_token(user, session)
    await send_password_reset_email(user.email, token)

    return {"message": "Password reset email sent"}


@router.post("/reset-password")
async def reset_password(data: ResetPasswordRequest, session: AsyncSession = Depends(get_session)):
    # This endpoint will be called by the Frontend after the user clicks the reset link in their email
    # The Frontend should send the token and the new password to this endpoint
    # You would need to implement logic here to validate the token, check its expiration, and update the user's password
    token_data = await validate_token(data.token, session)
    if token_data:
        user = await get_user_by_id(session, token_data.user_id)
        user.password_hash =  hash_password(data.new_password)
        token_data.is_used = True
        session.add(user)
        session.add(token_data)
        await session.commit()
        return {"message": "Password reset successful"}
    else:
        raise HTTPException(status_code=400, detail="Invalid or expired token")


@router.post("/refresh")
async def refresh_token(data: RefreshTokenRequest, session: AsyncSession = Depends(get_session)):
    token_record = await refresh_token_service(data.refresh_token, session)

    # # scalar_one_or_none is a method provided by SQLAlchemy (and by extension, SQLModel) that is used to retrieve a single scalar value from the result of a query. It returns the value if exactly one row is returned, None if no rows are returned, and raises an exception if more than one row is returned. In this context, it is used to fetch the refresh token record from the database based on the provided refresh token string.
    # token_record = result.scalar_one_or_none()
   
    if not token_record:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    if not token_record.is_active or token_record.expires_at < datetime.utcnow():
        raise HTTPException(status_code=401, detail="Token expired")

    new_access_token = create_access_token(token_record.user_id)

    return {"access_token": new_access_token}

# refresh token rotation (remaining) - when the user uses the refresh token to get a new access token, we can also generate a new refresh token and invalidate the old one. This way, if a refresh token is compromised, it can only be used once before it becomes invalid. To implement this, we would need to modify the refresh_token endpoint to generate a new refresh token and update the database record for the old refresh token to mark it as inactive. We would also need to return the new refresh token to the client so that it can be used for future refresh requests.

@router.post("/logout")
async def logout(refresh_token: str, session: AsyncSession = Depends(get_session)):
    
    result = await session.execute(
        select(RefreshToken).where(RefreshToken.token == refresh_token)
    )
    token_record = result.scalar_one_or_none()

    if token_record:
        token_record.is_active = False
        session.add(token_record)
        await session.commit()

    return {"message": "Logged out successfully"}
    # The Frontend (React/Angular) simply deletes the Access Token from its local storage or cookies.
