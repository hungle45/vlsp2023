from typing import Annotated, Union

from fastapi import APIRouter, HTTPException, status, Body, Depends
from fastapi.security import OAuth2PasswordRequestForm

from core.schemas.users import UserSchema
from core.auth import authenticate_user, create_access_token
from core.dependencies import current_user_dependency

# router
users_router = APIRouter(tags=['users'])

# @users_router.post('/token')
# async def login(
#     form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
# ):
#     user = authenticate_user(form_data.username, form_data.password)
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Incorrect username or password",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
#     access_token = create_access_token({'email': form_data.username})
#     return {'access_token': access_token, 'token_type': 'bearer'}


@users_router.post('/login')
async def login(
    form_data: Annotated[UserSchema, Body()]
):
    try:
        user = authenticate_user(form_data.email, form_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token = create_access_token({'email': form_data.email})
        return {
            'status': 1,
            'result': {
                'access_token': access_token
            }
        }
    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )


# @users_router.get('/users/me')
# async def get_users_me(
#     current_user: Annotated[UserSchema, current_user_dependency]
# ):
#     return current_user