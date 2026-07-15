import sys
import json
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import models
from database import SessionLocal


CONTENT_TYPE_NAMES = {
    12: "관광지",
    14: "문화시설",
    15: "축제공연행사",
    25: "여행코스",
    28: "레포츠",
    32: "숙박",
    38: "쇼핑",
    39: "음식점",
}

def ensure_categories(session):
    for cat_id, name in CONTENT_TYPE_NAMES.items():
        existing = session.query(models.Category).filter(models.Category.categoryId == cat_id).first()
        if not existing:
            session.add(models.Category(categoryId=cat_id, name=name))
    session.commit()


def load_places(json_path: str):
    session = SessionLocal()
    ensure_categories(session)
    try:
        with open(json_path, encoding='utf-8') as f:
            data = json.load(f)
    except UnicodeDecodeError:
        with open(json_path, encoding='cp949') as f:
            data = json.load(f)
            
    # 수정 핵심: JSON 구조가 { "items": [...] } 형태이므로 리스트 추출
    items = data.get('items', []) 
    
    for item in items:
        # JSON 데이터 키 이름이 소문자(contentid, mapx 등)이므로 맞춰줍니다.
        content_id = str(item.get('contentid') or item.get('contentId') or '')
        if not content_id:
            continue
            
        p = models.Place(
            contentId=content_id,
            categoryId=int(item.get('contenttypeid') or 0), # 예시 데이터의 contentTypeId 활용
            title=item.get('title'),
            address=item.get('addr1'),
            thumbnail=item.get('firstimage'),
            mapX=item.get('mapx'),
            mapY=item.get('mapy'),
            lDongRegnCd=item.get('lDongRegnCd'),
            lDongSignguCd=item.get('lDongSignguCd'),
        )
        session.merge(p)
    session.commit()
    session.close()

if __name__ == '__main__':
    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else 'data/region.json'
    if not os.path.exists(path):
        print('JSON file not found:', path)
        sys.exit(1)
    load_places(path)
    print('Loaded places from', path)
