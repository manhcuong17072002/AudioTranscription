"""
Trang chủ cho ứng dụng demo phiên âm và phân đoạn audio.
"""

import logging
import streamlit as st
import plotly.graph_objects as go

from sources.demo.utils.constants import APP_TITLE, APP_PAGE_TITLE, APP_FOOTER
from sources.demo.utils.cache_utils import render_cache_ui

# Thiết lập logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Thiết lập tiêu đề và thông tin trang
st.set_page_config(page_title=APP_PAGE_TITLE, layout="wide")

def render_hero_section():
    """Hiển thị phần hero với gradient background"""
    with st.container():
        # Sử dụng container với màu nền gradient
        st.markdown(
            """
            <style>
            .hero-container {
                background: linear-gradient(to right, #5D8BF4, #9AC5F4);
                padding: 2rem;
                border-radius: 10px;
                color: white;
                text-align: center;
                margin-bottom: 2rem;
            }
            </style>
            """, 
            unsafe_allow_html=True
        )
        
        # Chỉ sử dụng HTML cho container, phần nội dung sử dụng Streamlit native
        st.markdown('<div class="hero-container">', unsafe_allow_html=True)
        st.title(APP_TITLE)
        st.markdown("### Giải pháp phiên âm và phân đoạn audio thành văn bản với độ chính xác cao")
        st.markdown("Công nghệ AI tiên tiến · Phân đoạn thông minh · Dễ dàng sử dụng")
        
        cols = st.columns([1, 2, 1])
        with cols[0]:
            # Thêm chuyển hướng đến trang phiên âm khi nhấn nút
            if st.button("Bắt đầu ngay ➡️", use_container_width=True):
                js = """
                <script>
                    window.parent.open('/labeling_page', '_self');
                </script>
                """
                st.components.v1.html(js, height=0)
        
        st.markdown('</div>', unsafe_allow_html=True)

def render_feature_cards():
    """Hiển thị các tính năng chính dưới dạng cards"""
    st.header("Tính năng chính")
    
    # Định nghĩa dữ liệu cho các card
    features_row1 = [
        {
            "icon": "🎯",
            "title": "Phiên âm chính xác", 
            "desc": "Sử dụng Google Gemini API để phiên âm audio với độ chính xác cao, hỗ trợ nhiều giọng nói và ngôn ngữ khác nhau."
        },
        {
            "icon": "✂️",
            "title": "Phân đoạn thông minh", 
            "desc": "Tự động phân tích và chia nhỏ audio thành các đoạn có ý nghĩa theo câu hoặc đoạn văn."
        },
        {
            "icon": "📦",
            "title": "Xuất kết quả linh hoạt", 
            "desc": "Dễ dàng xuất kết quả dưới nhiều định dạng: JSON, văn bản thuần túy hoặc ZIP chứa audio + text."
        }
    ]
    
    features_row2 = [
        {
            "icon": "🎧",
            "title": "Nghe thử từng đoạn", 
            "desc": "Xem và nghe từng đoạn audio đã phân tách để kiểm tra chất lượng phiên âm trực tiếp."
        },
        {
            "icon": "⚙️",
            "title": "Tùy chỉnh linh hoạt", 
            "desc": "Điều chỉnh các thông số phiên âm và phân đoạn theo nhu cầu cụ thể của dự án."
        },
        {
            "icon": "💾",
            "title": "Lưu trữ thông minh", 
            "desc": "Hệ thống cache giúp lưu trữ và tái sử dụng kết quả, tiết kiệm thời gian xử lý."
        }
    ]
    
    # Hiển thị hàng feature cards đầu tiên
    cols = st.columns(len(features_row1))
    for i, col in enumerate(cols):
        with col:
            with st.container():
                st.markdown(f"### {features_row1[i]['icon']} {features_row1[i]['title']}")
                st.write(features_row1[i]['desc'])
    
    # Hiển thị hàng feature cards thứ hai
    cols = st.columns(len(features_row2))
    for i, col in enumerate(cols):
        with col:
            with st.container():
                st.markdown(f"### {features_row2[i]['icon']} {features_row2[i]['title']}")
                st.write(features_row2[i]['desc'])

def render_metrics():
    """Hiển thị thông tin dưới dạng metrics"""
    st.header("Hiệu suất & Khả năng")
    
    col1, col2, col3 = st.columns(3)
    col1.metric(label="Độ chính xác", value="98%")  # Loại bỏ delta so sánh
    col2.metric(label="Thời gian xử lý", value="<30s")  # Loại bỏ delta so sánh
    col3.metric(label="Định dạng hỗ trợ", value="2", help="WAV và MP3")

