from datetime import datetime, timedelta
from jose import jwt
import secrets

SECRET_KEY = "your-secret-key"  
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7


def create_access_token(user_id: int):
    payload = {
        "sub": str(user_id),
        # "sub" stands for subject which means the main thing this token is about. In our case, it's the user ID.
        # we convert user_id to string because JWT expects the payload to be JSON serializable, and integers are fine, but it's a common convention to use strings for IDs in JWTs.
        # example payload: {"sub": "123", "exp": 1700000000}
        "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    }
    
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str):
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

def create_refresh_token():
   return secrets.token_urlsafe(64)