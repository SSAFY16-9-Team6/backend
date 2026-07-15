import json
import os
from backend import database, models

def load_places(json_path: str):
    from backend.database import SessionLocal
    session = SessionLocal()
    with open(json_path, encoding='utf-8') as f:
        data = json.load(f)
    # expect data to be a list of place dicts
    for item in data:
        content_id = str(item.get('contentId') or item.get('content_id') or item.get('id') or '')
        if not content_id:
            continue
        p = models.Place(
            contentId=content_id,
            categoryId=item.get('categoryId') or item.get('category_id'),
            title=item.get('title') or item.get('name'),
            address=item.get('address'),
            thumbnail=item.get('thumbnail') or item.get('image'),
            mapX=item.get('mapX') or item.get('map_x') or item.get('lng') or item.get('longitude'),
            mapY=item.get('mapY') or item.get('map_y') or item.get('lat') or item.get('latitude'),
            # optional codes
            lDongRegnCd=item.get('lDongRegnCd') or item.get('l_dong_regn_cd'),
            lDongSignguCd=item.get('lDongSignguCd') or item.get('l_dong_signgu_cd'),
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
