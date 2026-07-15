import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

load_dotenv()

# 환경변수에서 DB 경로를 읽되, 없으면 로컬 파일 사용
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./localhub.db")

# 엔진 생성
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False} if SQLALCHEMY_DATABASE_URL.startswith("sqlite") else {},
)

# 세션 생성기
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 모델 클래스들의 베이스
Base = declarative_base()

# DB 세션 의존성 주입 함수 (API에서 사용)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()