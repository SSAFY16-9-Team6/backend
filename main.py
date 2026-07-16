import os
import openai
from fastapi import FastAPI, Depends, HTTPException, Request, Body
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from dotenv import load_dotenv

import models, database, crud, schemas

load_dotenv()

API_PREFIX = "/api/v1"
app = FastAPI(title="LocalHub API")

FRONT = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

def success(data):
    return {"success": True, "data": data}

def fail(message):
    return {"success": False, "message": message}

@app.on_event("startup")
def on_startup():
    database.Base.metadata.create_all(bind=database.engine)

SIGNGU_NAMES = {
    "110": "중구",
    "140": "서구",
    "170": "동구",
    "200": "영도구",
    "230": "부산진구",
    "260": "동래구",
    "290": "남구",
    "320": "북구",
    "350": "해운대구",
    "380": "사하구",
}

#지역코드로 관광지 조회
@app.get(API_PREFIX + "/regions/{code}")
def get_region_places(code: str, page: int = 1, size: int = 20, db: Session = Depends(get_db)):
    name = SIGNGU_NAMES.get(code)
    if not name:
        raise HTTPException(status_code=404, detail="등록되지 않은 지역 코드입니다.")

    skip = (page - 1) * size
    total, items = crud.places_by_region(db, code, skip, size)
    pagination = {"page": page, "size": size, "totalPages": (total + size - 1) // size, "hasNext": (page * size) < total, "hasPrevious": page > 1}

    def place_to_dict(p):
        return {
            "contentId": p.contentId, "categoryId": p.categoryId, "title": p.title, 
            "address": p.address, "thumbnail": p.thumbnail, 
            "mapX": p.mapX, "mapY": p.mapY, 
            "lDongRegnCd": p.lDongRegnCd, "lDongSignguCd": p.lDongSignguCd
        }

    return success({
        "regionCode": code,
        "regionName": name,
        "totalCount": total,
        "items": [place_to_dict(i) for i in items],
        "pagination": pagination
    })


@app.get(API_PREFIX + "/categories")
def list_categories(db: Session = Depends(get_db)):
    cats = crud.list_categories(db)
    return success([{"categoryId": c.categoryId, "name": c.name} for c in cats])

#카테고리로 관광지 조회
@app.get(API_PREFIX + "/categories/{categoryId}/places")
def places_by_category(categoryId: int, page: int = 1, size: int = 20, keyword: str = None, db: Session = Depends(get_db)):
    skip = (page - 1) * size
    total, items, name = crud.places_by_category(db, categoryId, skip, size, keyword)
    pagination = {"page": page, "size": size, "totalPages": (total + size - 1) // size, "hasNext": (page * size) < total, "hasPrevious": page > 1}
    
    def place_to_dict(p):
        return {
            "contentId": p.contentId, "categoryId": p.categoryId, "title": p.title, 
            "address": p.address, "thumbnail": p.thumbnail, 
            "mapX": p.mapX, "mapY": p.mapY, 
            "lDongRegnCd": p.lDongRegnCd, "lDongSignguCd": p.lDongSignguCd
        }
        
    return success({
        "categoryId": categoryId, 
        "categoryName": name, 
        "totalCount": total, 
        "items": [place_to_dict(i) for i in items], 
        "pagination": pagination
    })

#장소 검색
@app.get(API_PREFIX + "/places/search")
def place_search(keyword: str = None, categoryId: int = None, page: int = 1, size: int = 20, db: Session = Depends(get_db)):
    skip = (page - 1) * size
    total, items = crud.search_places(db, keyword, categoryId, skip, size)
    def place_to_dict(p):
        return {
            "contentId": p.contentId, "categoryId": p.categoryId, "title": p.title, 
            "address": p.address, "thumbnail": p.thumbnail, 
            "mapX": p.mapX, "mapY": p.mapY, 
            "lDongRegnCd": p.lDongRegnCd, "lDongSignguCd": p.lDongSignguCd
        }
    return success({
        "totalCount": total, 
        "items": [place_to_dict(i) for i in items]
    })

#컨텐츠로 장소 검색
@app.get(API_PREFIX + "/places/{contentId}")
def place_detail(contentId: str, db: Session = Depends(get_db)):
    p = crud.get_place(db, contentId)
    if not p:
        raise HTTPException(status_code=404, detail="Not found")
    return success({
        "contentId": p.contentId, "categoryId": p.categoryId, "title": p.title, 
        "address": p.address, "thumbnail": p.thumbnail, 
        "mapX": p.mapX, "mapY": p.mapY, 
        "lDongRegnCd": p.lDongRegnCd, "lDongSignguCd": p.lDongSignguCd
    })

#게시물 생성
@app.post(API_PREFIX + "/posts")
def create_post(post: schemas.PostCreate, db: Session = Depends(get_db)):
    category = db.query(models.Category).filter(models.Category.categoryId == post.categoryId).first()
    if not category:
        return fail("존재하지 않는 카테고리입니다.")
    p = crud.create_post(db, post.dict())
    return success({
        "postId": p.postId, "categoryId": p.categoryId, "title": p.title, 
        "content": p.content, "author": p.author, "createdAt": p.createdAt, 
        "likeCount": p.likeCount, "viewCount": p.viewCount
    })

#게시물 조회
@app.get(API_PREFIX + "/posts")
def list_posts(page: int = 1, size: int = 20, db: Session = Depends(get_db)):
    skip = (page - 1) * size
    total, items = crud.list_posts(db, skip, size)
    def post_to_dict(p):
        return {
            "postId": p.postId, "categoryId": p.categoryId, "title": p.title, 
            "content": p.content, "author": p.author, "createdAt": p.createdAt, 
            "likeCount": p.likeCount, "viewCount": p.viewCount
        }
    return success({
        "items": [post_to_dict(i) for i in items], 
        "totalCount": total
    })

#카테고리별 게시물 조회
@app.get(API_PREFIX + "/categories/{categoryId}/posts")
def category_posts(categoryId: int, page: int = 1, size: int = 20, db: Session = Depends(get_db)):
    skip = (page - 1) * size
    total, items = crud.posts_by_category(db, categoryId, skip, size)
    pagination = {"page": page, "size": size, "totalPages": (total + size - 1) // size, "hasNext": (page * size) < total, "hasPrevious": page > 1}

    def post_to_dict(p):
        return {
            "postId": p.postId, "categoryId": p.categoryId, "title": p.title, 
            "content": p.content, "author": p.author, "createdAt": p.createdAt, 
            "likeCount": p.likeCount, "viewCount": p.viewCount
        }
    return success({
        "items": [post_to_dict(i) for i in items], 
        "totalCount": total,
        "pagination": pagination
    })

@app.get(API_PREFIX + "/posts/search")
def search_posts(keyword: str, page: int = 1, size: int = 20, db: Session = Depends(get_db)):
    skip = (page - 1) * size
    total, items = crud.search_posts(db, keyword, skip, size)
    pagination = {"page": page, "size": size, "totalPages": (total + size - 1) // size, "hasNext": (page * size) < total, "hasPrevious": page > 1}

    def post_to_dict(p):
        return {
            "postId": p.postId, "categoryId": p.categoryId, "title": p.title, 
            "content": p.content, "author": p.author, "createdAt": p.createdAt, 
            "likeCount": p.likeCount, "viewCount": p.viewCount
        }
    return success({
        "totalCount": total,
        "items": [post_to_dict(i) for i in items],
        "pagination": pagination
    })

@app.get(API_PREFIX + "/posts/{postId}")
def get_post(postId: int, db: Session = Depends(get_db)):
    p = crud.get_post(db, postId)
    if not p:
        raise HTTPException(status_code=404, detail="Not found")
    p = crud.incr_view(db, p)
    return success({
        "postId": p.postId, "categoryId": p.categoryId, "title": p.title, 
        "content": p.content, "author": p.author, "createdAt": p.createdAt, 
        "likeCount": p.likeCount, "viewCount": p.viewCount
    })


@app.post(API_PREFIX + "/posts/{postId}/verify-password")
def verify_password(postId: int, body: dict = Body(...), db: Session = Depends(get_db)):
    password = body.get("password")
    p = crud.get_post(db, postId)
    if not p:
        raise HTTPException(status_code=404, detail="Not found")
    if p.password != password:
        return fail("비밀번호가 일치하지 않습니다.")
    return success({"verified": True})


@app.put(API_PREFIX + "/posts/{postId}")
def put_post(postId: int, post: schemas.PostUpdate, db: Session = Depends(get_db)):
    if postId in SEED_POST_IDS:
        return fail("지금 감히 누구의 글을 수정하려 하는가?")
    p = crud.get_post(db, postId)
    if not p:
        raise HTTPException(status_code=404, detail="Not found")
    updated = crud.update_post(db, p, post.dict(exclude_unset=True))
    return success({
        "postId": updated.postId, "categoryId": updated.categoryId, "title": updated.title, 
        "content": updated.content, "author": updated.author, "createdAt": updated.createdAt, 
        "likeCount": updated.likeCount, "viewCount": updated.viewCount
    })

SEED_POST_IDS = {1, 2, 3, 4, 5}
@app.delete(API_PREFIX + "/posts/{postId}")
def delete_post(postId: int, db: Session = Depends(get_db)):
    if postId in SEED_POST_IDS:
        return fail("지금 감히 누구의 글을 삭제하려 하는가?")
    p = crud.get_post(db, postId)
    if not p:
        raise HTTPException(status_code=404, detail="Not found")
    crud.delete_post(db, p)
    return success({"ok": True})


@app.post(API_PREFIX + "/posts/{postId}/likes")
def like_post(postId: int, request: Request, db: Session = Depends(get_db)):
    p = crud.get_post(db, postId)
    if not p:
        raise HTTPException(status_code=404, detail="Not found")
    user_key = request.client.host if request.client else "anon"
    liked, like_count = crud.add_like(db, p, user_key)
    return success({"liked": liked, "likeCount": like_count})

@app.get(API_PREFIX + "/stats/posts-by-category")
def posts_stats(db: Session = Depends(get_db)):
    return success(crud.post_counts_by_category(db))

# ----------------------------------------
# 챗봇 엔드포인트
# ----------------------------------------
from openai import OpenAI

OPENAI_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_KEY) if OPENAI_KEY else None

@app.post(API_PREFIX + "/chatbot/message")
def chatbot(req: schemas.ChatRequest, db: Session = Depends(get_db)):
    user_msg = req.message
    reply = "챗봇 API 키가 설정되지 않았습니다."
    
    if client:
        try:
            _, places = crud.search_places(db, keyword=user_msg, limit=3)
            context = "\n".join([f"- {p.title} (주소: {p.address})" for p in places])
            
            system_prompt = (
                "당신은 부산 관광 전문가입니다. 아래 [데이터]를 바탕으로 친절하게 답변하세요.\n"
                f"[데이터]\n{context}"
            )
            
            resp = client.chat.completions.create(
                model="gpt-5-mini", 
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_msg}
                ], 
                max_completion_tokens=3000
            )
            reply = resp.choices[0].message.content
        except Exception as e:
            reply = f"챗봇 오류 발생: {str(e)}"
            
    crud.log_chat(db, user_msg, reply)
    return success({"reply": reply})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)