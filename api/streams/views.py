from fastapi import APIRouter, status, Security, Body
from typing import List, Optional
from fastapi import UploadFile, File
from .models import *
from . import db_manager
from api.db_connect import database
from api.users.views import get_current_active_user
from api.users.models import *
from api.db import UserRole
from fastapi import Depends
from fastapi import HTTPException

stream_router = APIRouter(prefix="/streams", tags=["Streams"])


@stream_router.get('/', response_model=List[Stream])
async def get_streams():
    """
    Get all streams
    """
    return await db_manager.get_streams()


@stream_router.get('/{stream_id}', response_model=Stream)
async def get_stream(stream_id: int):
    """
    Get a stream by id
    """
    return await db_manager.get_stream(stream_id)


@stream_router.put('/{stream_id}', response_model=Stream)
async def update_stream(stream_id: int, stream: StreamUpdate, current_user: UserOut = Depends(get_current_active_user)):
    """
    Update a stream
    """
    if current_user.user_role == UserRole.ADMIN:
        return await db_manager.update_stream(stream_id, stream)
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You do not have permission to perform this action")


@stream_router.delete('/{stream_id}')
async def delete_stream(stream_id: int, current_user: UserOut = Depends(get_current_active_user)):
    """
    Delete a stream
    """
    if current_user.user_role == UserRole.ADMIN:
        return await db_manager.delete_stream(stream_id)
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You do not have permission to perform this action")


@stream_router.post('/', response_model=int, status_code=status.HTTP_201_CREATED)
async def create_stream(stream: StreamIn, current_user: UserOut = Depends(get_current_active_user)):
    """
    Create a stream
    """
    if current_user.user_role == UserRole.ADMIN:
        return await db_manager.create_stream(stream)
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You do not have permission to perform this action")
