from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func
import models

def list_categories(db: Session) -> List[models.Category]:
    return db.query(models.Category).all()

def get_places(db: Session, skip: int = 0, limit: int = 100) -> List[models.Place]:
    return db.query(models.Place).offset(skip).limit(limit).all()

def places_by_region(db: Session, signgu_code: str, skip: int = 0, limit: int = 20) -> Tuple[int, List[models.Place]]:
    q = db.query(models.Place).filter(models.Place.lDongSignguCd == signgu_code)
    total = q.count()
    items = q.offset(skip).limit(limit).all()
    return total, items

def places_by_category(db: Session, category_id: int, skip: int = 0, limit: int = 20, keyword: Optional[str] = None) -> Tuple[int, List[models.Place]]:
    category = db.query(models.Category).filter(models.Category.categoryId == category_id).first()
    q = db.query(models.Place).filter(models.Place.categoryId == category_id)
    if keyword:
        like = f"%{keyword}%"
        q = q.filter(models.Place.title.ilike(like) | models.Place.address.ilike(like))
    total = q.count()
    items = q.offset(skip).limit(limit).all()
    return total, items, category.name

def get_place(db: Session, content_id: str) -> Optional[models.Place]:
    return db.query(models.Place).filter(models.Place.contentId == content_id).first()

def search_places(db: Session, keyword: Optional[str] = None, category_id: Optional[int] = None, skip: int = 0, limit: int = 20) -> Tuple[int, List[models.Place]]:
    q = db.query(models.Place)
    if category_id:
        q = q.filter(models.Place.categoryId == category_id)
    if keyword:
        like = f"%{keyword}%"
        q = q.filter(models.Place.title.ilike(like) | models.Place.address.ilike(like))
    total = q.count()
    return total, q.offset(skip).limit(limit).all()

def posts_by_category(db: Session, category_id: int, skip: int = 0, limit: int = 20) -> Tuple[int, List[models.Post]]:
    q = db.query(models.Post).filter(models.Post.categoryId == category_id).order_by(models.Post.createdAt.desc())
    total = q.count()
    return total, q.offset(skip).limit(limit).all()

def create_post(db: Session, post_data: dict) -> models.Post:
    p = models.Post(
        categoryId=post_data.get("categoryId"),
        title=post_data.get("title"),
        content=post_data.get("content"),
        password=post_data.get("password"),
        author=post_data.get("author", "익명")
    )
    db.add(p)
    db.commit()
    db.refresh(p)
    return p

def list_posts(db: Session, skip: int = 0, limit: int = 20) -> Tuple[int, List[models.Post]]:
    q = db.query(models.Post).order_by(models.Post.createdAt.desc())
    total = q.count()
    items = q.offset(skip).limit(limit).all()
    return total, items

def get_post(db: Session, post_id: int) -> Optional[models.Post]:
    return db.query(models.Post).filter(models.Post.postId == post_id).first()

def incr_view(db: Session, post: models.Post) -> models.Post:
    post.viewCount = (post.viewCount or 0) + 1
    db.commit()
    db.refresh(post)
    return post

def update_post(db: Session, post: models.Post, updates: dict) -> models.Post:
    for k, v in updates.items():
        if hasattr(post, k):
            setattr(post, k, v)
    db.commit()
    db.refresh(post)
    return post

def delete_post(db: Session, post: models.Post):
    db.delete(post)
    db.commit()

def add_like(db: Session, post: models.Post, user_key: str):
    # simple duplicate prevention using LikeHistory if available
    if hasattr(models, 'LikeHistory'):
        exist = db.query(models.LikeHistory).filter(models.LikeHistory.post_id == post.postId, models.LikeHistory.user_key == user_key).first()
        if exist:
            return False, post.likeCount or 0
        lh = models.LikeHistory(post_id=post.postId, user_key=user_key)
        db.add(lh)
    post.likeCount = (post.likeCount or 0) + 1
    db.commit()
    db.refresh(post)
    return True, post.likeCount

def log_chat(db: Session, user_msg: str, bot_reply: str):
    if hasattr(models, 'ChatbotLog'):
        c = models.ChatbotLog(user_message=user_msg, bot_reply=bot_reply)
        db.add(c)
        db.commit()
        db.refresh(c)
        return c
    return None
