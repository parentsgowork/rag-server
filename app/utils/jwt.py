from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from app.core.config import settings
from datetime import datetime, timezone

bearer_scheme = HTTPBearer(auto_error=True)


def verify_jwt(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
):
    token = credentials.credentials
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_bytes,
            algorithms=[settings.JWT_ALGORITHM],
        )

        # 토큰 만료 검사 (timezone-aware 방식)
        if "exp" in payload and datetime.fromtimestamp(
            payload["exp"], tz=timezone.utc
        ) < datetime.now(timezone.utc):
            raise HTTPException(status_code=401, detail="Access token expired")

        return payload

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid access token")
