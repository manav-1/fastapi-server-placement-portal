from sqlite3 import Date
from pydantic import BaseModel, EmailStr
from typing import List, Optional

class StreamIn(BaseModel):
    stream_name:str


class Stream(StreamIn):
    stream_id:int

class StreamUpdate(BaseModel):
    stream_name:Optional[str]