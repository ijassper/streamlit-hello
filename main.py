import streamlit as st
import requests

# 1. 환율 가져오기 함수
def get_exchange_rate(base, target):
    if base == target:
        return 1.0
    url = f"https://open.er-api.com/v6/latest/{base}"
    try:
        response = requests.get(url)
        data = response.json()
        return data['rates'].get(target, None)
    except:
        return None

st.title("💱 완벽한 구글 스타일 환율 계산기")
st.write("💡 위, 아래 아무 곳이나 숫자를 입력해 보세요!")

currency_list = ["KRW", "USD", "EUR", "JPY", "CNY", "GBP", "AUD"]

# ==========================================
# 🧠 마법의 시작: 상태 유지와 알람(콜백) 설정
# ==========================================

# 1. 앱이 처음 켜졌을 때 딱 한 번만 실행되는 초기 세팅
if "initialized" not in st.session_state:
    st.session_state.top_amount = 1000.0 # 위쪽 초기 금액 1000원
    
    # 처음 켜졌을 때 원화->달러 환율을 가져와서 아래쪽 금액을 미리 계산해 둡니다.
    initial_rate = get_exchange_rate("KRW", "USD")
    st.session_state.bottom_amount = 1000.0 * (initial_rate if initial_rate else 0)
    
    st.session_state.initialized = True # 초기화 완료 도장 쾅!

# 2. 알람 함수 A: [위쪽 숫자]를 건드렸을 때 작동
def update_bottom():
    # 사용자가 입력한 위쪽 금액과 통화들을 가져옵니다.
    top_val = st.session_state.top_input
    top_curr = st.session_state.top_curr
    bot_curr = st.session_state.bot_curr
    
    # 환율을 가져와서 아래쪽 금액을 계산해 '메모장'에 덮어씁니다.
    rate = get_exchange_rate(top_curr, bot_curr)
    if rate:
        st.session_state.bottom_amount = top_val * rate

# 3. 알람 함수 B:[아래쪽 숫자]를 건드렸을 때 작동
def update_top():
    bot_val = st.session_state.bottom_input
    top_curr = st.session_state.top_curr
    bot_curr = st.session_state.bot_curr
    
    # 주의! 아래쪽에서 위쪽으로 가는 거니까 기준 통화가 반대입니다.
    rate = get_exchange_rate(bot_curr, top_curr) 
    if rate:
        st.session_state.top_amount = bot_val * rate

# 4. 알람 함수 C: [통화(달러, 원화 등)]를 바꿨을 때 작동
def update_currency():
    # 통화가 바뀌면 위쪽 금액을 기준으로 아래쪽 금액을 싹 다시 계산합니다.
    top_val = st.session_state.top_amount
    top_curr = st.session_state.top_curr
    bot_curr = st.session_state.bot_curr
    
    rate = get_exchange_rate(top_curr, bot_curr)
    if rate:
        st.session_state.bottom_amount = top_val * rate


# ==========================================
# 🖥️ 웹페이지 화면 구성 (UI)
# ==========================================

# --- [첫 번째 줄: 위쪽] ---
col1, col2 = st.columns([2, 1])
with col1:
    # on_change=update_bottom : "이 칸의 숫자가 바뀌면 update_bottom 함수를 실행해!" 라는 뜻입니다.
    st.number_input("위쪽 금액", key="top_input", value=st.session_state.top_amount, on_change=update_bottom, label_visibility="collapsed")
with col2:
    st.selectbox("위쪽 통화", currency_list, index=0, key="top_curr", on_change=update_currency, label_visibility="collapsed")

# --- [두 번째 줄: 아래쪽] ---
col3, col4 = st.columns([2, 1])
with col3:
    # 이전 코드와 달리 disabled=True (잠금)를 풀었습니다! 이제 아래쪽도 입력 가능합니다.
    st.number_input("아래쪽 금액", key="bottom_input", value=st.session_state.bottom_amount, on_change=update_top, label_visibility="collapsed")
with col4:
    st.selectbox("아래쪽 통화", currency_list, index=1, key="bot_curr", on_change=update_currency, label_visibility="collapsed")

# --- [현재 환율 요약 텍스트] ---
current_rate = get_exchange_rate(st.session_state.top_curr, st.session_state.bot_curr)
if current_rate:
    st.markdown(f"<p style='text-align: right; color: gray;'>1 {st.session_state.top_curr} = {current_rate:,.5f} {st.session_state.bot_curr}</p>", unsafe_allow_html=True)
