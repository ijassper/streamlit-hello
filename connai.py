import google.generativeai as genai
import streamlit as st

# --- 페이지 설정 및 제목 ---
st.set_page_config(page_title="My Gemini Chat", page_icon="✨")
st.title("My Own Gemini Chat ✨")

# --- 사이드바 설정 ---
with st.sidebar:
    st.header("⚙️ 설정")
    
    # Google AI Studio API 키 입력
    # Streamlit의 secrets.toml 파일에 GOOGLE_API_KEY = "YOUR_API_KEY" 형식으로 저장하세요.
    try:
        google_api_key = st.secrets["GOOGLE_API_KEY"]
        genai.configure(api_key=google_api_key)
    except (KeyError, FileNotFoundError):
        st.warning("사이드바에서 Google API 키를 secrets.toml에 설정해주세요.")
        st.stop()

    # 모델 선택 (Gemini 모델 목록)
    # 최신 모델은 https://ai.google.dev/models/gemini 에서 확인 가능
    selected_model = st.selectbox(
        "모델을 선택하세요",
        ["gemini-1.5-pro-latest", "gemini-1.0-pro"],
        key="google_model"
    )

    # 페르소나 설정 (System Prompt) -> Gemini에서는 'system_instruction'으로 사용
    system_prompt = st.text_area(
        "AI 페르소나를 설정하세요 (System Instruction)",
        "당신은 친절하고 명료하게 설명해주는 AI 비서입니다. 항상 한국어로 대답해주세요.",
        height=150
    )

    # 새 대화 시작 버튼
    if st.button("새 대화 시작", type="primary"):
        # Gemini는 대화 기록을 Role-based로 관리
        st.session_state.messages = []
        st.toast("새로운 대화를 시작합니다!", icon="✨")

# --- 메인 채팅 화면 ---

# GenerativeModel 초기화
model = genai.GenerativeModel(
    model_name=st.session_state.google_model,
    system_instruction=system_prompt  # 시스템 프롬프트 설정
)

# 세션에 메시지가 없으면 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

# 이전 대화 내용 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 사용자 입력 처리
if prompt := st.chat_input("무엇이 궁금하신가요?"):
    # 사용자 메시지 저장 및 표시
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 어시스턴트 응답 처리
    with st.chat_message("assistant"):
        try:
            # Gemini API는 메시지 형식을 약간 다르게 요구합니다.
            # user -> model (assistant) -> user -> model 순서가 되어야 합니다.
            # API에 전달할 메시지 포맷팅
            messages_for_api = []
            for msg in st.session_state.messages:
                # Gemini는 'assistant' 대신 'model'이라는 role을 사용합니다.
                role = "model" if msg["role"] == "assistant" else msg["role"]
                messages_for_api.append({"role": role, "content": msg["content"]})

            # 스트리밍 응답 생성
            stream = model.generate_content(messages_for_api, stream=True)

            # 응답을 점차적으로 표시
            full_response = ""
            placeholder = st.empty()
            for chunk in stream:
                # chunk.text 로 바로 텍스트에 접근 가능 (OpenAI보다 간단)
                full_response += chunk.text
                placeholder.markdown(full_response + "▌")
            
            placeholder.markdown(full_response)

            # 전체 응답을 세션에 'assistant' role로 저장 (UI 통일을 위해)
            st.session_state.messages.append(
                {"role": "assistant", "content": full_response}
            )

        except Exception as e:
            # Gemini API 관련 오류 처리
            st.error(f"❌ 오류가 발생했습니다: {e}")
            # 예: "400 The model `gemini-1.0-pro` does not support system instructions."
            # 위와 같은 오류 발생 시, system_instruction을 지원하는 모델(예: 1.5 pro)을 사용해야 합니다.
