import streamlit as st
import pandas as pd

# 제목 표시
st.title("교사 계획서 자동 검토 웹앱")

# 예시 데이터프레임 생성
df = pd.DataFrame({
    "이름": ["홍길동", "김철수"],
    "점수": [85, 90]
})

# 데이터프레임 표시
st.subheader("점수표 미리보기")
st.dataframe(df)

# CSV로 변환
csv = df.to_csv(index=False).encode('utf-8-sig')

# 다운로드 버튼 제공
st.download_button(
    label="CSV 파일 다운로드",
    data=csv,
    file_name='result.csv',
    mime='text/csv'
)
