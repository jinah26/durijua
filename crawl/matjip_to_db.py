import requests
import pprint
import urllib.parse
import time
from pymongo import MongoClient

def populate_matjip_db(client, db):

    # 서울시 구마다 맛집을 검색해보겠습니다.
    # seoul_gu = ["종로구", "중구", "용산구", "성동구", "광진구", "동대문구", "중랑구", "성북구", "강북구", "도봉구", "노원구", "은평구", "서대문구", "마포구", "양천구", "강서구", "구로구", "금천구", "영등포구", "동작구", "관악구", "서초구", "강남구", "송파구", "강동구"]
    seoul_gu = ["강남구"]

    client_id = "ESmgVXGmUyrdpoAYf6lA"
    client_secret =  "sR52eHmUTr"

    def get_naver_result(keyword):
        time.sleep(0.1)
        api_url = f"https://openapi.naver.com/v1/search/local.json?query={keyword}&display=30&start=1&sort=random"
        headers = {'X-Naver-Client-Id': client_id, 'X-Naver-Client-Secret': client_secret }
        data = requests.get(api_url, headers=headers)
        data = data.json()
        return data['items']


    # 저장할 전체 맛집 목록입니다.
    docs = []
    # 구별로 검색을 실행합니다.
    for gu in seoul_gu:
        # '강님구 맛집', '종로구 맛집', '용산구 맛집' .. 을 반복해서 인코딩합니다.
        keyword = f'{gu} 맛집'
        # 맛집 리스트를 받아옵니다.
        matjip_list = get_naver_result(keyword)

        # 구별 맛집 구분선입니다.
        print("*"*80 + gu)
        for matjip in matjip_list[:30]:
            # 구 정보를 추가합니다.
            matjip['gu'] = gu
            # 맛집을 인쇄합니다.
            pprint.pprint(matjip)
            # docs에 맛집을 추가합니다.
            docs.append(matjip)

   

 
    # 맛집 정보를 저장합니다.
    db.user.insert_many(docs)
    print("Done with populate db.")
    return db