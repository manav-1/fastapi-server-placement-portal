from fastapi import APIRouter, status, Security, Body
from typing import List, Optional
from fastapi import UploadFile, File
from .models import *
from . import db_manager
from api.db_connect import database
from api.users.views import  get_current_active_user
from api.users.models import  *
from  api.db import UserRole
from fastapi import  Depends

placement_router = APIRouter(prefix="/placements", tags=["Placements"])


@placement_router.post("/", response_model=int, status_code=status.HTTP_201_CREATED)
@database.transaction()
async def create_placement(placement: Placement):
    """
    Create a placement
    """
    return await db_manager.create_placement(placement)


@placement_router.get("/", response_model=List[PlacementOut])
async def get_placements(current_user: UserOut = Depends(get_current_active_user)):
    """
    Get all placements according to user
    """
    print(current_user.user_role)
    if  current_user.user_role == UserRole.ADMIN:
        return await db_manager.get_placements()
    return await db_manager.get_placements_acc_to_user(current_user)


@placement_router.get("/{placement_id}", response_model=PlacementOut)
async def get_placement(placement_id: int):
    """
    Get a placement by id
    """
    return await db_manager.get_placement(placement_id)


@placement_router.put("/{placement_id}", response_model=Placement)
@database.transaction()
async def update_placement(placement_id: int, placement: PlacementUpdate):
    """
    Update a placement
    """
    return await db_manager.update_placement(placement_id, placement)


@placement_router.delete("/{placement_id}")
async def delete_placement(placement_id: int):
    """
    Delete a placement
    """
    return await db_manager.delete_placement(placement_id)


@placement_router.get('/placements_by_stream/{stream_id}', response_model=List[Placement])
async def get_placements_by_stream(stream_id: int):
    """
    Get placements by stream
    """
    return await db_manager.get_placements_by_stream(stream_id)


@placement_router.get('/placements_by_user/{user_id}', response_model=List[Placement])
async def get_placements_by_user(user_id: int):
    """
    Get placements by user
    """
    return await db_manager.get_placements_by_user(user_id)


@placement_router.post('/apply/{placement_id}', response_model=int)
@database.transaction()
async def apply_placement(placement_id: int, user_id: int):
    """
    Apply for a placement
    """
    return await db_manager.apply_placement(placement_id, user_id)


@placement_router.get('/applicants/{placement_id}', status_code=status.HTTP_200_OK)
async def get_applicants(placement_id: int):
    """
    Get applicants for a placement
    """
    return await db_manager.get_applicants(placement_id)