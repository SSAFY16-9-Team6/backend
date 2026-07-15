from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.database import Base
import datetime

# 1. 카테고리 (데이터 고정 혹은 미리 삽입)
class Category(Base):
    __tablename__ = "categories"
    categoryId = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

# 2. 장소 (부산 데이터 매핑)
class Place(Base):
    __tablename__ = "places"
    contentId = Column(String, primary_key=True) # JSON 데이터 고유 ID
    categoryId = Column(Integer, ForeignKey("categories.categoryId"))
    title = Column(String, nullable=False)
    address = Column(String)
    thumbnail = Column(String)
    mapX = Column(String)
    mapY = Column(String)

# 3. 커뮤니티 게시글
class Post(Base):
    __tablename__ = "posts"
    postId = Column(Integer, primary_key=True, index=True)
    categoryId = Column(Integer, ForeignKey("categories.categoryId"))
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    password = Column(String, nullable=False) # 평문 저장(RFP 요구사항)
    author = Column(String, default="익명")
    createdAt = Column(DateTime, default=datetime.datetime.utcnow)
    likeCount = Column(Integer, default=0)