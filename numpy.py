import streamlet as st
import pandas as pd
import random

# 1. 가짜 데이터 생성 (딕셔너리 형태)
data = {
    'Date': ['2024-12-01', '2024-12-01', '2024-12-02', '2024-12-02', '2024-12-03',
             '2024-12-03', '2024-12-04', '2024-12-04', '2024-12-05', '2024-12-05',
             '2024-12-06', '2024-12-06', '2024-12-07', '2024-12-07', '2024-12-08'],
    'Equipment': ['EQP-A', 'EQP-B', 'EQP-A', 'EQP-B', 'EQP-A',
                  'EQP-B', 'EQP-A', 'EQP-B', 'EQP-A', 'EQP-B',
                  'EQP-A', 'EQP-B', 'EQP-A', 'EQP-B', 'EQP-A'],
    'Lot_ID': [f'LOT-{i}' for i in range(1001, 1016)],
    'Yield_Rate': [98.5, 97.2, 98.1, 96.8, 99.0, 97.5, 98.3, 96.5,
                   85.2, 82.1, 98.4, 97.0, 99.1, 97.8, 98.6] # 12월 5일에 수율 급락
}

# 2. 데이터프레임 만들기
# df = pd.read_csv('semiconductor_data.csv') # 저장된 파일 읽기용 (이 부분은 주석처리)
df_mock = pd.DataFrame(data)

# 3. CSV 파일로 저장 (코랩 왼쪽에 파일이 생깁니다)
df_mock.to_csv('semiconductor_data.csv', index=False)

st.wirte("✅ 테스트용 반도체 데이터 파일 생성 완료!")
print(df_mock)
