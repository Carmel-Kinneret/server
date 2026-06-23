from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, jwk
from jose.utils import base64url_decode
import urllib.request
import json
from pathlib import Path
from dotenv import load_dotenv
import os

# Load .env (project root is 4 levels up from this file)
repo_root = Path(__file__).resolve().parents[4]
load_dotenv(repo_root / ".env")

# Clerk configuration from environment variables
CLERK_ISSUER = os.getenv("CLERK_ISSUER", "")
CLERK_FRONTEND_API = os.getenv("CLERK_FRONTEND_API", "")
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

