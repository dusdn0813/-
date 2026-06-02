import streamlit as tf
import google.generativeai as genai

# 1. 페이지 설정 및 제목
st.set_page_config(page_title="수행평가 알리미", page_icon="📅")
st.title("📅 수행평가 알리미 챗봇")
st.caption("수행평가 일정 관리, 준비물, 팁 등을 물어보세요!")

# 2. Streamlit Secrets에서 API 키 불러오기 및 설정
try:
    if "GEMINI_API_KEY" not in st.secrets:
        st.error("Secrets에 'GEMINI_API_KEY'가 설정되지 않았습니다. Streamlit 대시보드에서 설정해주세요.")
        st.stop()
    
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except Exception as e:
    st.error(f"API 키를 설정하는 중 오류가 발생했습니다: {e}")
    st.stop()

# 3. 세션 상태(Session State)로 채팅 기록 초기화
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant", 
            "content": "안녕하세요! 수행평가 알리미입니다. 어떤 수행평가에 대해 도움이 필요하신가요? (예: 고1 통합과학 수행평가 주제 추천해줘)"
        }
    ]

# 4. 이전 채팅 기록 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 5. 사용자 입력 받기
if user_input := st.chat_input("수행평가에 대해 무엇이든 물어보세요!"):
    
    # 사용자의 메시지를 화면에 표시 및 세션에 저장
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # 6. Gemini 모델을 통한 답변 생성 (오류 처리 포함)
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("🔄 생각 중...")
        
        try:
            # gemini-2.5-flash-lite 모델 설정
            model = genai.GenerativeModel(
                model_name="gemini-2.5-flash-lite",
                system_instruction="당신은 학생들의 수행평가를 도와주는 '수행평가 알리미'입니다. 친절하고 명확하게 답변해야 하며, 수행평가 일정 관리법, 과목별 보고서 작성 팁, 발표 자료 준비 가이드 등을 전문적으로 안내해주세요."
            )
            
            # 대화 맥락을 유지하기 위해 세션 기록을 Gemini 형식으로 변환
            chat_history = []
            for msg in st.session_state.messages[:-1]:  # 방금 넣은 user_input 제외 전까지
                role = "user" if msg["role"] == "user" else "model"
                chat_history.append({"role": role, "parts": [msg["content"]]})
            
            # 채팅 세션 시작 및 메시지 전송
            chat = model.start_chat(history=chat_history)
            response = chat.send_message(user_input)
            
            # 결과 출력 및 저장
            ai_response = response.text
            message_placeholder.markdown(ai_response)
            st.session_state.messages.append({"role": "assistant", "content": ai_response})
            
        except Exception as e:
            error_msg = f"❌ 답변을 생성하는 중 오류가 발생했습니다: {e}"
            message_placeholder.markdown(error_msg)
            # 오류 메시지는 세션 기록에 저장하지 않음
