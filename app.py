import streamlit as st
import pandas as pd
import json
import os

# 데이터 저장 파일
DATA_FILE = "tasks_web.json"

# 데이터 로드 함수
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []

# 데이터 저장 함수
def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# Streamlit 앱 제목
st.set_page_config(page_title="수행평가 관리자", layout="centered")
st.title("📋 수행평가 일정 관리 앱")
st.write("학습용 수행평가 일정을 기록하고 관리해보세요!")

# 세션 상태 초기화 (데이터 유지)
if "tasks" not in st.session_state:
    st.session_state.tasks = load_data()

# --- 입력 폼 세션 ---
with st.form(key="task_form", clear_on_submit=True):
    st.subheader("새로운 수행평가 추가")
    col1, col2 = st.columns(2)
    
    with col1:
        subject = st.text_input("과목명", placeholder="예: 수학, 영어")
    with col2:
        date = st.date_input("마감일")
        
    content = st.text_input("수행평가 내용", placeholder="예: 교과서 문제 풀이 제출")
    submit_button = st.form_submit_button(label="추가하기")

# 추가 버튼 클릭 시 로직
if submit_button:
    if subject.strip() == "" or content.strip() == "":
        st.warning("과목명과 내용을 모두 입력해주세요!")
    else:
        new_task = {
            "과목": subject,
            "수행평가 내용": content,
            "마감일": str(date)
        }
        st.session_state.tasks.append(new_task)
        save_data(st.session_state.tasks)
        st.success(f"'{subject}' 수행평가 일정이 추가되었습니다!")

# --- 일정 출력 및 삭제 세션 ---
st.write("---")
st.subheader("현재 수행평가 일정 목록")

if st.session_state.tasks:
    # 데이터프레임으로 변환 후 마감일 순 정렬
    df = pd.DataFrame(st.session_state.tasks)
    df = df.sort_values(by="마감일").reset_index(drop=True)
    
    # 표 출력
    st.dataframe(df, use_container_width=True)
    
    # 삭제 기능
    st.write("### 일정 삭제하기")
    delete_options = [f"[{t['마감일']}] {t['과목']} - {t['수행평가 내용']}" for t in st.session_state.tasks]
    selected_to_delete = st.selectbox("삭제할 항목을 선택하세요", delete_options)
    
    if st.button("선택 항목 삭제", type="primary"):
        idx = delete_options.index(selected_to_delete)
        deleted_item = st.session_state.tasks.pop(idx)
        save_data(st.session_state.tasks)
        st.info(f"'{deleted_item['과목']}' 일정이 삭제되었습니다.")
        st.rerun()
else:
    st.info("등록된 수행평가 일정이 없습니다. 위에 새로 추가해보세요!")ㅍ
