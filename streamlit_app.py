import streamlit as st
from openai import OpenAI

# ------------------------------------------------------------
# Page configuration & global style
# ------------------------------------------------------------
st.set_page_config(
    page_title="✈️ Aviation Principles Chatbot",
    page_icon="🛩️",
    layout="wide",
)

# 기본 CSS 살짝 조정 (배경색, 본문 폭 등)
st.markdown(
    """
    <style>
        .main {
            background-color: #f0f4f8;
        }
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        footer {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True,
)

# ------------------------------------------------------------
# Sidebar – API key & 도움말
# ------------------------------------------------------------
with st.sidebar:
    st.header("🔑 API Key 설정")
    openai_api_key = st.text_input("OpenAI API Key", type="password")
    st.divider()
    st.markdown("### 사용 예시 질문")
    st.markdown("- 양력과 항력이 어떻게 균형잡히나요?\n- 헬리콥터 로터 피치 변경으로 상승 원리 설명해 줘\n- 테일로터가 필요한 이유는?")

# ------------------------------------------------------------
# 초기 화면(키 미입력) – 헬기 이미지 표시
# ------------------------------------------------------------
if not openai_api_key:
    st.info("사이드바에 OpenAI API 키를 입력하면 챗봇을 사용할 수 있습니다.")
    st.image(
        "https://upload.wikimedia.org/wikipedia/commons/7/7e/Apache_helicopter_flying.jpg",
        caption="AH‑64 Apache • © U.S. Army (Wikimedia Commons)",
        use_column_width=True,
    )
    st.stop()

# ------------------------------------------------------------
# OpenAI client
# ------------------------------------------------------------
client = OpenAI(api_key=openai_api_key)

# ------------------------------------------------------------
# 컬럼 레이아웃: 왼쪽 그림, 오른쪽 챗
# ------------------------------------------------------------
col_img, col_chat = st.columns([1, 2])

with col_img:
    st.image(
        "https://upload.wikimedia.org/wikipedia/commons/7/7e/Apache_helicopter_flying.jpg",
        caption="AH‑64 Apache • © U.S. Army (Wikimedia Commons)",
        use_column_width=True,
    )

with col_chat:
    st.title("💬 Aviation Principles Chatbot")
    st.markdown(
        "이 챗봇은 고정익·회전익 항공기의 비행 원리에 대해 전문적인 답변을 제공합니다. 질문을 입력해 보세요!"
    )

    # --------------------------------------------------------
    # Session‑state chat history (system prompt 포함)
    # --------------------------------------------------------
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "system",
                "content": (
                    "You are an aviation engineer and flight‑science instructor. "
                    "Explain aerodynamics, lift, drag, thrust, stability, helicopter rotor dynamics, "
                    "and related flight principles clearly, using equations and practical examples when useful. "
                    "Use Korean if the user writes in Korean."
                ),
            }
        ]

    # 기존 메시지 표시 (system 제외)
    for msg in st.session_state.messages:
        if msg["role"] != "system":
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    # --------------------------------------------------------
    # User input
    # --------------------------------------------------------
    if prompt := st.chat_input("✍️ 궁금한 비행 원리를 입력하세요..."):

        # 저장 & 화면 표시
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # OpenAI 스트리밍 응답
        try:
            stream = client.chat.completions.create(
                model="gpt-4o",
                messages=st.session_state.messages,
                temperature=0.7,
                top_p=0.9,
                stream=True,
            )

            with st.chat_message("assistant"):
                response_text = st.write_stream(stream)

            st.session_state.messages.append({"role": "assistant", "content": response_text})
        except Exception as e:
            st.error(f"🚨 Error: {e}")
