# This is similar to Spring Boot security configuration, we can use this to define dependencies for our routes
# it mainly uses OAuth2PasswordBearer which is a pre-built class provided by FastAPI to handle token-based authentication. It expects a token to be sent in the Authorization header of the request, and it will automatically extract the token for us.
# How OAuth2PasswordBearer Works
# When you add token: str = Depends(oauth2_scheme) to your function:
# Extraction: FastAPI automatically looks at the incoming request headers. 
# Validation: It searches for the key Authorization. 
# Parsing: It checks if the value starts with Bearer . If it does, it strips that word away and gives you just the token string. 
# Auto-Error: If the header is missing or doesn't say "Bearer," FastAPI immediately sends a 401 Unauthorized response. You don't even have to write the if statement!

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlmodel.ext.asyncio.session import AsyncSession

from app.database import get_session
from app.jwt import decode_token
from app.service.user_service import get_user_by_id

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


async def get_current_user(token: str = Depends(oauth2_scheme), session: AsyncSession = Depends(get_session)):
    try:
        payload = decode_token(token)
        user_id = int(payload.get("sub"))
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = await get_user_by_id(session, user_id)

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user