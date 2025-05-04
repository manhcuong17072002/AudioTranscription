"""
Trang phiên âm và phân đoạn audio.
"""

import logging
import time
from io import BytesIO
from typing import Dict, List

import pandas as pd
import streamlit as st
from streamlit.runtime.uploaded_file_manager import UploadedFile

# Import từ utils
from sources.demo.utils.constants import (
    APP_TITLE,
    BUTTON_PROCESS_AUDIO,
    DEFAULT_PROCESSING_MODE_INDEX,
    MODEL_OPTIONS,
    PROCESSING_MODES,
    SUPPORTED_AUDIO_FORMATS,
    TRANSCRIPT_PREVIEW_HEIGHT
)
from sources.demo.utils.cache_utils import get_current_settings, generate_cache_key
from sources.demo.utils.display_utils import show_transcript_details

# Import từ core
from sources.core.stt_llm import transcript_audio

# Thiết lập logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

@st.cache_resource
def import_from_core():
    """Import các hàm cần thiết từ core module."""
    from sources.core.audio_processor import (extract_transcript_text,
                                             process_audio_with_alignment)
    
    return extract_transcript_text, process_audio_with_alignment

extract_transcript_text, process_audio_with_alignment = import_from_core()

def show_labeling_page():
    """
    Hiển thị trang phiên âm và phân đoạn audio.
    """
    st.title(APP_TITLE)

    # Lấy cài đặt hiện tại
    settings = get_current_settings()

    # Hiển thị giới thiệu
    with st.expander("Giới thiệu"):
        st.markdown(
            """
        **Công cụ này giúp bạn:**
        - Phiên âm nội dung audio sử dụng Google Gemini AI
        - Phân đoạn audio theo câu/đoạn phiên âm
        - Xuất kết quả dưới dạng JSON hoặc các file audio và text riêng biệt
        
        **Cách sử dụng:**
        1. Tải lên file audio (định dạng WAV, MP3)
        2. Chọn chế độ xử lý (chỉ phiên âm hoặc phiên âm và phân đoạn)
        3. Nhấn nút xử lý và đợi kết quả
        4. Xem và tải xuống kết quả
        
        **Lưu ý:** Thời gian xử lý phụ thuộc vào độ dài audio và tùy chọn xử lý bạn chọn.
        """
        )

    # Form tải lên và xử lý audio
    with st.form("upload_form"):
        # Tải lên file audio
        uploaded_file = st.file_uploader("Tải lên file audio", type=SUPPORTED_AUDIO_FORMATS)

        # Chọn chế độ xử lý
        processing_mode = st.radio(
            "Chế độ xử lý",
            PROCESSING_MODES,
            index=DEFAULT_PROCESSING_MODE_INDEX,
            help="Chọn chỉ phiên âm để lấy text, hoặc phiên âm và phân đoạn để có các file audio riêng cho từng câu",
        )

        # Chọn cấu hình xử lý
        with st.expander("Cấu hình xử lý"):
            col1, col2 = st.columns(2)

            with col1:
                model = st.selectbox(
                    "Model AI",
                    options=MODEL_OPTIONS,
                    index=0,
                    help="Model AI sử dụng để phiên âm audio",
                )

                max_retries = st.slider(
                    "Số lần thử lại khi gặp lỗi",
                    min_value=1,
                    max_value=10,
                    value=settings.get("max_retries", 3),
                    help="Số lần thử lại tối đa khi gặp lỗi rate limit",
                )

            with col2:
                leading_silence_ms = st.slider(
                    "Khoảng im lặng đầu (milliseconds)",
                    min_value=0,
                    max_value=1000,
                    value=settings.get("leading_silence_ms", 100),
                    step=10,
                    help="Khoảng im lặng (milliseconds) thêm vào đầu mỗi đoạn audio",
                )

                trailing_silence_ms = st.slider(
                    "Khoảng im lặng cuối (milliseconds)",
                    min_value=0,
                    max_value=1000,
                    value=settings.get("trailing_silence_ms", 100),
                    step=10,
                    help="Khoảng im lặng (milliseconds) thêm vào cuối mỗi đoạn audio",
                )

        # Nút submit
        submitted = st.form_submit_button(BUTTON_PROCESS_AUDIO)

    # Xử lý khi người dùng submit form
    if submitted and uploaded_file is not None:
        process_uploaded_audio(
            uploaded_file,
            processing_mode,
            model,
            max_retries,
            leading_silence_ms,
            trailing_silence_ms,
        )

