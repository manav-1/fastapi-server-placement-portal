from pydantic import BaseModel, EmailStr
from typing import List, Optional

from api.db import UserRole

# from api.db import UserStatusEnum


class UserBase(BaseModel):
    user_name: str
    user_email: EmailStr
    user_mobile: int


class UserOut(UserBase):
    user_id: int
    user_role: UserRole
    # user_status: UserStatusEnum


class UserDetailsIn(UserBase):
    user_password: str
    user_role: UserRole


class UserProfileIn(BaseModel):
    user_id: int
    stream_id: int
    marks_10: float
    marks_12: float
    marks_ug: float
    additional_info: str
    resume_name: str
    resume_path: str


class UserProfileOut( UserProfileIn):
    user_profile_id: int


class UserProfileUpdate(BaseModel):
    user_id: Optional[int]
    stream_id: Optional[int]
    marks_10: Optional[float]
    marks_12: Optional[float]
    marks_ug: Optional[float]
    additional_info: Optional[str]
    resume_name: Optional[str]
    resume_path: Optional[str]


class UserDetailsOut(BaseModel):
    user_id: int


class UserDetailsAll(UserBase):
    user_id: int
    # user_status: UserStatusEnum
    user_password: str


class UserUpdateIn(BaseModel):
    user_name: Optional[str]
    user_email: Optional[EmailStr]
    user_mobile: Optional[int]
    # user_status: Optional[UserStatusEnum]


# send it as form data
class UserChangePasswordIn(BaseModel):
    user_id: int
    current_password: str
    new_password: str


class TokenData(BaseModel):
    username: str
    scopes: List[str] = []


class ProjectIn(BaseModel):
    project_name: str
    project_url: str
    created_by: int


class ProjectOut(ProjectIn):
    project_id: int


class ProjectUpdate(BaseModel):
    project_id: int
    project_name: Optional[str]
    project_url: Optional[str]
