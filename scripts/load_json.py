import sys
import json
import os
import glob
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import models
from database import SessionLocal, Base, engine   # Base, engine 추가로 import

Base.metadata.create_all(bind=engine)   # <- 이 줄 추가: 테이블 없으면 생성


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

SEED_POSTS = [
    {"postId": 1, "categoryId": 12, "title": "이재용의 부산 여행 첫 방문 후기", "content": "안녕하세요, 삼성전자 이재용입니다. 유엔기념공원 다녀왔는데 정말 좋았어요. 다음엔 감천문화마을도 가보려구요.", "author": "익명", "password": "1696"},
    {"postId": 2, "categoryId": 28, "title": "강대범의 해운대 서핑 추천!", "content": "안녕하세요, 삼성전자 강대범입니다. 레포츠 즐기시는 분들 해운대 서핑 강습 한번 받아보세요.", "author": "익명", "password": "1696"},
    {"postId": 3, "categoryId": 39, "title": "거대 강사 김태희의 부산 밀면 맛집 공유", "content": "여러분~ 남포동 근처 밀면집 정말 맛있었습니다.", "author": "익명", "password": "1696"},
    {"postId": 4, "categoryId": 12, "title": "거대 프로 강혜빈의 감천문화마을 사진 명소", "content": "여러분~ 포토스팟 정리해봤어요. 아침 일찍 가시는 걸 추천!", "author": "익명", "password": "1696"},
    {"postId": 5, "categoryId": 32, "title": "거제 야호 미아미의 해운대 근처 숙소 후기", "content": "내가 추천한 가성비 좋은 숙소 예약할때까지 파라파라나 춰야지", "author": "익명", "password": "1696"},
]

def ensure_seed_posts(session):
    for data in SEED_POSTS:
        existing = session.query(models.Post).filter(models.Post.postId == data["postId"]).first()
        if not existing:
            session.add(models.Post(**data))
    session.commit()
def ensure_categories(session):
    for cat_id, name in CONTENT_TYPE_NAMES.items():
        existing = session.query(models.Category).filter(models.Category.categoryId == cat_id).first()
        if not existing:
            session.add(models.Category(categoryId=cat_id, name=name))
    session.commit()


def load_places(json_path: str):
    """단일 파일 처리 (기존 이름 유지, 하위 호환용)"""
    try:
        with open(json_path, encoding='utf-8') as f:
            data = json.load(f)
    except UnicodeDecodeError:
        with open(json_path, encoding='cp949') as f:
            data = json.load(f)

    items = data.get('items', [])
    session = SessionLocal()
    count = 0
    for item in items:
        content_id = str(item.get('contentid') or item.get('contentId') or '')
        if not content_id:
            continue
        p = models.Place(
            contentId=content_id,
            categoryId=int(item.get('contenttypeid') or 0),
            title=item.get('title'),
            address=item.get('addr1'),
            thumbnail=item.get('firstimage'),
            mapX=item.get('mapx'),
            mapY=item.get('mapy'),
            lDongRegnCd=item.get('lDongRegnCd'),
            lDongSignguCd=item.get('lDongSignguCd'),
        )
        session.merge(p)
        count += 1
    session.commit()
    session.close()
    print(f"  -> {count}건 처리: {os.path.basename(json_path)}")


def load_all(folder: str):
    session = SessionLocal()
    ensure_categories(session)
    ensure_seed_posts(session)
    session.close()

    json_files = sorted(glob.glob(os.path.join(folder, "*.json")))
    if not json_files:
        print(f"'{folder}' 폴더에 JSON 파일이 없습니다.")
        return

    for path in json_files:
        load_places(path)   # 기존 함수 그대로 재사용

if __name__ == '__main__':
    folder = sys.argv[1] if len(sys.argv) > 1 else 'data'
    if not os.path.isdir(folder):
        print('폴더를 찾을 수 없습니다:', folder)
        sys.exit(1)
    load_all(folder)
    print('전체 JSON 파일 로딩 완료')
