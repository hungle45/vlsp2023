from typing import Annotated, Union, Optional

from fastapi import APIRouter, HTTPException, status, Body, Depends, Request
from fastapi.security import OAuth2PasswordBearer

from core.models.users import users_db, get_user_by_email
from core.schemas.users import UserSchema
from core.auth import decode_access_token

class OAuth2PasswordJWT(OAuth2PasswordBearer):
    def __init__(
        self,
        tokenUrl: str,
        scheme_name: Optional[str] = None,
        scopes: Optional[dict] = None,
        auto_error: bool = True,
    ):
        super().__init__(
            tokenUrl=tokenUrl,
            scopes=scopes,
            scheme_name=scheme_name,
            auto_error=auto_error,
        )

    async def __call__(self, request: Request) -> Optional[str]:
        authorization: str = request.headers.get("access_token")
        if not authorization:
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated",
                    headers={"WWW-Authenticate": "JWT"},
                )
            else:
                return None
        return authorization

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
oauth2_scheme = OAuth2PasswordJWT(tokenUrl="login")

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, 
        headers={"WWW-Authenticate": "Bearer"}
    )
    try:
        payload = decode_access_token(token)
        user = UserSchema(**get_user_by_email(payload['email']))
        return user
    except:
        raise credentials_exception
    
current_user_dependency = Depends(get_current_user)