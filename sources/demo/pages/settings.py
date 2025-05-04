"""
Trang cài đặt nâng cao cho ứng dụng demo.
"""
import streamlit as st
import os
from typing import Dict, Any

from sources.demo.utils.constants import (
    MODEL_OPTIONS,
    TAB_LABELS,
    BUTTON_SAVE_SETTINGS
)
from sources.demo.utils.cache_utils import get_current_settings, update_settings

def show_settings():
    """
    Hiển thị và quản lý các cài đặt nâng cao cho ứng dụng.
    
    Returns:
        Dict[str, Any]: Dictionary chứa các cài đặt người dùng
    """
    st.title("Cài đặt nâng cao")
    
    # Đọc các cài đặt hiện tại từ session state (nếu có)
    current_settings = get_current_settings()
    
    # Tab cài đặt
    tab1, tab2, tab3 = st.tabs(TAB_LABELS)
    
    with tab1:
        st.subheader("Cài đặt phiên âm")
        
        # Model AI sử dụng cho phiên âm
        current_model = current_settings.get("model", MODEL_OPTIONS[0])
        model_index = MODEL_OPTIONS.index(current_model) if current_model in MODEL_OPTIONS else 0
        model = st.selectbox(
            "Model AI",
            options=MODEL_OPTIONS,
            index=model_index,
            help="Model AI sử dụng để phiên âm audio"
        )
        
        # Số lần thử lại khi gặp lỗi rate limit
        max_retries = st.slider(
            "Số lần thử lại khi gặp lỗi",
            min_value=1,
            max_value=10,
            value=current_settings.get("max_retries", 3),
            help="Số lần thử lại tối đa khi gặp lỗi rate limit"
        )
    
    with tab2:
        st.subheader("Cài đặt căn chỉnh audio-text")
        
        # Khoảng im lặng thêm vào đầu mỗi đoạn audio
        leading_silence = st.slider(
            "Khoảng im lặng đầu (milliseconds)",
            min_value=0,
            max_value=1000,
            value=current_settings.get("leading_silence_ms", 100),
            step=10,
            help="Khoảng im lặng (milliseconds) thêm vào đầu mỗi đoạn audio"
        )
        
        # Khoảng im lặng thêm vào cuối mỗi đoạn audio
        trailing_silence = st.slider(
            "Khoảng im lặng cuối (milliseconds)",
            min_value=0,
            max_value=1000,
            value=current_settings.get("trailing_silence_ms", 100),
            step=10,
            help="Khoảng im lặng (milliseconds) thêm vào cuối mỗi đoạn audio"
        )
    
    with tab3:
        st.subheader("Cài đặt hệ thống")
        
        # Cache kết quả
        cache_results = st.toggle(
            "Lưu cache kết quả",
            value=current_settings.get("cache_results", True),
            help="Lưu cache kết quả để tránh xử lý lại các file audio đã xử lý trước đó"
        )
        
        st.info("Các tệp được xử lý sẽ không được lưu trên server. Để lưu kết quả, hãy sử dụng chức năng tải xuống sau khi xử lý.")
    
    # Lưu cài đặt vào session state khi người dùng nhấn nút lưu
    if st.button(BUTTON_SAVE_SETTINGS):
        settings = {
            "model": model,
            "max_retries": max_retries,
            "leading_silence_ms": leading_silence,
            "trailing_silence_ms": trailing_silence,
            "cache_results": cache_results
        }
        
        # Lưu vào session state sử dụng hàm update_settings
        update_settings(settings)
        
        st.success("Đã lưu cài đặt thành công! Cài đặt sẽ được áp dụng cho tất cả các trang.")
        
        return settings
    
    # Trả về cài đặt mới (hoặc giữ nguyên nếu người dùng chưa nhấn nút lưu)
    return current_settings


if __name__ == "__main__":
    # Chạy ứng dụng Streamlit
    show_settings()
