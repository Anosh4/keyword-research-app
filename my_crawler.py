# my_crawler.py

import time
import requests
import signaturehelper
from urllib.parse import quote

BASE_URL    = "https://api.searchad.naver.com"
API_KEY     = "0100000000f00ad936b33c28661dfecc20c4596a78bf2696da0704ccbc657d009457df5c60"
SECRET_KEY  = "AQAAAAD5G3Z/Dqcy7FShf16yRQYk4utWl6BqWj5s/YWIuraS4w=="
CUSTOMER_ID = "3210960"

def get_header(method: str, uri: str) -> dict:
    timestamp = str(round(time.time() * 1000))
    signature = signaturehelper.Signature.generate(timestamp, method, uri, SECRET_KEY)
    return {
        "Content-Type":      "application/json; charset=UTF-8",
        "X-Timestamp":       timestamp,
        "X-API-KEY":         API_KEY,
        "X-Customer":        CUSTOMER_ID,
        "X-Signature":       signature
    }

def crawl_keywords_api(base_keyword: str):
    # 1) 한글 키워드 퍼센트 인코딩 & 공백 제거
    keyword_enc = quote(base_keyword.replace(" ", ""), safe='')

    # 2) URL 직접 구성 (params 대신)
    uri      = "/keywordstool"
    full_url = f"{BASE_URL}{uri}?hintKeywords={keyword_enc}&showDetail=1"

    headers = get_header("GET", uri)

    # 3) 요청
    resp = requests.get(full_url, headers=headers)
    print("▶ Request URL   :", full_url)
    print("▶ Response Code :", resp.status_code)
    print("▶ Response Body :\n", resp.text)

    # 4) 에러 체크 & JSON 반환
    resp.raise_for_status()
    return resp.json().get("keywordList", [])
