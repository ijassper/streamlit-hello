from openai import OpenAI, RateLimitError
import streamlit as st

st.set_page_config(page_title="나만의 챗GPT", layout="wide")

st.title("ChatGPT-like clone")

# API 키 로드
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# 모델 설정
if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

# 메시지 세션 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

# 대화 히스토리 요약 목록 (간단한 요약만 저장)
if "history" not in st.session_state:
    st.session_state.history = []

# 사이드바에 채팅 요약 목록 표시
with st.sidebar:
    st.header("💬 대화 기록")
    if st.session_state.history:
        for i, item in enumerate(st.session_state.history):
            if st.button(item, key=f"history_{i}"):
                # 기록을 클릭하면 해당 내용을 메시지로 복원
                st.session_state.messages = item["full"]
                st.experimental_rerun()
    if st.button("🗑️ 기록 초기화"):
        st.session_state.history.clear()
        st.session_state.messages.clear()
        st.experimental_rerun()

# 이전 메시지 렌더링
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 사용자 입력 처리
if prompt := st.chat_input("What is up?"):
    # 사용자 메시지 저장 및 표시
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 어시스턴트 응답 처리
    with st.chat_message("assistant"):
        try:
            # 스트리밍 응답 생성
            stream = client.chat.completions.create(
                model=st.session_state["openai_model"],
                messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
                stream=True,
            )

            # 응답 점차 출력 및 누적
            full_response = ""
            placeholder = st.empty()
            for chunk in stream:
                content = getattr(chunk.choices[0].delta, "content", None)
                if content:
                    full_response += content
                    placeholder.markdown(full_response)

            # 응답 저장
            st.session_state.messages.append({"role": "assistant", "content": full_response})

            # 요약 저장 (사이드바용)
            summary = prompt[:30] + ("..." if len(prompt) > 30 else "")
            st.session_state.history.append({
                "title": summary,
                "full": st.session_state.messages.copy()
            })

        except RateLimitError:
            st.error("⚠️ 요청이 너무 많습니다. 잠시 후 다시 시도해 주세요.")
        except Exception as e:
            st.error(f"❌ 오류 발생: {e}")
