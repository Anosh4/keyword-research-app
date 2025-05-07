# shopping_analysis.py

from collections import Counter
import pandas as pd
import streamlit as st
import re
from urllib.parse import quote
import requests

# ─── 여기에 직접 발급받은 인증 정보를 넣으세요 ───
client_id     = "vFU_GHGD2iJ4TcdLHg4t"
client_secret = "cdVA8fwU2Z"

def fetch_shopping_titles(query: str, pages: int, per_page: int):
    titles = []
    for page in range(1, pages + 1):
        start = (page - 1) * per_page + 1
        url = (
            "https://openapi.naver.com/v1/search/shop.json"
            f"?query={quote(query)}"
            f"&display={per_page}"
            f"&start={start}"
        )
        headers = {
            "X-Naver-Client-Id":     client_id,
            "X-Naver-Client-Secret": client_secret,
        }
        resp = requests.get(url, headers=headers)
        resp.raise_for_status()
        data = resp.json().get("items", [])
        # 제목에 있는 HTML 태그 제거
        cleaned = [re.sub(r"<.*?>", "", item["title"]) for item in data]
        titles.extend(cleaned)
    return titles

def render_shopping_tab():
    st.markdown("## 🛍 네이버 쇼핑 상품 제목 키워드 빈도")

    query    = st.text_input("검색어를 입력하세요")
    per_page = st.slider("페이지당 상품 수", 10, 100, 40)
    max_pages = 1000 // per_page
    pages     = st.slider("몇 페이지까지 스크랩할까요?", 1, max_pages, 1)

    if st.button("분석 시작"):
        if not query:
            st.warning("검색어를 입력해주세요.")
            return

        # 1) 제목 수집
        titles = fetch_shopping_titles(query, pages, per_page)

        # 2) 단어 토큰화
        words = []
        for t in titles:
            words += re.findall(r"\w+", t)

        # 3) 빈도 계산
        freq = Counter(words)

        # 4) Top N 고정 (최대 50개)
        TOP_N = 50
        common = freq.most_common(min(TOP_N, len(freq)))

        df = pd.DataFrame(common, columns=["단어", "빈도"])

        # 5) 차트 & 테이블 출력
        st.bar_chart(df.set_index("단어")["빈도"])
        st.dataframe(df, use_container_width=True)
