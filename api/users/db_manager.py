from databases import Database
from pydantic import EmailStr
from sqlalchemy import and_
from api.db import *
from api.db_connect import session, database
from .models import *
from api.helper import send_email, get_file_url_from_bucket
from api.hashing import get_password_hash, verify_password

# from api.db_connect import database
# from api.db import User
# from .models import *
# from api.db import UserCompany, CompanyUserRole, RoleResource, Resource, UserRole
# from api.db_connect import session

# import httpx


async def get_users():
    query = User.select()
    return await database.fetch_all(query=query)


async def add_user(payload: UserDetailsIn):
    query = User.insert().values(**payload.dict())
    return await database.execute(query=query)

    # message = f"""
    #     Hey {payload.user_name}, Please visit this link and verify your email
    #     https://localhost:3000/verify/{user_id}
    # """
    # send_email(payload.user_email, "Verify Email", message)


async def get_user(user_id: int):
    query = User.select(User.c.user_id == user_id)
    return await database.fetch_one(query=query)


async def get_user_by_username(username: EmailStr):
    query = User.select(User.c.user_email == username)
    return await database.fetch_one(query=query)


@database.transaction()
async def update_user(user_id: int, user_update_in: UserUpdateIn):
    try:
        query = (
            User.update()
            .where(User.c.user_id == user_id)
            .values(**user_update_in.dict(exclude_unset=True))
        )
        return await database.execute(query)
    except Exception as e:
        raise Exception(e)


async def change_password(user_id: int, current_password: str, new_password: str):
    query = User.select(User.c.user_id == user_id)
    user = await database.fetch_one(query=query)

    if verify_password(current_password, user.get("user_password")):
        new_password = get_password_hash(new_password)
        query = User.update(user_id=user_id).values(user_password=new_password)
        return await database.execute(query=query)
    else:
        raise Exception("Current password is incorrect")


async def reset_password(user_id: int, password: str):
    new_password = get_password_hash(password)
    query = User.update(User.c.user_id == user_id).values(
        user_password=new_password)
    return await database.execute(query=query)


async def apply_for_placement(placement_id, user):
    query = Placements.select(Placements.c.placement_id == placement_id)
    placement = await database.fetch_one(query=query)

    query = PlacementUserLinking.insert().values(
        placement_id=placement_id, user_id=user.get("user_id"))
    return await database.execute(query=query)


async def get_user_profiles():
    query = UserProfile.select()
    return await database.fetch_all(query=query)


async def get_user_profile(user_profile_id: int):
    query = UserProfile.select(
        UserProfile.c.user_profile_id == user_profile_id)
    data = dict(await database.fetch_one(query=query))
    resume_url = get_file_url_from_bucket(
        'kmv-placements', data['resume_path'])
    data['resume_path'] = resume_url
    return data


async def get_user_profile_by_user_id(user_id: int):
    query = UserProfile.join(
        User, User.c.user_id == UserProfile.c.user_id, isouter=True).select(UserProfile.c.user_id == user_id)
    data = dict(await database.fetch_one(query=query))
    resume_url = get_file_url_from_bucket(
        'kmv-placements', data['resume_path'])
    data['resume_path'] = resume_url
    return data


async def create_user_profile(user_profile_in: UserProfileIn):
    query = UserProfile.insert().values(**user_profile_in.dict())
    return await database.execute(query=query)


async def update_user_profile(user_profile_id: int, user_profile_update_in: UserProfileUpdate):
    try:
        query = (
            UserProfile.update()
            .where(UserProfile.c.user_profile_id == user_profile_id)
            .values(**user_profile_update_in.dict(exclude_unset=True))
        )
        return await database.execute(query=query)
    except Exception as e:
        raise Exception(e)


async def get_user_projects(user_id: int):
    query = Projects.select().where(Projects.c.created_by == user_id)
    return await database.fetch_all(query=query)


async def create_user_project(user_id: int, project_in: ProjectIn):
    query = Projects.select().where(Projects.c.project_name ==
                                    project_in.project_name, Projects.c.created_by == user_id, Projects.c.project_url == project_in.project_url)
    project = await database.fetch_one(query=query)
    if not project:
        query = Projects.insert().values(**project_in.dict())
        return await database.execute(query=query)


async def delete_user_project(project_id: int):
    query = Projects.delete().where(Projects.c.project_id == project_id)
    return await database.execute(query=query)
