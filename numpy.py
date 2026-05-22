import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ── 페이지 설정 ──────────────────────────────────────────────
st.set_page_config(
    page_title="반도체 수율 대시보드",
    page_icon="🔬",
    layout="wide",
)

# ── 커스텀 CSS ──────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans+KR:wght@300;400;600&display=swap');

  html, body, [class*="css"] { font-family: 'IBM Plex Sans KR', sans-serif; }

  .stApp { background: #050D1A; color: #E0EAF4; }

  h1, h2, h3 { font-family: 'IBM Plex Mono', monospace !important; color: #00B4FF !important; }

  .metric-card {
    background: #0A1628;
    border: 1px solid #1A3A5C;
    border-left: 4px solid #00B4FF;
    border-radius: 8px;
    padding: 1rem 1.25rem;
    margin-bottom: 0.5rem;
  }
  .metric-label { font-size: 12px; color: #A8C0D6; letter-spacing: .06em; text-transform: uppercase; }
  .metric-value { font-family: 'IBM Plex Mono', monospace; font-size: 28px; font-weight: 600; color: #00B4FF; }
  .metric-value.warn { color: #FF6B6B; }
  .metric-value.ok   { color: #00FFE5; }

  .alert-box {
    background: #1A0505;
    border: 1px solid #FF6B6B;
    border-left: 4px solid #FF6B6B;
    border-radius: 8px;
    padding: 0.75rem 1rem;
    margin: 0.5rem 0;
    color: #FF9999;
    font-size: 14px;
  }

  div[data-testid="stDataFrame"] { border: 1px solid #1A3A5C; border-radius: 8px; overflow: hidden; }

  section[data-testid="stSidebar"] {
    background: #0A1628 !important;
    border-right: 1px solid #1A3A5C;
  }
  section[data-testid="stSidebar"] label { color: #A8C0D6 !important; }

  .stSelectbox > div > div { background: #0A1628; border-color: #1A3A5C; color: #E0EAF4; }
  .stMultiSelect > div > div { background: #0A1628; border-color: #1A3A5C; }
</style>
""", unsafe_allow_html=True)


# ── 데이터 생성 / 로드 ──────────────────────────────────────
@st.cache_data
def load_data() -> pd.DataFrame:
    data = {
        'Date': [
            '2024-12-01', '2024-12-01', '2024-12-02', '2024-12-02', '2024-12-03',
            '2024-12-03', '2024-12-04', '2024-12-04', '2024-12-05', '2024-12-05',
            '2024-12-06', '2024-12-06', '2024-12-07', '2024-12-07', '2024-12-08',
        ],
        'Equipment': [
            'EQP-A', 'EQP-B', 'EQP-A', 'EQP-B', 'EQP-A',
            'EQP-B', 'EQP-A', 'EQP-B', 'EQP-A', 'EQP-B',
            'EQP-A', 'EQP-B', 'EQP-A', 'EQP-B', 'EQP-A',
        ],
        'Lot_ID': [f'LOT-{i}' for i in range(1001, 1016)],
        'Yield_Rate': [
            98.5, 97.2, 98.1, 96.8, 99.0, 97.5, 98.3, 96.5,
            85.2, 82.1, 98.4, 97.0, 99.1, 97.8, 98.6,
        ],
    }
    df = pd.DataFrame(data)
    df['Date'] = pd.to_datetime(df['Date'])
    return df


df = load_data()

# ── 사이드바 필터 ──────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🔬 필터")
    st.markdown("---")

    selected_equip = st.multiselect(
        "장비 선택",
        options=df['Equipment'].unique().tolist(),
        default=df['Equipment'].unique().tolist(),
    )

    yield_threshold = st.slider(
        "수율 임계값 (%)",
        min_value=80.0, max_value=100.0, value=95.0, step=0.5,
    )

    st.markdown("---")
    st.markdown(
        "<span style='color:#A8C0D6;font-size:12px;'>임계값 미만 로트는 ⚠️ 이상으로 표시됩니다.</span>",
        unsafe_allow_html=True,
    )

# ── 데이터 필터링 ──────────────────────────────────────────
df_filtered = df[df['Equipment'].isin(selected_equip)].copy()
df_filtered['Status'] = df_filtered['Yield_Rate'].apply(
    lambda x: '⚠️ 이상' if x < yield_threshold else '✅ 정상'
)

# ── 헤더 ──────────────────────────────────────────────────
st.markdown("# 🔬 반도체 수율 모니터링 대시보드")
st.markdown(
    "<p style='color:#A8C0D6;margin-top:-0.5rem;'>Semiconductor Yield Rate Analysis · 2024-12</p>",
    unsafe_allow_html=True,
)
st.markdown("---")

# ── KPI 카드 ──────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)

avg_yield   = df_filtered['Yield_Rate'].mean()
min_yield   = df_filtered['Yield_Rate'].min()
anomaly_cnt = (df_filtered['Yield_Rate'] < yield_threshold).sum()
total_lots  = len(df_filtered)

with col1:
    cls = "ok" if avg_yield >= yield_threshold else "warn"
    st.markdown(f"""
    <div class="metric-card">
      <div class="metric-label">평균 수율</div>
      <div class="metric-value {cls}">{avg_yield:.1f}%</div>
    </div>""", unsafe_allow_html=True)

with col2:
    cls = "ok" if min_yield >= yield_threshold else "warn"
    st.markdown(f"""
    <div class="metric-card">
      <div class="metric-label">최저 수율</div>
      <div class="metric-value {cls}">{min_yield:.1f}%</div>
    </div>""", unsafe_allow_html=True)

with col3:
    cls = "warn" if anomaly_cnt > 0 else "ok"
    st.markdown(f"""
    <div class="metric-card">
      <div class="metric-label">이상 로트 수</div>
      <div class="metric-value {cls}">{anomaly_cnt}건</div>
    </div>""", unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card">
      <div class="metric-label">총 로트 수</div>
      <div class="metric-value">{total_lots}개</div>
    </div>""", unsafe_allow_html=True)

# ── 이상 감지 알림 ──────────────────────────────────────────
anomalies = df_filtered[df_filtered['Yield_Rate'] < yield_threshold]
if not anomalies.empty:
    for _, row in anomalies.iterrows():
        st.markdown(
            f"<div class='alert-box'>⚠️ <b>{row['Lot_ID']}</b> | {row['Equipment']} | "
            f"{row['Date'].strftime('%Y-%m-%d')} | 수율 <b>{row['Yield_Rate']}%</b> "
            f"(임계값 {yield_threshold}% 미만)</div>",
            unsafe_allow_html=True,
        )

st.markdown("")

# ── 차트 ──────────────────────────────────────────────────
chart_col1, chart_col2 = st.columns([2, 1])

with chart_col1:
    st.markdown("### 📈 일자별 수율 추이")

    fig_line = go.Figure()

    colors = {'EQP-A': '#00B4FF', 'EQP-B': '#00FFE5'}
    for eqp in df_filtered['Equipment'].unique():
        df_eqp = df_filtered[df_filtered['Equipment'] == eqp].sort_values('Date')
        fig_line.add_trace(go.Scatter(
            x=df_eqp['Date'], y=df_eqp['Yield_Rate'],
            mode='lines+markers',
            name=eqp,
            line=dict(color=colors.get(eqp, '#9B59FF'), width=2.5),
            marker=dict(size=8, symbol='circle'),
            hovertemplate='%{x|%m/%d}<br>수율: %{y:.1f}%<extra>' + eqp + '</extra>',
        ))

    # 임계값 라인
    fig_line.add_hline(
        y=yield_threshold,
        line_dash="dash",
        line_color="#FF6B6B",
        annotation_text=f"임계값 {yield_threshold}%",
        annotation_font_color="#FF6B6B",
        annotation_position="bottom right",
    )

    fig_line.update_layout(
        paper_bgcolor='#0A1628', plot_bgcolor='#050D1A',
        font=dict(color='#A8C0D6', family='IBM Plex Mono'),
        legend=dict(bgcolor='#0A1628', bordercolor='#1A3A5C'),
        xaxis=dict(gridcolor='#0D2137', tickformat='%m/%d'),
        yaxis=dict(gridcolor='#0D2137', range=[78, 101]),
        margin=dict(l=10, r=10, t=10, b=10),
        height=320,
    )
    st.plotly_chart(fig_line, use_container_width=True)

with chart_col2:
    st.markdown("### 🏭 장비별 평균 수율")

    equip_avg = df_filtered.groupby('Equipment')['Yield_Rate'].mean().reset_index()

    fig_bar = go.Figure(go.Bar(
        x=equip_avg['Equipment'],
        y=equip_avg['Yield_Rate'],
        marker=dict(
            color=equip_avg['Yield_Rate'],
            colorscale=[[0, '#FF6B6B'], [0.5, '#FFD700'], [1, '#00FFE5']],
            cmin=80, cmax=100,
            showscale=False,
        ),
        text=equip_avg['Yield_Rate'].map('{:.1f}%'.format),
        textposition='outside',
        textfont=dict(color='#E0EAF4', family='IBM Plex Mono', size=13),
    ))
    fig_bar.update_layout(
        paper_bgcolor='#0A1628', plot_bgcolor='#050D1A',
        font=dict(color='#A8C0D6', family='IBM Plex Mono'),
        xaxis=dict(gridcolor='#0D2137'),
        yaxis=dict(gridcolor='#0D2137', range=[78, 102]),
        margin=dict(l=10, r=10, t=10, b=10),
        height=320,
    )
    st.plotly_chart(fig_bar, use_container_width=True)

# ── 데이터 테이블 ──────────────────────────────────────────
st.markdown("### 📋 로트 상세 데이터")

df_display = df_filtered[['Date', 'Lot_ID', 'Equipment', 'Yield_Rate', 'Status']].copy()
df_display['Date'] = df_display['Date'].dt.strftime('%Y-%m-%d')
df_display = df_display.rename(columns={
    'Date': '날짜', 'Lot_ID': '로트 ID',
    'Equipment': '장비', 'Yield_Rate': '수율 (%)', 'Status': '상태',
})

st.dataframe(
    df_display.style.applymap(
        lambda v: 'color: #FF6B6B; font-weight: bold;' if '이상' in str(v) else '',
        subset=['상태']
    ).applymap(
        lambda v: 'color: #FF6B6B;' if isinstance(v, float) and v < yield_threshold else '',
        subset=['수율 (%)']
    ),
    use_container_width=True,
    hide_index=True,
)

# ── CSV 다운로드 ──────────────────────────────────────────
st.markdown("")
csv = df_filtered.drop(columns=['Status']).to_csv(index=False).encode('utf-8-sig')
st.download_button(
    label="⬇️ 필터링된 데이터 CSV 다운로드",
    data=csv,
    file_name='semiconductor_filtered.csv',
    mime='text/csv',
)

st.markdown(
    "<p style='text-align:center;color:#1A3A5C;font-size:11px;margin-top:2rem;'>"
    "Semiconductor Yield Dashboard · Built with Streamlit</p>",
    unsafe_allow_html=True,
)
