import streamlit as st
from openai import OpenAI
from io import BytesIO
import base64

# ------------------------------------------------------------
# Utility – load and encode helicopter image
# ------------------------------------------------------------
@st.cache_resource(show_spinner=False)
def load_helicopter_image(uploaded_file=None, default_image_url=None):
    """Return base64-encoded image data for a helicopter image."""
    if uploaded_file is not None:
        # User-uploaded image
        img_data = uploaded_file.read()
    else:
        # Fallback to a default image (you can replace with a URL or local file path)
        # For this example, assume a placeholder Base64 string or fetch from URL
        # Replace this with actual Base64 string or URL fetching logic
        # Example: Use a placeholder or fetch from a URL (not implemented here)
        st.warning("No image uploaded. Using placeholder image.")
        # Placeholder Base64 for a simple image (replace with actual helicopter image Base64)
        img_data = None  # Replace with actual Base64 string or fetch logic
        if default_image_url:
            import requests
            response = requests.get(default_image_url)
            img_data = response.content

    if img_data:
        img_b64 = base64.b64encode(img_data).decode()
        return img_b64
    return None

# Default helicopter image URL (optional, replace with a valid URL)
DEFAULT_IMAGE_URL = "https://example.com/helicopter.jpg"  # Replace with actual URL
IMG_DATA = load_helicopter_image(default_image_url=DEFAULT_IMAGE_URL)
IMG_TAG = f'<img src="data:image/jpeg;base64,{IMG_DATA}" width="100%">' if IMG_DATA else '<p>No image available</p>'

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
# Sidebar – API key & Image uploader & Help
# ------------------------------------------------------------
with st.sidebar:
    st.header("🔑 API Key 설정")
    openai_api_key = st.text_input("OpenAI API Key", type="password")
    st.divider()
    st.header("🖼️ 헬리콥터 이미지 업로드")
    uploaded_file = st.file_uploader("헬리콥터 이미지를 업로드하세요 (JPG/PNG)", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        IMG_DATA = load_helicopter_image(uploaded_file)
        IMG_TAG = f'<img src="data:image/jpeg;base64,{IMG_DATA}" width="100%">' if IMG_DATA else '<p>No image available</p>'
    st.divider()
    st.markdown("### 사용 예시 질문")
    st.markdown("- 양력과 항력이 어떻게 균형잡히나요?\n- 헬리콥터 로터 피치 변경으로 상승 원리 설명해 줘\n- 테일로터가 필요한 이유는?")

# ------------------------------------------------------------
# 초기 화면(키 미입력) – 헬리콥터 이미지 표시
# ------------------------------------------------------------
if not openai_api_key:
    st.info("사이드바에 OpenAI API 키를 입력하면 챗봇을 사용할 수 있습니다.")
    st.markdown(IMG_TAG, unsafe_allow_html=True)
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
    st.markdown(IMG_TAG, unsafe_allow_html=True)

with col_chat:
    st.title("💬 Aviation Principles Chatbot")
    st.markdown(
        "이 챗봇은 고정익·회전익 항공기의 비행 원리에 대해 전문적인 답변을 제공합니다. 질문을 입력해 보세요!"
    )

    # --------------------------------------------------------
    # Session-state chat history (system prompt 포함)
    # --------------------------------------------------------
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "system",
                "content": (
                    "You are an aviation engineer and flight-science instructor. "
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
