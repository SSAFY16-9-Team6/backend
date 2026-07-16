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
    {"postId": 5, "categoryId": 32, "title": "거제 야호 미나미의 해운대 근처 숙소 후기", "content": "내가 추천한 가성비 좋은 숙소 예약할때까지 파라파라나 춰야지", "author": "익명", "password": "1696"},
    {"postId": 6, "categoryId": 11, "title": "영도 흰여울문화마을 바다뷰 미쳤네요", "content": "골목길 따라 쭉 걷는데 파란 바다가 바로 옆에 보여서 진짜 힐링돼요. 아기자기한 소품샵도 많고 인생샷 건지기 딱 좋은 곳!", "author": "영도나들이", "password": "1111"},
    {"postId": 7, "categoryId": 11, "title": "기장 아홉산숲 대나무길 다녀왔습니다", "content": "생각보다 숲이 엄청 울창하고 시원하더라고요. 천천히 산책하듯 걸으니까 1시간 반 정도 걸렸는데 머리가 맑아지는 기분입니다.", "author": "그린러버", "password": "2222"},
    {"postId": 8, "categoryId": 22, "title": "광안리 토요일 드론쇼 명당 꿀팁 방출함", "content": "해수욕장 정중앙은 사람 너무 터져서 민락수변공원 쪽으로 조금 비껴서 보는 게 훨씬 여유로워요. 자리 선점 필수입니다!", "author": "드론마니아", "password": "3333"},
    {"postId": 9, "categoryId": 44, "title": "해운대 블루라인파크 해변열차 코스 후기", "content": "미포에서 송정까지 쭉 타고 가는데 통창 밖으로 보이는 해안선이 대박입니다. 캡슐열차는 꼭 일주일 전에 예약하고 가세요.", "author": "철도여행자", "password": "4444"},
    {"postId": 10, "categoryId": 11, "title": "태종대 다누비열차 안 타면 다리 부서짐", "content": "경사가 제법 있어서 걸어가긴 힘들고 무조건 다누비열차 매표하셔야 합니다. 전망대에서 보는 탁 트인 남해 바다가 최고예요.", "author": "뚜벅이짱", "password": "5555"},
    {"postId": 11, "categoryId": 55, "title": "부산 시립미술관 현대미술 전시 관람 평점 5점", "content": "실내 데이트 코스로 다녀왔는데 전시 기획이 엄청 알차서 시간 가는 줄 몰랐네요. 주차 공간도 꽤 여유 있는 편입니다.", "author": "미술학도", "password": "6666"},
    {"postId": 12, "categoryId": 22, "title": "부산 불꽃축제 황령산 봉수대 시야 어떤가요?", "content": "광안리 해변만큼 가깝진 않지만 멀리서 광안대교랑 불꽃 전체를 조망하기엔 최고의 명당입니다. 대신 야간 산행이라 조심히 가야 해요.", "author": "야경스팟러", "password": "7777"},
    {"postId": 13, "categoryId": 11, "title": "송도 용궁구름다리 바람 엄청 부네요", "content": "케이블카 타고 건너가서 구름다리까지 세트로 도는 코스 추천합니다. 발밑으로 바다가 출렁이는 게 보여서 은근 아찔해요.", "author": "바람막이필수", "password": "8888"},
    {"postId": 14, "categoryId": 66, "title": "송정해수욕장에서 생애 첫 서핑 강습", "content": "파도가 완만해서 왕초보들이 배우기엔 송정이 딱인 듯요! 강사님도 친절하시고 몇 번 물 먹다 보니 드디어 보드 위에 섰습니다.", "author": "서린이", "password": "9999"},
    {"postId": 15, "categoryId": 11, "title": "청사포 다릿돌전망대 덧신 신고 입장해야 됨", "content": "유리 바닥으로 되어있어서 덧신 꼭 신어야 하더라고요. 바로 밑으로 파도치는 거 직관 가능한데 고소공포증 있으면 살짝 무서울 지도?", "author": "고소공포증", "password": "1010"},
    {"postId": 16, "categoryId": 77, "title": "국제시장 꽃분이네 아직도 사람 많나요?", "content": "오랜만에 남포동 나간 김에 국제시장 들러서 구경하고 먹자골목에서 씨앗호떡이랑 물떡 먹었는데 여전히 북적북적하고 재밌네요.", "author": "시장투어", "password": "1212"},
    {"postId": 17, "categoryId": 22, "title": "영도 다리 도개 시간 맞춰서 구경하고 옴", "content": "하루에 딱 한 번 낮에 도개하는데 타이밍 맞추기 은근 빡세네요. 다리 올라가는 모습이 웅장하기도 하고 신기한 구경이었습니다.", "author": "타이밍굿", "password": "1313"},
    {"postId": 18, "categoryId": 32, "title": "광안대교 뷰 끝판왕 에어비앤비 내돈내산 후기", "content": "통창으로 아침부터 밤까지 광안대교 오션뷰가 한눈에 들어오는 숙소였어요. 아침에 눈 떴을 때 윤슬 비치는 바다가 잊혀지질 않네요.", "author": "감성여행자", "password": "1414"},
    {"postId": 19, "categoryId": 11, "title": "감천문화마을 어린왕자 동상이랑 사진 찍는 대기줄", "content": "주말 낮에 갔더니 어린왕자 옆에서 뒷모습 사진 찍으려고 대기만 30분 넘게 했네요. 그래도 알록달록한 마을 배경이 너무 예쁩니다.", "author": "인생샷사냥꾼", "password": "1515"},
    {"postId": 20, "categoryId": 44, "title": "부산 당일치기 알짜배기 동부 코스 제안", "content": "해운대 블루라인파크 -> 해동용궁사 -> 기장 롯데월드 아웃렛 쇼핑 코스로 도니까 하루 아주 꽉 찬 일정으로 잘 놀고 왔습니다.", "author": "프로계획러", "password": "1616"},
    {"postId": 21, "categoryId": 22, "title": "벡스코 지스타 축제 보러 원정 왔습니다!", "content": "역대급 스케일이라 볼거리 진짜 많고 대기 줄도 어마어마하네요. 내일 방문하실 분들은 얇은 옷 여러 겹 입고 오시길 추천합니다.", "author": "게이머", "password": "1717"},
    {"postId": 22, "categoryId": 11, "title": "해동용궁사 파도 소리랑 절 풍경의 조화", "content": "보통 절은 산속에 있는데 바다 바로 앞에 있으니까 진짜 이색적이고 멋져요. 파도치는 절벽 위의 사찰이라니 풍경이 명화 수준입니다.", "author": "풍경러버", "password": "1818"},
    {"postId": 23, "categoryId": 22, "title": "부산 수영강 카약 축제 체험하고 왔어요", "content": "강바람 맞으면서 센텀시티 고층 빌딩 숲 사이로 카약 타니까 기분 묘하네요. 초등학생 아이들도 쉽게 탈 수 있을 정도로 안전했습니다.", "author": "카약러버", "password": "1919"},
    {"postId": 24, "categoryId": 44, "title": "영도 흰여울마을 갔다가 태종대 조개구이 먹는 하루 코스", "content": "낮에는 영도 흰여울길 걷고, 해 질 무렵 태종대 자갈마당 가서 바다 보며 조개구이에 소주 한잔 걸치는 코스. 완벽한 로컬 힐링입니다.", "author": "먹고죽자", "password": "2020"},
    {"postId": 25, "categoryId": 32, "title": "부산 영도 가성비 비즈니스 호텔 추천", "content": "위치도 남포동이랑 영도 대교 다 가깝고 신축이라 엄청 깔끔해요. 가성비 좋게 잠만 잘 용도로 부산 출장이나 뚜벅이 여행객에게 딱임.", "author": "가성비추구", "password": "2121"},
    {"postId": 26, "categoryId": 11, "title": "초량 이바구길 모노레일 타보신 분 계신가요?", "content": "경사가 어마무시해서 모노레일 타고 올라가는데 아찔하면서도 재밌었어요. 정상에서 바라보는 부산항 대교 전망이 기가 막힙니다.", "author": "동네탐험가", "password": "2222"},
    {"postId": 27, "categoryId": 11, "title": "동래읍성 둘레길 조용하게 산책하기 참 좋네요", "content": "사람 북적이는 바닷가가 질릴 때쯤 오기 딱 좋은 숨은 명소입니다. 성곽길 따라 잔디밭이 잘 가꾸어져 있어서 걷기만 해도 편안해져요.", "author": "산책마니아", "password": "2323"},
    {"postId": 28, "categoryId": 22, "title": "해운대 모래축제 작품들 퀄리티 대박이네요", "content": "모래로 어떻게 이렇게 정교하게 겨울왕국 캐릭터들을 조각했는지 신기할 따름입니다. 주말이라 주차가 헬이니 대중교통 이용하세요.", "author": "모래성", "password": "2424"},
    {"postId": 29, "categoryId": 11, "title": "오륙도 스카이워크 유리 깨질까 봐 쫄았음", "content": "발밑이 바로 낭떠러지 바다라 심장 쫄깃해집니다. 짧은 코스지만 오륙도의 강한 바닷바람 맞으면서 스릴 느끼기엔 최고예요.", "author": "심장쿵", "password": "2525"},
    {"postId": 30, "categoryId": 22, "title": "부산 자갈치 크루즈 축제 불꽃놀이 후기", "content": "배 위에서 갈매기 밥도 주고 남항대교 야경 감상하는 코스인데, 하이라이트인 선상 불꽃놀이가 정말 낭만적이었습니다.", "author": "선장님", "password": "2626"},
    {"postId": 31, "categoryId": 11, "title": "다대포 해수욕장 노을 낙조 분수 꼭 보세요", "content": "부산에서 노을 제일 예쁜 곳을 꼽으라면 단연 다대포입니다. 낙조 분수 쇼까지 세트로 감상하고 오면 완벽한 저녁 데이트 완성이에요.", "author": "노을중독", "password": "2727"},
    {"postId": 32, "categoryId": 11, "title": "부산 전포 카페거리 골목 투어", "content": "아기자기하고 이국적인 인테리어의 개인 카페들이 골목마다 숨겨져 있어서 구경하는 재미가 쏠쏠해요. 커피 맛집 투어로 강추!", "author": "커피러버", "password": "2828"},
    {"postId": 33, "categoryId": 22, "title": "삼락생태공원 벚꽃축제 인파 장난 아니네요", "content": "낙동강 변 따라 끝없이 펼쳐진 벚꽃 터널이 장관입니다. 이번 주말이 절정일 것 같으니 돗자리 챙겨서 꼭 다녀와 보세요.", "author": "봄봄봄", "password": "2929"},
    {"postId": 34, "categoryId": 11, "title": "금정산성 막걸리에 파전 먹으러 등산함", "content": "범어사 코스로 가볍게 등산하고 산성마을 내려와서 오리불고기에 금정산성 막걸리 한잔 걸치니 세상 부러울 게 없는 하루입니다.", "author": "막걸리파", "password": "3030"},
    {"postId": 35, "categoryId": 22, "title": "부산 바다미술제 다대포 해변 전시 보고 옴", "content": "넓은 모래사장 전체가 거대한 미술관으로 변신해서 이색적이었어요. 자연과 예술 작품이 어우러지는 풍경이 꽤나 멋졌습니다.", "author": "예술사랑", "password": "3131"}
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
