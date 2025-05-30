# -*- coding: utf-8 -*-
"""connAI.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/12yUZCSu484ybqurPEXaUC8CPxmRYT0IP
"""

import streamlit as st
import openai

st.title("교사 계획서 AI 피드백")

# OpenAI API 키 입력
openai_api_key = st.text_input("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", type="password")

# 사용자 입력 받기
user_input = st.text_area("✏️ 계획서 내용을 입력하세요")

if st.button("AI 피드백 받기"):
    if not openai_api_key:
        st.warning("API 키를 입력해주세요.")
    elif not user_input.strip():
        st.warning("계획서 내용을 입력해주세요.")
    else:
        with st.spinner("AI가 피드백을 생성 중입니다..."):
            # OpenAI API 호출
            openai.api_key = openai_api_key
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "당신은 교육계에서 일하는 전문가이며, 교사의 수업 계획서에 대해 친절하고 구체적인 피드백을 제공합니다."},
                    {"role": "user", "content": user_input}
                ]
            )
            feedback = response['choices'][0]['message']['content']
            st.success("✅ 피드백 생성 완료!")
            st.markdown("### 🧠 AI 피드백")
            st.write(feedback)