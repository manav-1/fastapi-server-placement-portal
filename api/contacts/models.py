from sqlite3 import Date
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from api.db import ContactPosition


class ContactIn(BaseModel):
    contact_name: str
    contact_email: EmailStr
    contact_mobile: int
    contact_position: ContactPosition


class ContactOut(ContactIn):
    contact_id: int


class ContactUpdate(BaseModel):
    contact_name: Optional[str]
    contact_email: Optional[EmailStr]
    contact_mobile: Optional[str]
    contact_position: Optional[ContactPosition]
