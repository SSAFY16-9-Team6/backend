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
`OPENAI_API_KEY`가 설정되어 있으면 데이터 적재 시 place/post에 대한 임베딩(RAG용)도 함께 생성됩니다.
나중에 키를 추가했거나 임베딩만 다시 만들고 싶다면:
```bash
python scripts/build_embeddings.py
```

## 서버 실행
```bash
uvicorn backend.main:app --reload --port 8000
```
서버 시작 시에도 임베딩이 없는 place/post가 있으면 자동으로 채워집니다.

## 챗봇 RAG 구조
외부 벡터DB 없이 우리 DB(`embeddings` 테이블)만으로 RAG를 구현했습니다.
- `place`(장소)와 `post`(게시글) 텍스트를 OpenAI 임베딩(`text-embedding-3-small`, 512차원)으로 변환해 `embeddings` 테이블에 저장합니다 (`rag.py`).
- 게시글은 생성/수정/삭제 시 임베딩이 함께 갱신됩니다 (`crud.py`).
- `/api/v1/chatbot/message` 호출 시 사용자 질문을 임베딩하고, DB에 저장된 벡터들과 코사인 유사도를 계산해 가장 관련 있는 상위 5건을 컨텍스트로 LLM에 전달합니다 (`rag.retrieve`, `rag.build_context`).

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
