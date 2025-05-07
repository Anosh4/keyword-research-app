import streamlit as st
import pandas as pd
import re
from my_crawler import crawl_keywords_api
from shopping_analysis import render_shopping_tab

# ── 페이지 설정 & CSS ─────────────────────────────────────────
st.set_page_config(layout="wide")
st.markdown("""
    <style>
      /* 탭을 페이지 상단으로 밀어올리기 */
      [data-testid="stTabs"] {
        margin-top: 10px;
      }
      html, body, [class*="css"] {
        font-size: 24px !important;
      }
    </style>
""", unsafe_allow_html=True)

# ── 유틸 함수 ──────────────────────────────────────────────────
def parse_count(val):
    try: return int(val)
    except:
        if isinstance(val, str):
            m = re.search(r"(\d+)", val)
            if m: return int(m.group(1))
    return 0

def do_search():
    rows = []
    for kw in [k.strip() for k in st.session_state.keywords_input.split(",") if k.strip()]:
        for item in crawl_keywords_api(kw):
            pc = parse_count(item.get("monthlyPcQcCnt",0))
            mo = parse_count(item.get("monthlyMobileQcCnt",0))
            rows.append({
                "기준키워드":   kw,
                "연관키워드":   item.get("relKeyword",""),
                "PC검색량":     pc,
                "모바일검색량": mo,
                "총검색량":     pc+mo,
                "경쟁강도":     item.get("compIdx","")
            })
    df = pd.DataFrame(rows)
    for c in ["PC검색량","모바일검색량","총검색량"]:
        df[c] = pd.to_numeric(df[c],errors="coerce").fillna(0).astype(int)
    st.session_state.df = df

# ── 상단 탭 생성 ───────────────────────────────────────────────
tab1, tab2 = st.tabs(["키워드 리서치 대시보드", "쇼핑 키워드 분석"])

# ── 탭1: 키워드 리서치 ────────────────────────────────────────
with tab1:
    st.title("🕵️‍♀️ 키워드 리서치 대시보드")

    st.text_input(
        "기준 키워드 (콤마로 구분)",
        key="keywords_input",
        on_change=do_search,
        placeholder="예) 산리오, 오버핏 셔츠"
    )
    if st.button("검색 시작"):
        do_search()

    df = st.session_state.get("df", pd.DataFrame())
    if df.empty:
        st.info("🔍 검색 결과가 없습니다.")
    else:
        st.success(f"✅ 총 {len(df)}개 결과 수집 완료")

        sub1, sub2 = st.tabs(["전체 보기","필터링 뷰"])
        with sub1:
            st.dataframe(df, use_container_width=True, height=700)
        with sub2:
            # 필터링 뷰
            if "total_slider" not in st.session_state:
                st.session_state.total_slider = int(df["총검색량"].min())
            if "total_input" not in st.session_state:
                st.session_state.total_input = st.session_state.total_slider

            def _sync_input(): st.session_state.total_input = st.session_state.total_slider
            def _sync_slider(): st.session_state.total_slider = st.session_state.total_input

            cs, ci = st.columns([3,1])
            mn, mx = int(df["총검색량"].min()), int(df["총검색량"].max())
            cs.slider("최소 총검색량", mn, mx,
                      key="total_slider", on_change=_sync_input)
            ci.number_input("", mn, mx,
                            key="total_input", on_change=_sync_slider,
                            label_visibility="collapsed")

            comps = st.multiselect("경쟁강도 선택",
                                   df["경쟁강도"].unique().tolist(),
                                   default=df["경쟁강도"].unique().tolist())
            filt = df[(df["총검색량"]>=st.session_state.total_slider)&
                      (df["경쟁강도"].isin(comps))]
            st.dataframe(filt, use_container_width=True, height=700)

        # 경쟁강도별 합계
                # ─── 경쟁강도별 합계 검색량 ─────────────────────────────
        st.header("경쟁강도별 합계 검색량")

        # 1) slider / number_input 에 중복 없는 key 부여
        if "top_n_slider" not in st.session_state:
            st.session_state.top_n_slider = 10
        if "top_n_input" not in st.session_state:
            st.session_state.top_n_input = st.session_state.top_n_slider

        def _sync_input():
            # slider → input 동기화
            st.session_state.top_n_input = st.session_state.top_n_slider

        def _sync_slider():
            # input → slider 동기화
            st.session_state.top_n_slider = st.session_state.top_n_input

        c_s, c_i = st.columns([3, 1])
        c_s.slider(
            "Top N", 5, 40,
            key="top_n_slider",
            on_change=_sync_input
        )
        c_i.number_input(
            "", 5, 40,
            key="top_n_input",
            label_visibility="collapsed",
            on_change=_sync_slider
        )

        # 2) 대표값은 slider 쪽(top_n_slider)으로 읽어와서 사용
        N = st.session_state.top_n_slider

        c1, c2, c3 = st.columns(3)
        for col, lvl in zip((c1, c2, c3), ("높음", "중간", "낮음")):
            with col:
                st.subheader(lvl)
                st.table(
                    df[df["경쟁강도"] == lvl]
                      .nlargest(N, "총검색량")[["연관키워드", "총검색량"]]
                )

# ── 탭2: 쇼핑 키워드 분석 ─────────────────────────────────────
with tab2:
    render_shopping_tab()
