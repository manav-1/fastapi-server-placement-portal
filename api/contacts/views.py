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

contact_router = APIRouter(prefix="/contact", tags=["Contacts"])


@contact_router.get('/', response_model=List[ContactOut])
async def get_contacts():
    """
    Get all contacts
    """
    return await db_manager.get_contacts()


@contact_router.get('/{contact_id}', response_model=ContactOut)
async def get_contact(contact_id: int):
    """
    Get a contact by id
    """
    return await db_manager.get_contact(contact_id)


@contact_router.put('/{contact_id}', response_model=ContactOut)
async def update_contact(contact_id: int, contact: ContactUpdate, current_user: UserOut = Depends(get_current_active_user)):
    """
    Update a contact
    """
    if current_user.user_role == UserRole.ADMIN:
        return await db_manager.update_contact(contact_id, contact)
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You do not have permission to perform this action")


@contact_router.delete('/{contact_id}')
async def delete_contact(contact_id: int, current_user: UserOut = Depends(get_current_active_user)):
    """
    Delete a contact
    """
    if current_user.user_role == UserRole.ADMIN:
        return await db_manager.delete_contact(contact_id)
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You do not have permission to perform this action")


@contact_router.post('/', response_model=int, status_code=status.HTTP_201_CREATED)
async def create_contact(contact: ContactIn, current_user: UserOut = Depends(get_current_active_user)):
    """
    Create a contact
    """
    if current_user.user_role == UserRole.ADMIN:
        return await db_manager.create_contact(contact)
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You do not have permission to perform this action")
