"""
Trang chủ cho ứng dụng demo phiên âm và phân đoạn audio.
"""

import logging
import streamlit as st

from sources.demo.utils.constants import APP_TITLE, APP_PAGE_TITLE, APP_FOOTER
from sources.demo.utils.cache_utils import render_cache_ui

# Thiết lập logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Thiết lập tiêu đề và thông tin trang
st.set_page_config(page_title=APP_PAGE_TITLE, layout="wide")

def main():
    """Hàm chính hiển thị trang homepage"""
    st.title(APP_TITLE)
    
    # Sidebar cho các tùy chọn
    st.sidebar.title("Menu")
    
    # Hiển thị thông tin cache
    render_cache_ui()
    
    # Hiển thị nội dung chính
    st.header("Xin chào và chào mừng đến với công cụ phiên âm!")
    
    # Giới thiệu
    st.markdown("""
    ## Giới thiệu
    
    Công cụ này cung cấp khả năng phiên âm và phân đoạn audio thành văn bản với độ chính xác cao, 
    sử dụng Google Gemini API. Hệ thống được thiết kế để hỗ trợ quá trình tạo dữ liệu có chất lượng 
    cho các hệ thống text-to-speech và speech-to-text.
    
    ## Tính năng chính
    
    - **Phiên âm chính xác** sử dụng các model AI tiên tiến
    - **Phân đoạn thông minh** giúp tách audio thành từng đoạn nhỏ theo câu
    - **Dễ dàng xuất kết quả** dưới nhiều định dạng (JSON, ZIP)
    - **Nghe thử từng đoạn** để kiểm tra chất lượng
    - **Tùy chỉnh linh hoạt** các thông số xử lý
    
    ## Bắt đầu sử dụng
    
    Để bắt đầu, hãy chuyển đến trang "Phiên âm và Phân đoạn" trong menu bên trái và tải lên file audio của bạn.
    
    ## Hướng dẫn sử dụng
    
    1. Tải lên file audio (định dạng WAV, MP3)
    2. Chọn chế độ xử lý phù hợp
    3. Điều chỉnh các thông số nếu cần
    4. Nhấn nút xử lý và đợi kết quả
    5. Xem và tải xuống kết quả
    """)
    
    # Hiển thị demo video hoặc hình ảnh minh họa (tùy chọn)
    st.subheader("Quy trình xử lý")
    
    # Hiển thị biểu đồ mermaid minh họa quy trình
    mermaid_code = """
    %%{init: {'theme': 'base', 'themeVariables': { 'primaryColor': '#5D8BF4', 'textColor': '#333', 'primaryBorderColor': '#5D8BF4'}}}%%
    flowchart LR
        A[Tải lên audio] --> B[Phiên âm với<br>Gemini AI]
        B --> C{Có phân đoạn<br>không?}
        C -->|Có| D[Phân tích ngữ cảnh]
        C -->|Không| F[Xuất text]
        D --> E[Căn chỉnh audio-text]
        E --> G[Cắt audio theo câu]
        G --> H[Xuất kết quả]
        F --> H
    """
    st.markdown(f"```mermaid\n{mermaid_code}\n```")
    
    # Thông tin về API và yêu cầu
    with st.expander("Yêu cầu hệ thống"):
        st.markdown("""
        - Python 3.8 trở lên
        - 4GB RAM trở lên
        - Kết nối internet để sử dụng Google Gemini API
        - API key của Google Gemini (cài đặt trong file `sources/core/api_key.py`)
        """)
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.info(APP_FOOTER)

if __name__ == "__main__":
    main()
