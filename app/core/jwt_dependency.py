from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional

security = HTTPBearer(auto_error=False)


def get_optional_token(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
):
    if credentials:
        return credentials.credentials

    return None