def render_workflow_diagram():
    """Hiển thị biểu đồ workflow sử dụng Plotly"""
    st.subheader("Quy trình xử lý")
    
    # Tạo biểu đồ workflow với Plotly
    # Dữ liệu nodes và edges
    nodes = ["Tải lên Audio", "Phiên âm với<br>Gemini AI", "Phân đoạn?", 
             "Phân tích ngữ cảnh", "Căn chỉnh<br>audio-text", 
             "Cắt audio<br>theo câu", "Kết quả<br>phân đoạn", "Kết quả<br>text"]
    
    # Tạo diagram dạng Sankey
    fig = go.Figure(go.Sankey(
        arrangement = "snap",
        node = dict(
            pad = 20,
            thickness = 20,
            line = dict(color = "black", width = 0.5),
            label = nodes,
            color = ["#5D8BF4", "#5D8BF4", "#FF6B6B", "#5D8BF4", 
                     "#5D8BF4", "#5D8BF4", "#4CAF50", "#4CAF50"]
        ),
        link = dict(
            source = [0, 1, 2, 2, 3, 4, 5],
            target = [1, 2, 3, 7, 4, 5, 6],
            value = [10, 10, 7, 3, 7, 7, 7],
            color = ["rgba(93, 139, 244, 0.4)", "rgba(93, 139, 244, 0.4)", 
                    "rgba(93, 139, 244, 0.4)", "rgba(93, 139, 244, 0.4)", 
                    "rgba(93, 139, 244, 0.4)", "rgba(93, 139, 244, 0.4)", 
                    "rgba(93, 139, 244, 0.4)"]
        )
    ))
    
    fig.update_layout(
        title_text="Luồng xử lý dữ liệu audio", 
        font=dict(size=14),
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)

def render_usage_guide():
    """Hiển thị hướng dẫn sử dụng với biểu tượng"""
    st.header("Hướng dẫn sử dụng")
    
    # CSS cho step container
    st.markdown(
        """
        <style>
        .steps-container {
            background-color: #f1f3f9;
            border-radius: 10px;
            padding: 20px;
            margin: 10px 0;
        }
        </style>
        """, 
        unsafe_allow_html=True
    )
    
    # Định nghĩa các bước
    steps = [
        {"icon": "📁", "title": "Tải lên file audio", 
         "desc": "Hỗ trợ định dạng WAV, MP3"},
        {"icon": "⚙️", "title": "Chọn chế độ xử lý", 
         "desc": "Chỉ phiên âm hoặc phiên âm + phân đoạn"},
        {"icon": "🔧", "title": "Điều chỉnh thông số", 
         "desc": "Tùy chỉnh các thông số xử lý nếu cần"},
        {"icon": "▶️", "title": "Xử lý và đợi kết quả", 
         "desc": "Hệ thống sẽ xử lý audio và trả về văn bản"},
        {"icon": "💾", "title": "Xem và tải xuống", 
         "desc": "Xem kết quả và tải xuống theo định dạng mong muốn"}
    ]
        
    cols = st.columns(len(steps))
    for i, col in enumerate(cols):
        with col:
            st.subheader(f"{steps[i]['icon']} {i+1}")
            st.markdown(f"**{steps[i]['title']}**")
            st.caption(steps[i]['desc'])
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_introduction():
    """Hiển thị phần giới thiệu"""
    st.header("Giới thiệu")
    
    # CSS cho info section
    st.markdown(
        """
        <style>
        .info-section {
            border-left: 4px solid #5D8BF4;
            padding-left: 15px;
        }
        </style>
        """, 
        unsafe_allow_html=True
    )
    
    # Sử dụng columns để tạo bố cục tốt hơn
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('<div class="info-section">', unsafe_allow_html=True)
        st.markdown("""
        Công cụ này cung cấp khả năng phiên âm và phân đoạn audio thành văn bản với độ chính xác cao, 
        sử dụng Google Gemini API. Hệ thống được thiết kế để hỗ trợ quá trình tạo dữ liệu có chất lượng 
        cho các hệ thống text-to-speech và speech-to-text.
        
        Với giao diện thân thiện và các tùy chọn linh hoạt, công cụ này phù hợp cho cả người dùng 
        cá nhân và doanh nghiệp có nhu cầu phiên âm và phân đoạn audio chất lượng cao.
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        # Tạo card hiển thị lợi ích với Streamlit native
        with st.container():
            st.markdown("### Tại sao chọn chúng tôi?")
            st.markdown("""
            - ✅ Độ chính xác cao
            - ⚡ Xử lý nhanh chóng
            - 🔧 Tùy biến linh hoạt
            - 💼 Hỗ trợ các định dạng phổ biến
            """)

def main():
    """Hàm chính hiển thị trang homepage"""
    # Sidebar cho các tùy chọn
    st.sidebar.title("Menu")
    
    st.sidebar.markdown("""
    - [📄 Trang chủ](/)
    - [🎤 Phiên âm và phân đoạn](/labeling_page)
    - [👁️ Xem kết quả](/transcript_view)
    - [⚙️ Cài đặt](/settings)
    """)
        
    # Hiển thị thông tin cache
    render_cache_ui()
    
    # Hiển thị các thành phần UI
    render_hero_section()
    render_introduction()  # Di chuyển phần giới thiệu lên trên
    render_feature_cards()
    render_metrics()
    render_workflow_diagram()
    render_usage_guide()
        
    # Footer với inline style thay vì CSS class
    st.sidebar.markdown("---")
    st.sidebar.markdown(
        f"""
        <div style="
            background-color: #f8f9fa;
            padding: 1rem;
            border-radius: 0.5rem;
            border-left: 4px solid #5D8BF4;
            margin-top: 1rem;
            font-size: 0.9rem;
            color: #666;
        ">
            {APP_FOOTER}
        </div>
        """, 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
