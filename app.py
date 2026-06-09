import streamlit as st
import pandas as pd
from datetime import datetime
import calendar
import os

st.set_page_config(
    page_title="학급 학사일정 캘린더",
    page_icon="📚",
    layout="wide"
)

DATA_FILE = "schedule_data.csv"

# -----------------------------
# 데이터 저장/불러오기 함수
# -----------------------------
def load_data():
    try:
        if os.path.exists(DATA_FILE):
            return pd.read_csv(DATA_FILE)
        else:
            return pd.DataFrame(
                columns=["date", "title", "category"]
            )
    except Exception:
        return pd.DataFrame(
            columns=["date", "title", "category"]
        )

def save_data(df):
    try:
        df.to_csv(DATA_FILE, index=False)
    except Exception as e:
        st.error(f"저장 오류: {e}")

# -----------------------------
# 데이터 로드
# -----------------------------
if "schedule_df" not in st.session_state:
    st.session_state.schedule_df = load_data()

df = st.session_state.schedule_df

# -----------------------------
# 제목
# -----------------------------
st.title("📚 학급 학사일정 캘린더")
st.caption("시험, 수행평가, 과제, 학교행사를 한눈에 관리하세요.")

# -----------------------------
# 사이드바
# -----------------------------
with st.sidebar:
    st.header("➕ 일정 추가")

    selected_date = st.date_input(
        "날짜 선택",
        value=datetime.today()
    )

    title = st.text_input(
        "일정 내용",
        placeholder="예) 수학 수행평가"
    )

    category = st.selectbox(
        "일정 종류",
        [
            "시험",
            "수행평가",
            "과제",
            "학교행사",
            "기타"
        ]
    )

    if st.button("일정 저장"):
        if title.strip() == "":
            st.warning("일정 내용을 입력하세요.")
        else:
            new_row = pd.DataFrame(
                [{
                    "date": selected_date.strftime("%Y-%m-%d"),
                    "title": title.strip(),
                    "category": category
                }]
            )

            st.session_state.schedule_df = pd.concat(
                [st.session_state.schedule_df, new_row],
                ignore_index=True
            )

            save_data(st.session_state.schedule_df)

            st.success("일정이 저장되었습니다.")
            st.rerun()

    st.divider()

    uploaded = st.file_uploader(
        "CSV 불러오기",
        type=["csv"]
    )

    if uploaded:
        try:
            imported_df = pd.read_csv(uploaded)

            required_cols = {"date", "title", "category"}

            if required_cols.issubset(imported_df.columns):
                st.session_state.schedule_df = imported_df
                save_data(imported_df)
                st.success("불러오기 완료")
            else:
                st.error("올바른 CSV 파일이 아닙니다.")

        except Exception as e:
            st.error(f"불러오기 오류: {e}")

# -----------------------------
# 달력 설정
# -----------------------------
col1, col2 = st.columns([1, 1])

with col1:
    year = st.number_input(
        "연도",
        min_value=2020,
        max_value=2100,
        value=datetime.today().year
    )

with col2:
    month = st.selectbox(
        "월",
        list(range(1, 13)),
        index=datetime.today().month - 1
    )

# -----------------------------
# 카테고리 색상
# -----------------------------
category_colors = {
    "시험": "#ffb3b3",
    "수행평가": "#ffe0a3",
    "과제": "#b3e6ff",
    "학교행사": "#c8f7c5",
    "기타": "#dddddd"
}

# -----------------------------
# 달력 생성
# -----------------------------
cal = calendar.monthcalendar(year, month)

weekdays = ["월", "화", "수", "목", "금", "토", "일"]

header_cols = st.columns(7)

for idx, day in enumerate(weekdays):
    header_cols[idx].markdown(
        f"### {day}"
    )

for week in cal:
    cols = st.columns(7)

    for i, day in enumerate(week):

        if day == 0:
            cols[i].write("")
            continue

        current_date = f"{year}-{month:02d}-{day:02d}"

        day_events = df[df["date"] == current_date]

        html = f"""
        <div style="
            border:1px solid #cccccc;
            border-radius:8px;
            padding:5px;
            min-height:140px;
        ">
        <b>{day}</b><br>
        """

        for _, row in day_events.iterrows():

            color = category_colors.get(
                row["category"],
                "#dddddd"
            )

            html += f"""
            <div style="
                background:{color};
                padding:3px;
                margin-top:3px;
                border-radius:5px;
                font-size:12px;
            ">
            [{row['category']}]<br>
            {row['title']}
            </div>
            """

        html += "</div>"

        cols[i].markdown(
            html,
            unsafe_allow_html=True
        )

# -----------------------------
# 일정 목록
# -----------------------------
st.divider()

st.subheader("📋 전체 일정")

if not df.empty:

    display_df = df.copy()
    display_df.columns = [
        "날짜",
        "일정",
        "종류"
    ]

    st.dataframe(
        display_df.sort_values("날짜"),
        use_container_width=True
    )

    csv = df.to_csv(index=False).encode("utf-8-sig")

    st.download_button(
        "📥 CSV 다운로드",
        data=csv,
        file_name="class_schedule.csv",
        mime="text/csv"
    )

    delete_idx = st.selectbox(
        "삭제할 일정 선택",
        range(len(df)),
        format_func=lambda x:
            f"{df.iloc[x]['date']} | {df.iloc[x]['title']}"
    )

    if st.button("🗑 일정 삭제"):
        st.session_state.schedule_df = (
            df.drop(index=delete_idx)
            .reset_index(drop=True)
        )

        save_data(st.session_state.schedule_df)

        st.success("삭제 완료")
        st.rerun()

else:
    st.info("등록된 일정이 없습니다.")
