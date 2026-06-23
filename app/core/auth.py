from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, jwk
from jose.utils import base64url_decode
import urllib.request
import json
from pathlib import Path
from dotenv import load_dotenv
import os

import base64

# Locate and load .env recursively searching up the directory tree
current_dir = Path(__file__).resolve().parent
while current_dir != current_dir.parent:
    env_path = current_dir / ".env"
    if env_path.exists():
        load_dotenv(env_path)
        break
    current_dir = current_dir.parent
else:
    load_dotenv()

CLERK_PUBLISHABLE_KEY = os.getenv("CLERK_PUBLISHABLE_KEY", "")
CLERK_SECRET_KEY = os.getenv("CLERK_SECRET_KEY", "")

# Extract frontend api and issuer from publishable key if not set explicitly
derived_frontend_api = ""
if CLERK_PUBLISHABLE_KEY:
    try:
        parts = CLERK_PUBLISHABLE_KEY.split("_")
        if len(parts) >= 3:
            encoded_part = parts[2]
            missing_padding = len(encoded_part) % 4
            if missing_padding:
                encoded_part += "=" * (4 - missing_padding)
            decoded = base64.b64decode(encoded_part).decode("utf-8")
            if decoded.endswith("$"):
                decoded = decoded[:-1]
            derived_frontend_api = decoded
    except Exception:
        pass

CLERK_FRONTEND_API = os.getenv("CLERK_FRONTEND_API", derived_frontend_api)
CLERK_ISSUER = os.getenv("CLERK_ISSUER", f"https://{CLERK_FRONTEND_API}" if CLERK_FRONTEND_API else "")
from app.core.exceptions import UnauthorizedException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.database import get_db
from app.models.user import User

from typing import Optional
from app.models.user import User, Role
from app.core.exceptions import ForbiddenException

security = HTTPBearer()
security_optional = HTTPBearer(auto_error=False)

def get_jwks():
    if not CLERK_ISSUER:
        raise ValueError("CLERK_ISSUER environment variable is not set")
    jwks_url = f"{CLERK_ISSUER}/.well-known/jwks.json"
    response = urllib.request.urlopen(jwks_url)
    return json.loads(response.read())

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        # Get the unverified header
        unverified_header = jwt.get_unverified_header(token)
        
        # Get JWKS
        jwks = get_jwks()
        
        # Find the matching key
        rsa_key = {}
        for key in jwks["keys"]:
            if key["kid"] == unverified_header["kid"]:
                rsa_key = {
                    "kty": key["kty"],
                    "kid": key["kid"],
                    "use": key["use"],
                    "n": key["n"],
                    "e": key["e"]
                }
        
        if rsa_key:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=["RS256"],
                audience=CLERK_FRONTEND_API,
                issuer=CLERK_ISSUER
            )
            return payload
        raise UnauthorizedException(message="Unable to find appropriate key.")
        
    except jwt.ExpiredSignatureError:
        raise UnauthorizedException(message="Token has expired.")
    except jwt.JWTClaimsError:
        raise UnauthorizedException(message="Incorrect claims.")
    except Exception as e:
        raise UnauthorizedException(message=f"Could not parse token: {str(e)}")

async def get_current_user(
    token_payload: dict = Depends(verify_token),
    db: AsyncSession = Depends(get_db)
) -> User:
    clerk_id = token_payload.get("sub")
    if not clerk_id:
        raise UnauthorizedException(message="Token missing subject.")
    
    result = await db.execute(select(User).where(User.clerkId == clerk_id))
    user = result.scalars().first()
    
    if not user:
        username = token_payload.get("username") or token_payload.get("name") or ""
        if not username:
            # Fallback to email prefix or a portion of clerk_id
            email = token_payload.get("email") or ""
            username = email.split("@")[0] if email else f"user_{clerk_id[-8:]}"
        # Truncate username to 50 chars to avoid constraint violation
        username = username[:50]
        user = User(clerkId=clerk_id, role=Role.USER, userName=username)
        db.add(user)
        await db.commit()
        await db.refresh(user)
    
    return user

async def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_optional),
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    if not credentials:
        return None
    try:
        token_payload = await verify_token(credentials)
        clerk_id = token_payload.get("sub")
        if not clerk_id:
            return None
        
        result = await db.execute(select(User).where(User.clerkId == clerk_id))
        user = result.scalars().first()
        
        if not user:
            username = token_payload.get("username") or token_payload.get("name") or ""
            if not username:
                email = token_payload.get("email") or ""
                username = email.split("@")[0] if email else f"user_{clerk_id[-8:]}"
            username = username[:50]
            user = User(clerkId=clerk_id, role=Role.USER, userName=username)
            db.add(user)
            await db.commit()
            await db.refresh(user)
        return user
    except Exception:
        return None

async def get_current_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    if current_user.role != Role.ADMIN:
        raise ForbiddenException(message="Admin role check failed: Access denied.")
    return current_user

