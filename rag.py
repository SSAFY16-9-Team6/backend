import os
import json
import math
import datetime
from typing import List, Optional, Tuple

from openai import OpenAI
from sqlalchemy.orm import Session

import models
from constants import CONTENT_TYPE_NAMES, SIGNGU_NAMES

EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIM = 512

OPENAI_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_KEY) if OPENAI_KEY else None

# entityType별 (entityId, vector) 캐시. embeddings 테이블은 자주 바뀌지 않으므로
# 매 요청마다 DB 전체를 읽어 JSON 파싱하는 비용을 피하기 위해 메모리에 캐시한다.
_cache: Optional[List[Tuple[str, str, List[float]]]] = None


def invalidate_cache() -> None:
    global _cache
    _cache = None


def embed_texts(texts: List[str]) -> List[List[float]]:
    if not client:
        raise RuntimeError("OPENAI_API_KEY가 설정되지 않았습니다.")
    resp = client.embeddings.create(model=EMBEDDING_MODEL, input=texts, dimensions=EMBEDDING_DIM)
    return [d.embedding for d in resp.data]


def embed_text(text: str) -> List[float]:
    return embed_texts([text])[0]


def build_place_text(place: models.Place) -> str:
    parts = [place.title]
    category_name = CONTENT_TYPE_NAMES.get(place.categoryId)
    if category_name:
        parts.append(f"카테고리: {category_name}")
    region_name = SIGNGU_NAMES.get(place.lDongSignguCd)
    if region_name:
        parts.append(f"지역: {region_name}")
    if place.address:
        parts.append(f"주소: {place.address}")
    return " / ".join(parts)


def build_post_text(post: models.Post) -> str:
    return f"{post.title}\n{post.content}"


def upsert_embedding(db: Session, entity_type: str, entity_id: str, text: str) -> models.Embedding:
    vector = embed_text(text)
    row = (
        db.query(models.Embedding)
        .filter(models.Embedding.entityType == entity_type, models.Embedding.entityId == str(entity_id))
        .first()
    )
    if row:
        row.content = text
        row.vector = json.dumps(vector)
        row.model = EMBEDDING_MODEL
        row.updatedAt = datetime.datetime.utcnow()
    else:
        row = models.Embedding(
            entityType=entity_type,
            entityId=str(entity_id),
            content=text,
            vector=json.dumps(vector),
            model=EMBEDDING_MODEL,
        )
        db.add(row)
    db.commit()
    invalidate_cache()
    return row


def delete_embedding(db: Session, entity_type: str, entity_id: str) -> None:
    db.query(models.Embedding).filter(
        models.Embedding.entityType == entity_type, models.Embedding.entityId == str(entity_id)
    ).delete()
    db.commit()
    invalidate_cache()


def sync_place_embeddings(db: Session, batch_size: int = 100) -> int:
    """embeddings 테이블에 없는 place만 찾아 임베딩을 생성한다 (idempotent)."""
    embedded_ids = {
        eid for (eid,) in db.query(models.Embedding.entityId).filter(models.Embedding.entityType == "place")
    }
    targets = [p for p in db.query(models.Place).all() if p.contentId not in embedded_ids]

    count = 0
    for i in range(0, len(targets), batch_size):
        chunk = targets[i : i + batch_size]
        texts = [build_place_text(p) for p in chunk]
        vectors = embed_texts(texts)
        for place, text, vector in zip(chunk, texts, vectors):
            db.add(
                models.Embedding(
                    entityType="place",
                    entityId=place.contentId,
                    content=text,
                    vector=json.dumps(vector),
                    model=EMBEDDING_MODEL,
                )
            )
        db.commit()
        count += len(chunk)

    if count:
        invalidate_cache()
    return count


def sync_post_embeddings(db: Session, batch_size: int = 100) -> int:
    """embeddings 테이블에 없는 post만 찾아 임베딩을 생성한다 (idempotent)."""
    embedded_ids = {
        eid for (eid,) in db.query(models.Embedding.entityId).filter(models.Embedding.entityType == "post")
    }
    targets = [p for p in db.query(models.Post).all() if str(p.postId) not in embedded_ids]

    count = 0
    for i in range(0, len(targets), batch_size):
        chunk = targets[i : i + batch_size]
        texts = [build_post_text(p) for p in chunk]
        vectors = embed_texts(texts)
        for post, text, vector in zip(chunk, texts, vectors):
            db.add(
                models.Embedding(
                    entityType="post",
                    entityId=str(post.postId),
                    content=text,
                    vector=json.dumps(vector),
                    model=EMBEDDING_MODEL,
                )
            )
        db.commit()
        count += len(chunk)

    if count:
        invalidate_cache()
    return count


def _cosine(a: List[float], b: List[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def _load_cache(db: Session) -> List[Tuple[str, str, List[float]]]:
    global _cache
    if _cache is None:
        rows = db.query(
            models.Embedding.entityType, models.Embedding.entityId, models.Embedding.vector
        ).all()
        _cache = [(t, i, json.loads(v)) for t, i, v in rows]
    return _cache


def retrieve(
    db: Session, query: str, entity_types: Optional[List[str]] = None, top_k: int = 5
) -> List[Tuple[str, str, float]]:
    """쿼리 문장을 임베딩해서 DB에 저장된 벡터들과 코사인 유사도로 비교, 상위 top_k를 반환한다."""
    query_vector = embed_text(query)
    candidates = _load_cache(db)
    if entity_types:
        candidates = [c for c in candidates if c[0] in entity_types]

    scored = [(entity_type, entity_id, _cosine(query_vector, vector)) for entity_type, entity_id, vector in candidates]
    scored.sort(key=lambda x: x[2], reverse=True)
    return scored[:top_k]


def build_context(db: Session, scored: List[Tuple[str, str, float]]) -> str:
    lines = []
    for entity_type, entity_id, score in scored:
        if entity_type == "place":
            place = db.query(models.Place).filter(models.Place.contentId == entity_id).first()
            if not place:
                continue
            category_name = CONTENT_TYPE_NAMES.get(place.categoryId, "")
            lines.append(f"- [장소] {place.title} ({category_name}) - 주소: {place.address or '정보 없음'}")
        elif entity_type == "post":
            post = db.query(models.Post).filter(models.Post.postId == int(entity_id)).first()
            if not post:
                continue
            snippet = post.content[:200]
            lines.append(f"- [여행 후기] {post.title}: {snippet}")

    return "\n".join(lines) if lines else "관련 자료를 찾지 못했습니다."
