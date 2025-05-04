"""
Các hàm tiện ích để quản lý cache.
"""

import hashlib
import time
from typing import Any, Dict

import streamlit as st

from sources.demo.utils.constants import (
    DEFAULT_MODEL, 
    DEFAULT_MAX_RETRIES,
    DEFAULT_LEADING_SILENCE_MS,
    DEFAULT_TRAILING_SILENCE_MS,
    DEFAULT_CACHE_RESULTS,
    BUTTON_CLEAR_CACHE
)

def get_current_settings() -> Dict[str, Any]:
    """
    Lấy cài đặt hiện tại từ session state hoặc trả về cài đặt mặc định.
    
    Returns:
        Dict[str, Any]: Dictionary chứa các cài đặt hiện tại
    """
    if "settings" not in st.session_state:
        st.session_state.settings = {
            "model": DEFAULT_MODEL,
            "max_retries": DEFAULT_MAX_RETRIES,
            "leading_silence_ms": DEFAULT_LEADING_SILENCE_MS,
            "trailing_silence_ms": DEFAULT_TRAILING_SILENCE_MS,
            "cache_results": DEFAULT_CACHE_RESULTS,
        }
    return st.session_state.settings

def update_settings(settings_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Cập nhật cài đặt vào session state.
    
    Args:
        settings_dict: Dictionary chứa các cài đặt cần cập nhật
        
    Returns:
        Dict[str, Any]: Dictionary chứa các cài đặt đã cập nhật
    """
    current = get_current_settings()
    # Cập nhật từng giá trị
    for key, value in settings_dict.items():
        current[key] = value
    
    # Lưu lại vào session state
    st.session_state.settings = current
    
    return current

def generate_cache_key(
    audio_bytes: bytes,
    processing_mode: str,
    model: str,
    leading_silence_ms: int,
    trailing_silence_ms: int,
) -> str:
    """
    Tạo cache key duy nhất dựa trên nội dung audio và các tham số xử lý.

    Args:
        audio_bytes: Nội dung của file audio dạng bytes
        processing_mode: Chế độ xử lý
        model: Model AI sử dụng
        leading_silence_ms: Khoảng lặng đầu (ms)
        trailing_silence_ms: Khoảng lặng cuối (ms)

    Returns:
        str: Cache key duy nhất
    """
    # Tạo hash từ nội dung file và các tham số
    hash_obj = hashlib.md5()

    # Hash nội dung file (có thể lấy mẫu để tránh hash toàn bộ file lớn)
    if len(audio_bytes) > 1024 * 1024:  # Nếu file lớn hơn 1MB
        # Lấy 512KB đầu, 512KB cuối và 10 mẫu ngẫu nhiên từ giữa
        sample_size = 1024  # 1KB mỗi mẫu
        hash_obj.update(audio_bytes[: 512 * 1024])  # 512KB đầu
        hash_obj.update(audio_bytes[-512 * 1024 :])  # 512KB cuối

        # Lấy 10 mẫu từ giữa
        total_len = len(audio_bytes)
        for i in range(10):
            pos = (512 * 1024) + i * ((total_len - 1024 * 1024) // 10)
            hash_obj.update(audio_bytes[pos : pos + sample_size])
    else:
        # Hash toàn bộ file nếu kích thước file nhỏ
        hash_obj.update(audio_bytes)

    # Hash các tham số xử lý
    hash_obj.update(processing_mode.encode("utf-8"))
    hash_obj.update(model.encode("utf-8"))
    hash_obj.update(str(leading_silence_ms).encode("utf-8"))
    hash_obj.update(str(trailing_silence_ms).encode("utf-8"))

    return hash_obj.hexdigest()

def render_cache_ui():
    """
    Hiển thị UI quản lý cache trong sidebar.
    """
    if "audio_cache" in st.session_state:
        cache_count = len(st.session_state.audio_cache)
        if cache_count > 0:
            st.sidebar.markdown("---")
            st.sidebar.subheader("Cache")
            st.sidebar.info(f"Hiện có {cache_count} kết quả trong cache")

            # Nút xóa cache
            if st.sidebar.button(BUTTON_CLEAR_CACHE):
                st.session_state.audio_cache = {}
                st.sidebar.success("Đã xóa cache thành công!")
                time.sleep(0.5)
                st.rerun()  # Rerun app để cập nhật giao diện
