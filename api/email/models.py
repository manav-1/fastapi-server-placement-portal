from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional


class Email(BaseModel):
    sender_email: Optional[EmailStr]
    password: Optional[str]
    subject: str
    sheet_url: str
    starting_number: int
    ending_number: int
    email_type: bool


class EmailDbIn(BaseModel):
    hr_email: EmailStr
    hr_name: str
    email_sent_at: datetime
    email_sent_by_user_id: int
    email_type: bool


class EmailDbOut(EmailDbIn):
    email_data_id: int
    user_name: str
    user_email: EmailStr