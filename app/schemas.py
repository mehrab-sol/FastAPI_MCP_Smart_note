from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# schema-1-creating note
class NoteCreate(BaseModel):
    title: str
    content: str

#schema-2-reading note
class NoteResponse(BaseModel):
    id: int 
    title: str
    content: str
    created_at: datetime


    class Config:
        from_attributes = True

#schema-3-searching notes
class NoteSearchResponse(BaseModel):
    notes: list[NoteResponse]
    total: int

    