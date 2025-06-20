import streamlit as st
from openai import OpenAI

# ------------------------------------------------------------
# Page configuration & header
# ------------------------------------------------------------
st.set_page_config(page_title="🛩️ Aviation Principles Chatbot", page_icon="✈️", layout="centered")

st.title("💬 Aviation Principles Chatbot")

st.markdown(
    """
이 챗봇은 항공기(특히 고정익·회전익)의 **비행 원리**와 **항공역학**에 대한 전문 답변을 제공합니다.  
OpenAI GPT‑4o 모델을 사용하며, 질문은 한국어·영어 모두 가능합니다.
"""
)

# ------------------------------------------------------------
# Sidebar – API key & helper image
# ------------------------------------------------------------
with st.sidebar:
    st.image(
        "https://images.unsplash.com/photo-1516569420820-527ea139c2b7?auto=format&fit=crop&w=600&q=60",
        caption="Bell 412 helicopter • © Alex Loup – Unsplash",
        use_column_width=True,
    )
    st.markdown("### 사용 방법")
    st.markdown("""
- 좌측 입력란에 **OpenAI API 키**를 입력하세요.  
- 예시 질문:  
  • `양력과 항력은 어떻게 균형잡히나요?`  
  • `헬리콥터 로터는 왜 피치 변경으로 상승하나요?`
""")

openai_api_key = st.sidebar.text_input("🔑 OpenAI API Key", type="password")
if not openai_api_key:
    st.info("API 키를 입력하면 대화를 시작할 수 있습니다.", icon="🗝️")
    st.stop()

# ------------------------------------------------------------
# OpenAI client
# ------------------------------------------------------------
client = OpenAI(api_key=openai_api_key)

# ------------------------------------------------------------
# Session‑state chat history (include system prompt for domain focus)
# ------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system",
            "content": (
                "You are an aviation engineer and flight‑science instructor. "
                "Explain concepts of aerodynamics, lift, drag, thrust, stability, helicopter rotor dynamics, "
                "and other flight principles with clear examples and equations when helpful. "
                "Keep answers concise but thorough, and switch to Korean when the user writes in Korean."
            ),
        }
    ]

# ------------------------------------------------------------
# Render existing messages (excluding hidden system message)
# ------------------------------------------------------------
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# ------------------------------------------------------------
# User input field
# ------------------------------------------------------------
if prompt := st.chat_input("✍️ 궁금한 비행 원리를 입력하세요..."):

    # Store & echo the user prompt
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Request streaming completion from OpenAI
    try:
        stream = client.chat.completions.create(
            model="gpt-4o",
            messages=st.session_state.messages,
            temperature=0.7,
            top_p=0.9,
            stream=True,
        )

        # Display assistant response as it streams
        with st.chat_message("assistant"):
            response_content = st.write_stream(stream)

        # Save assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response_content})
    except Exception as e:
        st.error(f"🚨 Error: {e}")
