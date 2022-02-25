from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status, Security, Form
from fastapi.security import (
    OAuth2PasswordBearer,
    OAuth2PasswordRequestForm,
    SecurityScopes,
)
from typing import List, Optional
from jose import JWTError, jwt
from pydantic import ValidationError, EmailStr
from sqlalchemy import and_
from fastapi import UploadFile,  File
from .models import *
from . import db_manager

from api.token.models import *
from api import hashing
# from api.resources import db_manager as resource_manager
from api.db_connect import session, database
# from api.db import UserCompany, Resource, RoleResource, CompanyUserRole
from api.helper import send_email, upload_to_bucket

user_router = APIRouter(prefix="/users", tags=["Users"])

SECRET_KEY = "13d25e094fb36ca2246c818166b7a9563b93f7099f6f0f4caa6cf63b98e8d3f5"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440

scopes = {}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/token")


async def get_current_user(
    security_scopes: SecurityScopes, token: str = Depends(oauth2_scheme)
):
    # print(security_scopes.scopes, token)
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = f"Bearer"
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_scopes = []
        token_data = TokenData(username=username, scopes=token_scopes)
    except Exception as e:
        # print(e)
        raise credentials_exception

    user = await db_manager.get_user_by_username(username)
    if user is None:
        raise credentials_exception
    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not enough permissions",
                headers={"WWW-Authenticate": authenticate_value},
            )
    user_details = UserOut(**user)
    return user_details


async def get_current_active_user(current_user: UserOut = Depends(get_current_user)):
    return current_user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def authenticate_user(username: str, password: str):
    user = await db_manager.get_user_by_username(username)
    if not user:
        return False

    if not hashing.verify_password(password, user.get("user_password")):
        return False
    return UserOut(**user)


@user_router.get("/me/", status_code=status.HTTP_200_OK, response_model=UserOut)
async def read_users_me(current_user: UserOut = Depends(get_current_user)):
    return current_user


@user_router.post("/token/")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    # scopes = await db_manager.get_resources_by_user_email(form_data.username)
    access_token = create_access_token(
        data={
            "sub": user.user_email,
            "scopes": scopes,
            "token_type": "access",
            "id": user.user_id,
        },
        expires_delta=access_token_expires,
    )
    return {"access_token": access_token, "token_type": "bearer", "user": user.user_id}


@user_router.get("/", status_code=status.HTTP_200_OK, response_model=List[UserOut])
async def get_users():
    users = await db_manager.get_users()
    return users


@user_router.post(
    "/", status_code=status.HTTP_201_CREATED, response_model=UserDetailsOut
)
@database.transaction()
async def register(payload: UserDetailsIn):
    payload.user_password = hashing.get_password_hash(payload.user_password)

    user = await db_manager.get_user_by_username(payload.user_email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="User already exists"
        )

    user_id = await db_manager.add_user(payload)
    return {"user_id": user_id}


@user_router.get('/profiles/', status_code=status.HTTP_200_OK,  response_model=List[UserProfileOut])
async def get_user_profiles():
    return await db_manager.get_user_profiles()


@user_router.get('/profiles/{user_profile_id}/', status_code=status.HTTP_200_OK, response_model=UserProfileOut)
async def get_user_profile(user_profile_id: int):
    return await db_manager.get_user_profile(user_profile_id)


@user_router.post('/profiles/', status_code=status.HTTP_201_CREATED, response_model=int)
@database.transaction()
async def create_user_profile(user_profile_in: UserProfileIn):
    return await db_manager.create_user_profile(user_profile_in)


@user_router.patch('/profiles/{user_profile_id}/', status_code=status.HTTP_200_OK, response_model=UserProfileOut)
@database.transaction()
async def update_user_profile(user_profile_id: int, user_profile_in: UserProfileUpdate):
    return await db_manager.update_user_profile(user_profile_id, user_profile_in)


@user_router.get('/profiles/user/{user_id}/', status_code=status.HTTP_200_OK, response_model=UserProfileOut)
async def get_user_profile_by_user(user_id: int):
    return await db_manager.get_user_profile_by_user_id(user_id)


@user_router.post('/resume/{user_id}/', status_code=status.HTTP_201_CREATED)
async def upload_user_resume(user_id: int, resume_file: UploadFile):
    return upload_to_bucket(resume_file, user_id)


@user_router.get('/projects/{user_id}', status_code=status.HTTP_200_OK, response_model=List[ProjectOut])
async def get_user_projects(user_id: int):
    return await db_manager.get_user_projects(user_id)


@user_router.post('/projects/{user_id}', status_code=status.HTTP_201_CREATED, response_model=int)
@database.transaction()
async def create_user_project(user_id: int, project_in: ProjectIn):
    return await db_manager.create_user_project(user_id, project_in)


@user_router.patch('/projects/{project_id}', status_code=status.HTTP_200_OK, response_model=ProjectOut)
@database.transaction()
async def update_user_project(project_id: int, project_in: ProjectUpdate):
    return await db_manager.update_user_project(project_id, project_in)


@user_router.delete('/projects/{project_id}', status_code=status.HTTP_200_OK)
@database.transaction()
async def delete_user_project(project_id: int):
    return await db_manager.delete_user_project(project_id)


@user_router.get("/{user_id}/", status_code=status.HTTP_200_OK, response_model=UserOut)
async def get_user_by_id(user_id: int):
    user = await db_manager.get_user(user_id)
    return user


@user_router.patch("/{user_id}/", status_code=status.HTTP_200_OK)
@database.transaction()
async def update_user(user_id: int, user_update_in: UserUpdateIn):
    return await db_manager.update_user(user_id, user_update_in)


@user_router.patch("/password/change/{user_id}/", status_code=status.HTTP_201_CREATED)
@database.transaction()
async def change_password(
    user_id: int, current_password: str = Form(...), new_password: str = Form(...)
):
    try:
        await db_manager.change_password(user_id, current_password, new_password)
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid password",
        )


@user_router.get("/password/forgot/", status_code=status.HTTP_200_OK)
async def send_email_to_reset_password(user_email: EmailStr):
    user = await db_manager.get_user_by_username(user_email)
    if user:
        message = f"""
            Hey User, we have received a request to reset your password.
            Please click on the link below to reset your password.

            http://localhost:3000/pages/reset-password/{user.get('user_id')}

            If you did not request a password reset, please ignore this email.
        """
        send_email(user_email, "Reset Password", message)  # Not asynchronous
        return
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User does not exist",
        )


@user_router.patch("/password/forgot/{user_id}/", status_code=status.HTTP_200_OK)
@database.transaction()
async def reset_password(user_id: int, password: str = Form(...)):
    return await db_manager.reset_password(user_id, password)


@user_router.post('/apply/{placement_id}/', status_code=status.HTTP_201_CREATED)
@database.transaction()
async def apply_for_placement(
    placement_id: int, user: int = Depends(get_current_active_user),
):
    return await db_manager.apply_for_placement(placement_id, user)
