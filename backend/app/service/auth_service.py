from datetime import datetime, timedelta
from uuid import uuid4
from app.models.user import User
from app.models.password_reset_token import Password_Reset_Token
from sqlmodel.ext.asyncio.session import AsyncSession
from app.database import get_session
from sqlmodel import select
from app.models.refresh_token import RefreshToken
from app.jwt import create_refresh_token, REFRESH_TOKEN_EXPIRE_DAYS



async def create_password_reset_token(user: User, session: AsyncSession) -> str:
    token = str(uuid4())
    expires_at = datetime.utcnow() + timedelta(minutes=15)  # Token valid for 15 minutes ( we also can do 15 * 60 to make it in seconds)

    password_reset_token = Password_Reset_Token(
        user_id=user.id,
        token=token,
        expires_at=expires_at
    )
    session.add(password_reset_token)
    await session.commit()

    return token

# if we would have made this boolean we had to write 2 queries one to check if the token is valid and another to mark it as used. by returning the object of password reset token we can mark it as used in the same query
async def validate_token(token: str, session: AsyncSession) -> Password_Reset_Token | None:
    # result = await session.execute(
    #     "SELECT * FROM password_reset_token WHERE token = :token && expires_at > :now",
    #     {"token": token, "now": datetime.utcnow()}
    # )
    result = await session.exec(
        select(Password_Reset_Token).where(
            Password_Reset_Token.token == token,
            Password_Reset_Token.expires_at > datetime.utcnow(),
            Password_Reset_Token.is_used == False
        )
    )
    return result.first()

async def create_and_store_reset_token(user_id:int, session: AsyncSession) -> str:
    token = create_refresh_token()

    refresh_token = RefreshToken(
        user_id=user_id,
        token=token,
        expires_at=datetime.utcnow()+timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)  # Token valid for 7 days
    )
    session.add(refresh_token)
    await session.commit()

    return token

async def refresh_token_service(token: str, session: AsyncSession):
    result = await session.exec(
        select(RefreshToken).where(RefreshToken.token == token)
    )
    return result.first()

    # eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3IiwiZXhwIjoxNzc0NTY0NjA3fQ.v464lukJ68KThH-uUWu06NI6LYicQmaNDS2YIlQaUEs

    # eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3IiwiZXhwIjoxNzc0NTY0NTkzfQ.4Y7Yxq1r16yCiEmnKZJYWEC_caawfGFv3lKf7JTG7wI

    