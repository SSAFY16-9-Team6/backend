"""
DB에 이미 적재된 place/post 중 임베딩이 없는 항목을 찾아 생성한다 (idempotent).
OPENAI_API_KEY를 나중에 설정했거나, 서버를 띄우지 않고 임베딩만 갱신하고 싶을 때 사용.

사용법:
    python scripts/build_embeddings.py
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import rag
from database import SessionLocal, Base, engine

Base.metadata.create_all(bind=engine)


def main():
    if not rag.client:
        print("OPENAI_API_KEY가 설정되지 않았습니다. .env 파일을 확인하세요.")
        sys.exit(1)

    db = SessionLocal()
    try:
        n_places = rag.sync_place_embeddings(db)
        n_posts = rag.sync_post_embeddings(db)
        print(f"완료: place {n_places}건, post {n_posts}건 임베딩 생성")
    finally:
        db.close()


if __name__ == '__main__':
    main()
