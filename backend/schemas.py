from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class CategoryOut(BaseModel):
    categoryId: int
    name: str
    class Config:
        orm_mode = True

class PlaceOut(BaseModel):
    contentId: str
    title: str
    address: Optional[str]
    thumbnail: Optional[str]
    mapX: Optional[str]
    mapY: Optional[str]
    lDongRegnCd: Optional[str]
    lDongSignguCd: Optional[str]
    class Config:
        orm_mode = True

class PostCreate(BaseModel):
    categoryId: Optional[int]
    title: str
    content: str
    password: str
    author: Optional[str] = "익명"

class PostOut(BaseModel):
    postId: int
    categoryId: Optional[int]
    title: str
    content: str
    author: str
    createdAt: datetime
    likeCount: int
    viewCount: Optional[int] = 0
    class Config:
        orm_mode = True

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    reply: str
