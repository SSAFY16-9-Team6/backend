from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, UniqueConstraint
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

# 6. RAG 임베딩 테이블 (장소/게시글 텍스트를 벡터로 저장해두고 코사인 유사도로 검색)
class Embedding(Base):
    __tablename__ = "embeddings"
    id = Column(Integer, primary_key=True, index=True)
    entityType = Column(String, nullable=False)   # "place" | "post"
    entityId = Column(String, nullable=False, index=True)
    content = Column(Text, nullable=False)         # 임베딩을 생성한 원본 텍스트
    vector = Column(Text, nullable=False)          # JSON으로 직렬화된 float 벡터
    model = Column(String, nullable=False)
    updatedAt = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("entityType", "entityId", name="uq_embedding_entity"),
    )