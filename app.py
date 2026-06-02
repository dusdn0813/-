import streamlit as st
from google import genai
from google.genai import types
from google.genai.errors import APIError

# 1. 페이지 설정 및 제목
st.set_page_config(page_title="수행평가 알리미", page_icon="📝", layout="centered")
st.title("📝 수행평가 알리미 챗봇")
st.caption("수행평가 일정 관리, 준비물, 팁 등을 물어보세요!")

# 2. API 키 및 클라이언트 초기화 (Streamlit Secrets 활용)
if "GEMINI_API_KEY" not in st.secrets:
    st.error("⚠️ Streamlit Secrets에 'GEMINI_API_KEY'가 설정되지 않았습니다. 서비스 설정에서 API 키를 입력해주세요.")
    st.stop()

try:
    # google-genai 최신 SDK 스타일로 클라이언트 초기화
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
except Exception as e:
    st.error(f"⚠️ API 클라이언트 초기화 중 오류가 발생했습니다: {e}")
    st.stop()

# 3. 세션 상태(Session State)를 활용한 채팅 기록 유지
if "messages" not in st.session_state:
    st.session_state.messages = []

# 4. 앱을 처음 켤 때 챗봇에게 페르소나 주입 (System Instruction)
# gemini-2.5-flash-lite는 시스템 지침을 지원합니다.
system_instruction = """
당신은 고등학생들의 수행평가를 전반적으로 도와주는 '수행평가 알리미'입니다.
학생들이 수행평가 일정 관리, 과제 작성 팁, 발표 자료 준비 방법, 과목별 핵심 체크리스트 등을 물어보면
친절하고, 명확하며, 격려하는 어조로 답변해주세요. 
답변을 할 때는 가독성이 좋게 이모지나 불릿 포인트를 적절히 사용해 주세요.
"""

# 5. 기존 채팅 기록 화면에 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 6. 사용자 입력 처리
if user_input := st.chat_input("예: '확률과 통계 수행평가 보고서 주제 추천해줘'"):
    
    # 사용자가 입력한 메시지 화면에 표시 및 기록 저장
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # 챗봇의 답변 생성 과정
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        try:
            # API 호출 및 스트리밍 답변 생성
            # 요구사항대로 'gemini-2.5-flash-lite' 모델 지정
            response = client.models.generate_content_stream(
                model='gemini-2.5-flash-lite',
                contents=user_input,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.7,
                )
            )
            
            # 스트리밍 텍스트 실시간 누적
            full_response = ""
            for chunk in response:
                full_response += chunk.text
                message_placeholder.markdown(full_response + "▌")
            
            # 최종 답변 확정 표시
            message_placeholder.markdown(full_response)
            
            # 챗봇의 답변도 기록에 저장
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except APIError as ae:
            # 구글 API 관련 명시적 에러 처리
            error_msg = f"❌ Gemini API 오류가 발생했습니다: {ae.message}"
            message_placeholder.markdown(error_msg)
            st.sidebar.error(f"상세 에러: {ae}")
        except Exception as e:
            # 기타 예외 처리 (네트워크 오류 등)
            error_msg = "❌ 답변을 생성하는 중 알 수 없는 오류가 발생했습니다. 잠시 후 다시 시도해주세요."
            message_placeholder.markdown(error_msg)
            st.sidebar.error(f"일반 에러: {e}")
