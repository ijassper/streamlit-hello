from openai import OpenAI, RateLimitError
import streamlit as st

st.set_page_config(page_title="ChatGPT Clone", layout="wide")

# 🧼 CSS: 중앙 입력창용, 입력창 폭 제한
st.markdown("""
    <style>
    .centered-input-container {
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        height: 80vh;
        text-align: center;
    }
    [data-testid="stChatInput"] {
        max-width: 700px;
        margin: 0 auto;
    }
    </style>
""", unsafe_allow_html=True)

# 📌 API 설정
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# 상태 초기화
if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"
if "messages" not in st.session_state:
    st.session_state.messages = []
if "history" not in st.session_state:
    st.session_state.history = []

# 🔹 사이드바: 대화 기록
with st.sidebar:
    st.header("💬 대화 기록")
    if st.session_state.history:
        for i, item in enumerate(st.session_state.history):
            if st.button(item["title"], key=f"history_{i}"):
                st.session_state.messages = item["full"]
                st.experimental_rerun()
    if st.button("🗑️ 기록 초기화"):
        st.session_state.history.clear()
        st.session_state.messages.clear()
        st.experimental_rerun()

# 🔹 1. 첫 화면 (대화 전)
if not st.session_state.messages:
    st.markdown('<div class="centered-input-container">', unsafe_allow_html=True)
    st.title("💬 ChatGPT-like Clone")
    st.subheader("무엇이 궁금한가요?")
    user_input = st.chat_input("여기에 입력하세요...")
    st.markdown('</div>', unsafe_allow_html=True)

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.experimental_rerun()

# 🔹 2. 채팅 화면 (대화 시작 후)
else:
    # 이전 메시지 렌더링
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # 입력 받기 (하단 고정)
    if prompt := st.chat_input("질문을 입력하세요..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            try:
                stream = client.chat.completions.create(
                    model=st.session_state["openai_model"],
                    messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
                    stream=True,
                )
                full_response = ""
                placeholder = st.empty()
                for chunk in stream:
                    content = getattr(chunk.choices[0].delta, "content", None)
                    if content:
                        full_response += content
                        placeholder.markdown(full_response)

                # 응답 저장
                st.session_state.messages.append({"role": "assistant", "content": full_response})

                # 요약 저장
                summary = prompt[:30] + ("..." if len(prompt) > 30 else "")
                st.session_state.history.append({
                    "title": summary,
                    "full": st.session_state.messages.copy()
                })

            except RateLimitError:
                st.error("⚠️ 요청이 너무 많습니다. 잠시 후 다시 시도해 주세요.")
            except Exception as e:
                st.error(f"❌ 오류 발생: {e}")
