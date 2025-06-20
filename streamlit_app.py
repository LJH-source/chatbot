import streamlit as st
from openai import OpenAI
import requests
from PIL import Image
from io import BytesIO
import base64

# ------------------------------------------------------------
# Utility – Get helicopter image from Unsplash API or use default
# ------------------------------------------------------------
@st.cache_data(show_spinner=False)
def get_helicopter_image():
    """Get a helicopter image from various sources."""
    # 여러 헬리콥터 이미지 URL 목록 (확실한 헬리콥터 이미지들)
    helicopter_urls = [
        "https://images.unsplash.com/photo-1544717302-de2939b7ef71?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&h=300&q=80",
        "https://images.unsplash.com/photo-1578662996442-48f60103fc96?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&h=300&q=80",
        "https://images.unsplash.com/photo-1562813733-b31f71025d54?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&h=300&q=80",
        "https://images.unsplash.com/photo-1570710891163-6d3b5c47248b?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&h=300&q=80"
    ]
    
    # 각 URL을 시도해서 작동하는 첫 번째 이미지 사용
    for url in helicopter_urls:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                # 이미지가 실제로 로드되는지 확인
                img = Image.open(BytesIO(response.content))
                # 크기 조정
                img = img.resize((400, 300), Image.Resampling.LANCZOS)
                
                # Base64로 인코딩
                buffered = BytesIO()
                img.save(buffered, format="JPEG", quality=85)
                img_base64 = base64.b64encode(buffered.getvalue()).decode()
                
                return f"data:image/jpeg;base64,{img_base64}"
        except Exception:
            continue
    
    # 모든 URL이 실패하면 직접 헬리콥터 이미지 URL 반환
    return "https://images.unsplash.com/photo-1544717302-de2939b7ef71?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&h=300&q=80"

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
        .helicopter-container {
            text-align: center;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 15px;
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
            margin-bottom: 20px;
        }
        .helicopter-image {
            border-radius: 10px;
            box-shadow: 0 4px 15px 0 rgba(0, 0, 0, 0.3);
            max-width: 100%;
            height: auto;
        }
        .helicopter-caption {
            color: white;
            font-size: 14px;
            margin-top: 10px;
            font-weight: 500;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# ------------------------------------------------------------
# Sidebar – API key & 도움말 & 이미지 업로드
# ------------------------------------------------------------
with st.sidebar:
    st.header("🔑 API Key 설정")
    openai_api_key = st.text_input("OpenAI API Key", type="password")
    
    st.divider()
    
    st.header("🚁 헬리콥터 이미지")
    uploaded_file = st.file_uploader(
        "헬리콥터 이미지를 업로드하세요 (선택사항)", 
        type=['png', 'jpg', 'jpeg'],
        help="업로드하지 않으면 기본 이미지를 사용합니다."
    )
    
    st.divider()
    
    st.markdown("### 사용 예시 질문")
    st.markdown("""
    - 양력과 항력이 어떻게 균형잡히나요?
    - 헬리콥터 로터 피치 변경으로 상승 원리 설명해 줘
    - 테일로터가 필요한 이유는?
    - 오토로테이션이란 무엇인가요?
    - 고정익과 회전익의 차이점은?
    """)

# ------------------------------------------------------------
# 이미지 처리
# ------------------------------------------------------------
if uploaded_file is not None:
    # 업로드된 이미지 사용
    image = Image.open(uploaded_file)
    image = image.resize((400, 300), Image.Resampling.LANCZOS)
    
    buffered = BytesIO()
    image.save(buffered, format="JPEG", quality=85)
    img_base64 = base64.b64encode(buffered.getvalue()).decode()
    helicopter_img_src = f"data:image/jpeg;base64,{img_base64}"
    img_caption = "업로드된 헬리콥터 이미지"
else:
    # 기본 이미지 사용
    helicopter_img_src = get_helicopter_image()
    img_caption = "헬리콥터 - 회전익 항공기"

# ------------------------------------------------------------
# 초기 화면(키 미입력) – 헬리콥터 이미지 표시
# ------------------------------------------------------------
if not openai_api_key:
    st.markdown(
        f"""
        <div class="helicopter-container">
            <img src="{helicopter_img_src}" class="helicopter-image" alt="Helicopter Image">
            <div class="helicopter-caption">{img_caption}</div>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.info("🔑 사이드바에 OpenAI API 키를 입력하면 챗봇을 사용할 수 있습니다.")
    st.markdown("### 🚁 항공 원리 챗봇에 오신 것을 환영합니다!")
    st.markdown("""
    이 챗봇은 다음과 같은 항공 관련 질문에 전문적으로 답변해드립니다:
    
    **고정익 항공기 (비행기)**
    - 양력, 항력, 추력, 중량의 4가지 힘
    - 베르누이 법칙과 뉴턴의 법칙
    - 날개 설계와 에어포일
    
    **회전익 항공기 (헬리콥터)**
    - 로터 시스템과 피치 제어
    - 사이클릭과 컬렉티브 조작
    - 토크 보상과 테일로터
    - 오토로테이션 원리
    """)
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
    st.markdown(
        f"""
        <div class="helicopter-container">
            <img src="{helicopter_img_src}" class="helicopter-image" alt="Helicopter Image">
            <div class="helicopter-caption">{img_caption}</div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # 추가 정보 카드
    st.markdown("""
    ### 📚 항공 지식 가이드
    
    **🔄 회전익 원리**
    - 로터 블레이드의 회전으로 양력 생성
    - 피치 각도 조절로 상승/하강 제어
    
    **✈️ 고정익 원리** 
    - 전진 속도와 날개 형상으로 양력 생성
    - 조종면으로 자세 제어
    
    **⚖️ 비행 역학**
    - 4가지 기본 힘의 균형
    - 안정성과 조종성의 상호관계
    """)

with col_chat:
    st.title("💬 Aviation Principles Chatbot")
    st.markdown(
        "🛩️ **고정익·회전익 항공기의 비행 원리 전문 챗봇**입니다. "
        "항공역학, 비행원리, 항공기 시스템에 대해 질문해보세요!"
    )

    # --------------------------------------------------------
    # Session‑state chat history (system prompt 포함)
    # --------------------------------------------------------
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "system",
                "content": (
                    "You are an experienced aviation engineer and flight instructor with expertise in both fixed-wing and rotary-wing aircraft. "
                    "Provide detailed explanations about aerodynamics, flight principles, aircraft systems, and aviation physics. "
                    "Include relevant equations, diagrams descriptions, and practical examples when helpful. "
                    "Cover topics like lift generation, drag forces, propulsion systems, flight controls, stability, "
                    "helicopter rotor dynamics, autorotation, torque effects, and flight safety principles. "
                    "Always respond in Korean when the user writes in Korean, and use clear, educational language suitable for both beginners and advanced learners."
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
    if prompt := st.chat_input("✍️ 궁금한 비행 원리를 입력하세요... (예: 헬리콥터가 어떻게 날아요?)"):

        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        try:
            with st.chat_message("assistant"):
                with st.spinner("항공 전문가가 답변을 준비하고 있습니다..."):
                    stream = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=st.session_state.messages,
                        temperature=0.7,
                        top_p=0.9,
                        stream=True,
                    )
                    response_text = st.write_stream(stream)

            st.session_state.messages.append({"role": "assistant", "content": response_text})
            
        except Exception as e:
            st.error(f"🚨 오류가 발생했습니다: {e}")
            st.info("API 키가 올바른지 확인하고 다시 시도해주세요.")

# ------------------------------------------------------------
# Footer
# ------------------------------------------------------------
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; font-size: 12px;'>
        ✈️ Aviation Principles Chatbot | Powered by OpenAI GPT-4o-mini | 🚁 항공역학 전문 상담
    </div>
    """,
    unsafe_allow_html=True
)
