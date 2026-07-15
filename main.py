import os
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from backend import database, crud, schemas

load_dotenv()

API_PREFIX = "/api/v1"
app = FastAPI(title="LocalHub API")

FRONT = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONT],
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


@app.get(API_PREFIX + "/categories")
def list_categories(db: Session = Depends(get_db)):
    cats = crud.list_categories(db)
    return success([{"categoryId": c.categoryId, "name": c.name} for c in cats])


@app.get(API_PREFIX + "/categories/{categoryId}/places")
def places_by_category(categoryId: int, page: int = 1, size: int = 20, keyword: str = None, db: Session = Depends(get_db)):
    skip = (page - 1) * size
    total, items = crud.places_by_category(db, categoryId, skip, size, keyword)
    pagination = {"page": page, "size": size, "totalPages": (total + size - 1) // size, "hasNext": (page * size) < total, "hasPrevious": page > 1}
    # convert ORM objects to dicts safely
    def to_dict(p):
        return {"contentId": p.contentId, "title": p.title, "thumbnail": p.thumbnail, "address": p.address, "mapX": p.mapX, "mapY": p.mapY}
    return success({"categoryId": categoryId, "categoryName": None, "totalCount": total, "items": [to_dict(i) for i in items], "pagination": pagination})


@app.get(API_PREFIX + "/places/{contentId}")
def place_detail(contentId: str, db: Session = Depends(get_db)):
    p = crud.get_place(db, contentId)
    if not p:
        raise HTTPException(status_code=404, detail="Not found")
    data = {"contentId": p.contentId, "title": p.title, "address": p.address, "tel": getattr(p, 'tel', None), "thumbnail": p.thumbnail, "mapX": p.mapX, "mapY": p.mapY}
    return success(data)


@app.get(API_PREFIX + "/places/search")
def place_search(keyword: str = None, categoryId: int = None, page: int = 1, size: int = 20, db: Session = Depends(get_db)):
    skip = (page - 1) * size
    total, items = crud.search_places(db, keyword, categoryId, skip, size)
    def to_dict(p):
        return {"contentId": p.contentId, "title": p.title, "thumbnail": p.thumbnail, "address": p.address, "mapX": p.mapX, "mapY": p.mapY}
    return success({"totalCount": total, "items": [to_dict(i) for i in items]})


@app.get(API_PREFIX + "/categories/{categoryId}/posts")
def category_posts(categoryId: int, page: int = 1, size: int = 20, db: Session = Depends(get_db)):
    skip = (page - 1) * size
    total, items = crud.posts_by_category(db, categoryId, skip, size)
    def to_dict(p):
        return {"postId": p.postId, "title": p.title, "content": p.content, "author": p.author, "createdAt": p.createdAt, "likeCount": p.likeCount}
    return success({"items": [to_dict(i) for i in items], "totalCount": total})


@app.post(API_PREFIX + "/posts")
def create_post(post: schemas.PostCreate, db: Session = Depends(get_db)):
    p = crud.create_post(db, post.dict())
    return success(p)


@app.get(API_PREFIX + "/posts/{postId}")
def get_post(postId: int, db: Session = Depends(get_db)):
    p = crud.get_post(db, postId)
    if not p:
        raise HTTPException(status_code=404, detail="Not found")
    p = crud.incr_view(db, p)
    return success(p)


@app.put(API_PREFIX + "/posts/{postId}")
def put_post(postId: int, post: schemas.PostCreate, db: Session = Depends(get_db)):
    p = crud.get_post(db, postId)
    if not p:
        raise HTTPException(status_code=404, detail="Not found")
    if p.password != post.password:
        raise HTTPException(status_code=403, detail="Password mismatch")
    updated = crud.update_post(db, p, post.dict(exclude_unset=True))
    return success(updated)


@app.delete(API_PREFIX + "/posts/{postId}")
def delete_post(postId: int, body: dict, db: Session = Depends(get_db)):
    password = body.get("password")
    p = crud.get_post(db, postId)
    if not p:
        raise HTTPException(status_code=404, detail="Not found")
    if p.password != password:
        raise HTTPException(status_code=403, detail="Password mismatch")
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


# Chatbot endpoint
import openai
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
if OPENAI_KEY:
    openai.api_key = OPENAI_KEY


@app.post(API_PREFIX + "/chatbot/message")
def chatbot(req: schemas.ChatRequest, db: Session = Depends(get_db)):
    user_msg = req.message
    reply = "챗봇이 준비중입니다."
    if OPENAI_KEY:
        try:
            resp = openai.ChatCompletion.create(model="gpt-4o-mini", messages=[{"role": "user", "content": user_msg}], max_tokens=300)
            reply = resp.choices[0].message.content
        except Exception:
            reply = "챗봇 호출 중 오류가 발생했습니다."
    crud.log_chat(db, user_msg, reply)
    return success({"reply": reply})
