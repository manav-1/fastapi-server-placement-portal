from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional


class Email(BaseModel):
    sender_email: Optional[EmailStr]
    password: Optional[str]
    subject: str
    sheet_url: str
    starting_number: int
    ending_number: int
