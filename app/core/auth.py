from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, jwk
from jose.utils import base64url_decode
import urllib.request
import json
from app.core.config import settings
from app.core.exceptions import UnauthorizedException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.database import get_db
from app.models.user import User

security = HTTPBearer()

def get_jwks():
    if not settings.CLERK_ISSUER:
        raise ValueError("CLERK_ISSUER environment variable is not set")
    jwks_url = f"{settings.CLERK_ISSUER}/.well-known/jwks.json"
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
                audience=settings.CLERK_FRONTEND_API,
                issuer=settings.CLERK_ISSUER
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
        # Optionally create user if not found, or raise exception
        raise UnauthorizedException(message="User not found in database.")
    
    return user
