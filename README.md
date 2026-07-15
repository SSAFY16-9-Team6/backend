# LocalHub Backend

로컬 개발 가이드

## 준비
1. 가상환경 생성
```bash
python -m venv .venv
.\.venv\Scripts\activate
```
2. 의존성 설치
```bash
pip install -r requirements.txt
```
3. 환경변수 설정
루트에 `.env` 파일을 만들고 아래 항목을 설정하세요:
```
DATABASE_URL=sqlite:///./localhub.db
OPENAI_API_KEY=your_openai_key_here
FRONTEND_ORIGIN=http://localhost:5173
```

## DB 생성 및 데이터 적재
```bash
python -c "from backend import database; database.Base.metadata.create_all(bind=database.engine)"
python scripts/load_json.py path/to/region.json
```

## 서버 실행
```bash
uvicorn backend.main:app --reload --port 8000
```

## 주요 엔드포인트
- `GET /api/v1/categories`
- `GET /api/v1/categories/{categoryId}/places`
- `GET /api/v1/places/{contentId}`
- `GET /api/v1/places/search`
- `GET /api/v1/categories/{categoryId}/posts`
- `POST /api/v1/posts`
- `GET/PUT/DELETE /api/v1/posts/{postId}`
- `POST /api/v1/posts/{postId}/likes`
- `POST /api/v1/chatbot/message`


문의: 추가 자동화(테스트 스크립트, Dockerfile 등) 원하시면 알려주세요.
