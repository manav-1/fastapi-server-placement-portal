from sqlite3 import Date
from pydantic import BaseModel, EmailStr
from typing import List, Optional


class Placement(BaseModel):
    placement_company_name: str
    placement_profile: str
    company_url: str
    image_url: str
    linkedin_url: str
    jd_url: str
    deadline: Date
    stream_ids: List[int]
    is_active: bool


class PlacementOut(Placement):
    placement_id: int


class PlacementUpdate(BaseModel):
    placement_company_name: Optional[str]
    placement_profile: Optional[str]
    company_url: Optional[str]
    image_url: Optional[str]
    linkedin_url: Optional[str]
    jd_url: Optional[str]
    deadline: Optional[Date]
    stream_ids: Optional[List[int]]
    is_active: Optional[bool]
