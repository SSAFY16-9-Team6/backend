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
    {"postId": 3, "categoryId": 38, "title": "거대 강사 김태희의 부산 밀면 맛집 공유", "content": "여러분~ 남포동 근처 밀면집 정말 맛있었습니다.", "author": "익명", "password": "1696"},
    {"postId": 4, "categoryId": 12, "title": "거대 프로 강혜빈의 감천문화마을 사진 명소", "content": "여러분~ 포토스팟 정리해봤어요. 아침 일찍 가시는 걸 추천!", "author": "익명", "password": "1696"},
    {"postId": 5, "categoryId": 32, "title": "거제 야호 미나미의 해운대 근처 숙소 후기", "content": "내가 추천한 가성비 좋은 숙소 예약할때까지 파라파라나 춰야지", "author": "익명", "password": "1696"},
    {"postId": 6, "categoryId": 12, "title": "태종대 드라이브 코스", "content": "태종대 순환도로 드라이브하기 정말 좋았어요. 전망대에서 보는 바다뷰 최고입니다.", "author": "익명", "password": "1234"},
    {"postId": 7, "categoryId": 12, "title": "송도해상케이블카 후기", "content": "생각보다 스릴 있었어요. 크리스탈 캐빈 타면 발밑이 다 보입니다.", "author": "익명", "password": "1234"},
    {"postId": 8, "categoryId": 14, "title": "부산현대미술관 다녀왔어요", "content": "전시가 자주 바뀌어서 매번 새로운 느낌입니다. 카페도 분위기 좋아요.", "author": "익명", "password": "1234"},
    {"postId": 9, "categoryId": 14, "title": "국립일제강제동원역사관 방문기", "content": "아이들과 함께 역사 공부하러 다녀왔습니다. 전시 설명이 잘 되어있어요.", "author": "익명", "password": "1234"},
    {"postId": 10, "categoryId": 15, "title": "부산불꽃축제 명당자리 찾기", "content": "매년 가는데 광안대교 주변 자리 미리 맡아야 편하게 볼 수 있어요.", "author": "익명", "password": "1234"},
    {"postId": 11, "categoryId": 15, "title": "부산국제영화제 상영관 정보", "content": "BIFF 기간에 남포동 일대 상영관들 돌아다니면서 관람하는 재미가 있습니다.", "author": "익명", "password": "1234"},
    {"postId": 12, "categoryId": 25, "title": "부산 원도심 도보여행 코스", "content": "40계단부터 시작해서 용두산공원까지 이어지는 코스 추천드려요.", "author": "익명", "password": "1234"},
    {"postId": 13, "categoryId": 25, "title": "갈맷길 완주 후기", "content": "구간별로 나눠서 완주했는데 바다 보면서 걷는 느낌이 최고입니다.", "author": "익명", "password": "1234"},
    {"postId": 14, "categoryId": 28, "title": "광안리 패들보드 체험", "content": "처음 타봤는데 생각보다 안 어려워요. 강습 30분이면 충분합니다.", "author": "익명", "password": "1234"},
    {"postId": 15, "categoryId": 28, "title": "기장 스노클링 스팟 공유", "content": "여름에 물 맑아서 스노클링 하기 좋은 곳 발견했어요.", "author": "익명", "password": "1234"},
    {"postId": 16, "categoryId": 32, "title": "광안리 오션뷰 숙소 추천", "content": "야경 보면서 자고 싶으신 분들은 광안리 쪽 숙소 강추입니다.", "author": "익명", "password": "1234"},
    {"postId": 17, "categoryId": 32, "title": "게스트하우스 vs 호텔 고민", "content": "혼자 여행이면 게스트하우스도 나쁘지 않은 것 같아요. 사람들과 얘기도 하고.", "author": "익명", "password": "1234"},
    {"postId": 18, "categoryId": 38, "title": "국제시장 쇼핑 팁", "content": "흥정 가능한 곳도 있으니 참고하세요. 먹거리도 같이 즐기면 좋아요.", "author": "익명", "password": "1234"},
    {"postId": 19, "categoryId": 38, "title": "부산 전통시장 기념품 추천", "content": "자갈치시장에서 건어물 사왔는데 선물용으로 딱이었습니다.", "author": "익명", "password": "1234"},
    {"postId": 20, "categoryId": 14, "title": "부산근대역사관 방문기", "content": "옛 부산의 모습을 사진과 자료로 볼 수 있어서 흥미로웠습니다.", "author": "익명", "password": "1234"},
    {"postId": 21, "categoryId": 15, "title": "영도다리축제 다녀온 후기", "content": "다리 개폐 행사를 직접 볼 수 있어서 신기했어요. 주변 야시장도 즐길거리가 많습니다.", "author": "익명", "password": "1234"},
    {"postId": 22, "categoryId": 12, "title": "오륙도 스카이워크 추천", "content": "유리바닥이라 스릴 있어요. 날씨 좋은 날 가시면 뷰가 정말 좋습니다.", "author": "익명", "password": "1234"},
    {"postId": 23, "categoryId": 14, "title": "부산시립미술관 전시 후기", "content": "기획전 다녀왔는데 생각할 거리가 많은 전시였어요.", "author": "익명", "password": "1234"},
    {"postId": 24, "categoryId": 15, "title": "삼락생태공원 유채꽃 축제", "content": "봄에 가면 유채꽃밭이 정말 예뻐요. 자전거 타고 둘러보기도 좋습니다.", "author": "익명", "password": "1234"},
    {"postId": 25, "categoryId": 25, "title": "부산 야경 명소 코스 정리", "content": "황령산, 광안대교, 이기대 순으로 돌면 하루 야경투어 코스 완성됩니다.", "author": "익명", "password": "1234"},
    {"postId": 26, "categoryId": 28, "title": "이기대 갈맷길 트레킹 후기", "content": "난이도는 낮은 편인데 경치가 정말 좋아서 시간 가는 줄 몰랐습니다.", "author": "익명", "password": "1234"},
    {"postId": 27, "categoryId": 32, "title": "부산역 근처 숙소 접근성", "content": "KTX 타고 오시는 분들은 부산역 근처가 이동하기 편해요.", "author": "익명", "password": "1234"},
    {"postId": 28, "categoryId": 38, "title": "센텀시티 쇼핑몰 후기", "content": "비 오는 날 실내에서 쇼핑하기 좋은 곳입니다.", "author": "익명", "password": "1234"},
    {"postId": 29, "categoryId": 25, "title": "부산 원도심 야경 투어 코스", "content": "40계단부터 시작해서 야시장 골목까지 이어지는 코스로 다녀왔어요.", "author": "익명", "password": "1234"},
    {"postId": 30, "categoryId": 12, "title": "흰여울문화마을 산책 코스", "content": "영화 촬영지로 유명한데 실제로 가보니 골목마다 사진 찍을 곳이 많았어요.", "author": "익명", "password": "1234"},
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