def process_uploaded_audio(
    uploaded_file: UploadedFile,
    processing_mode: str,
    model: str,
    max_retries: int,
    leading_silence_ms: int,
    trailing_silence_ms: int,
):
    """
    Xử lý file audio đã tải lên.
    
    Args:
        uploaded_file: File audio đã tải lên
        processing_mode: Chế độ xử lý ("Chỉ phiên âm" hoặc "Phiên âm và phân đoạn")
        model: Model AI sử dụng
        max_retries: Số lần thử lại tối đa
        leading_silence_ms: Khoảng lặng đầu (ms)
        trailing_silence_ms: Khoảng lặng cuối (ms)
    """
    try:
        # Hiển thị thông tin file và trạng thái xử lý
        st.info(f"Đang xử lý file: {uploaded_file.name}")
        progress_bar = st.progress(0)
        status_text = st.empty()

        # Đọc nội dung file audio
        audio_bytes = uploaded_file.getvalue()

        # Xác định có phân đoạn hay không dựa trên processing_mode
        do_alignment = processing_mode == "Phiên âm và phân đoạn"

        # Kiểm tra cache nếu cài đặt cache_results = True
        settings = get_current_settings()
        use_cache = settings.get("cache_results", True)
        cache_used = False
        combined_results = None

        if use_cache:
            # Tạo cache key từ nội dung file và các tham số xử lý
            cache_key = generate_cache_key(
                audio_bytes,
                processing_mode,
                model,
                leading_silence_ms if do_alignment else 0,
                trailing_silence_ms if do_alignment else 0,
            )

            # Kiểm tra cache trong session state
            if "audio_cache" not in st.session_state:
                st.session_state.audio_cache = {}

            # Nếu kết quả đã có trong cache, sử dụng nó
            if cache_key in st.session_state.audio_cache:
                status_text.text("Đang tải kết quả từ cache...")
                progress_bar.progress(40)

                # Lấy kết quả từ cache
                combined_results = st.session_state.audio_cache[cache_key]
                cache_used = True

                progress_bar.progress(80)
                status_text.text("Đã tìm thấy kết quả trong cache!")
                time.sleep(0.5)  # Tạm dừng để người dùng thấy thông báo

        # Nếu không có trong cache hoặc không sử dụng cache, xử lý bình thường
        if not cache_used:
            # Tạo lại BytesIO từ bytes vì có thể đã đọc cũ nếu kiểm tra cache
            audio_buffer = BytesIO(audio_bytes)

            status_text.text("Đang xử lý audio...")
            progress_bar.progress(20)

            if do_alignment:
                # Xử lý phiên âm và phân đoạn
                combined_results = process_audio_with_alignment(
                    audio_file=audio_buffer,
                    leading_silence_ms=leading_silence_ms,
                    trailing_silence_ms=trailing_silence_ms,
                    save_folder=None,
                    max_retries=max_retries,
                    model=model,
                )

                progress_bar.progress(80)
                status_text.text("Xử lý hoàn tất! Đang chuẩn bị kết quả...")

                # Lưu vào cache nếu đã bật tính năng cache
                if use_cache and not cache_used:
                    st.session_state.audio_cache[cache_key] = combined_results

            else:
                # Chỉ phiên âm, không phân đoạn
                combined_results = transcript_audio(
                    audio_file=audio_buffer,
                    max_retries=max_retries,
                    model=model,
                )

                progress_bar.progress(80)
                status_text.text("Phiên âm hoàn tất! Đang chuẩn bị kết quả...")

                # Lưu vào cache nếu đã bật tính năng cache
                if use_cache and not cache_used:
                    st.session_state.audio_cache[cache_key] = combined_results

        # Lưu kết quả vào session state để các trang khác có thể truy cập
        st.session_state.transcription_results = combined_results

        # Trích xuất văn bản từ kết quả để hiển thị
        transcript_text = extract_transcript_text(combined_results)

        # Hiển thị thống kê cache nếu sử dụng cache
        if use_cache:
            cache_count = len(st.session_state.get("audio_cache", {}))
            cache_status = "sử dụng kết quả có sẵn" if cache_used else "lưu kết quả mới"
            st.sidebar.info(f"Cache: {cache_count} kết quả ({cache_status})")

        # Hoàn thành
        progress_bar.progress(100)
        status_text.text("Xử lý hoàn tất!")

        # Thông báo thành công
        st.success("Đã xử lý audio thành công!")

        # Hiển thị preview kết quả dạng text đơn giản
        with st.expander("Xem trước văn bản phiên âm tổng hợp", expanded=False):
            st.text_area("Kết quả phiên âm", transcript_text, height=TRANSCRIPT_PREVIEW_HEIGHT)

        # Hiển thị kết quả chi tiết từng đoạn
        show_transcript_details(combined_results, page_state_key='labeling_page_number')

    except Exception as e:
        st.error(f"Đã xảy ra lỗi: {str(e)}")
        logger.error(f"Lỗi khi xử lý audio: {str(e)}", exc_info=True)

if __name__ == "__main__":
    show_labeling_page()
