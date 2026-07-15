from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from database import Base
import datetime

# 1. 카테고리
class Category(Base):
    __tablename__ = "categories"
    categoryId = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

# 2. 장소 
class Place(Base):
    __tablename__ = "places"
    contentId = Column(String, primary_key=True)
    categoryId = Column(Integer, ForeignKey("categories.categoryId"))
    title = Column(String, nullable=False)
    address = Column(String)
    thumbnail = Column(String)
    mapX = Column(String)
    mapY = Column(String)
    lDongRegnCd = Column(String)
    lDongSignguCd = Column(String)

# 3. 커뮤니티 게시글 
class Post(Base):
    __tablename__ = "posts"
    postId = Column(Integer, primary_key=True, index=True)
    categoryId = Column(Integer, ForeignKey("categories.categoryId"))
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    password = Column(String, nullable=False)
    author = Column(String, default="익명")
    createdAt = Column(DateTime, default=datetime.datetime.utcnow)
    likeCount = Column(Integer, default=0)
    viewCount = Column(Integer, default=0)

# 4. 좋아요 중복 방지 테이블 
class LikeHistory(Base):
    __tablename__ = "like_history"
    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.postId"))
    user_key = Column(String, nullable=False)

# 5. 챗봇 로그 테이블 
class ChatbotLog(Base):
    __tablename__ = "chatbot_logs"
    id = Column(Integer, primary_key=True, index=True)
    user_message = Column(Text)
    bot_reply = Column(Text)