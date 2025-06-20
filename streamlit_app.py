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

st.markdown(
    """
    <style>
        .main {background-color: #f0f4f8;}
        .block-container {padding-top: 2rem; padding-bottom: 2rem;}
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
# 초기 화면(키 미입력) – 사용자 이미지 표시 가능 영역
# ------------------------------------------------------------
if not openai_api_key:
    st.info("사이드바에 OpenAI API 키를 입력하면 챗봇을 사용할 수 있습니다.")

    # ✅ 여기에 사용자가 직접 넣은 이미지를 표시합니다.
    # 프로젝트 폴더에 'helicopter.jpg' 파일이 있어야 합니다.
    try:
        st.image("helicopter.png", caption="🚁 헬리콥터 원리의 이해", use_column_width=True)
    except FileNotFoundError:
        st.warning("⚠️ 'helicopter.png' 파일이 프로젝트 폴더에 없습니다. 이미지를 확인해 주세요.")

    st.stop()

# ------------------------------------------------------------
# OpenAI client
# ------------------------------------------------------------
client = OpenAI(api_key=openai_api_key)

# ------------------------------------------------------------
# 컬럼 레이아웃: 왼쪽 이미지, 오른쪽 챗
# ------------------------------------------------------------
col_img, col_chat = st.columns([1, 2])

with col_img:
    try:
        st.image("helicopter.png", caption="🚁 헬리콥터 로터 시스템", use_column_width=True)
    except FileNotFoundError:
        st.warning("⚠️ 이미지 파일을 찾을 수 없습니다.")

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

        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

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
