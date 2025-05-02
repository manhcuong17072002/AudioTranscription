"""
Ứng dụng demo cho công cụ phiên âm và phân đoạn audio.
"""

import hashlib
import logging
import sys
import tempfile
import time
from io import BytesIO
from pathlib import Path
from typing import Any, Dict, Tuple, Callable

import streamlit as st
from streamlit.runtime.uploaded_file_manager import UploadedFile

# Thiết lập tiêu đề và thông tin
st.set_page_config(page_title="Audio Transcription Demo", layout="wide")

st.title("Công cụ phiên âm và phân đoạn audio")

# Thiết lập logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@st.cache_resource
def import_from_core() -> Tuple[Callable, Callable]:
    from sources.core.audio_processor import (
        extract_transcript_text,
        process_audio_with_alignment,
    )
    
    return extract_transcript_text, process_audio_with_alignment

extract_transcript_text, process_audio_with_alignment = import_from_core()


# Hàm để lấy cài đặt hiện tại
def get_current_settings():
    """Lấy cài đặt hiện tại từ session state hoặc trả về cài đặt mặc định"""
    if "settings" not in st.session_state:
        st.session_state.settings = {
            "model": "gemini-2.0-flash",
            "max_retries": 3,
            "leading_silence_ms": 100,
            "trailing_silence_ms": 100,
            "cache_results": True,
        }
    return st.session_state.settings


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


# Hàm chính của ứng dụng
def main():

    # Lấy cài đặt hiện tại
    settings = get_current_settings()

    # Sidebar cho các tùy chọn
    st.sidebar.title("Menu")

    # Thêm thông tin và nút xóa cache
    if "audio_cache" in st.session_state:
        cache_count = len(st.session_state.audio_cache)
        if cache_count > 0:
            st.sidebar.markdown("---")
            st.sidebar.subheader("Cache")
            st.sidebar.info(f"Hiện có {cache_count} kết quả trong cache")

            # Nút xóa cache
            if st.sidebar.button("Xóa cache"):
                st.session_state.audio_cache = {}
                st.sidebar.success("Đã xóa cache thành công!")
                time.sleep(0.5)
                st.rerun()  # Rerun app để cập nhật giao diện

    # Hiển thị trang chính
    show_main_page(settings)

    # Thông tin footer
    st.sidebar.markdown("---")
    st.sidebar.info("Audio Transcription Demo © 2025")


# Trang chính của ứng dụng
def show_main_page(settings: Dict[str, Any]):
    """
    Hiển thị trang chính của ứng dụng.

    Args:
        settings: Cài đặt hiện tại của ứng dụng
    """
    st.header("Phiên âm và phân đoạn audio")

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
        uploaded_file = st.file_uploader("Tải lên file audio", type=["wav", "mp3"])

        # Chọn chế độ xử lý
        processing_mode = st.radio(
            "Chế độ xử lý",
            ["Chỉ phiên âm", "Phiên âm và phân đoạn"],
            index=1,
            help="Chọn chỉ phiên âm để lấy text, hoặc phiên âm và phân đoạn để có các file audio riêng cho từng câu",
        )

        # Chọn cấu hình xử lý
        with st.expander("Cấu hình xử lý"):
            col1, col2 = st.columns(2)

            with col1:
                model = st.selectbox(
                    "Model AI",
                    options=["gemini-2.0-flash", "gemini-2.0-flash-lite"],
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
        submitted = st.form_submit_button("Xử lý Audio")

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
    # Tạo thư mục tạm để lưu kết quả phân đoạn (nếu cần)
    temp_dir = tempfile.mkdtemp()

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
                    save_folder=temp_dir if do_alignment else None,
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
                combined_results = process_audio_with_alignment(
                    audio_file=audio_buffer,
                    leading_silence_ms=0,
                    trailing_silence_ms=0,
                    save_folder=None,
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

        # Hiển thị thông tin trang kết quả
        st.info(
            "Bạn có thể xem và tải xuống kết quả chi tiết ở trang [Kết quả phiên âm] trong thanh bên"
        )

        # Hiển thị preview kết quả
        st.subheader("Xem trước văn bản phiên âm")
        st.text_area("Kết quả phiên âm", transcript_text, height=200)

    except Exception as e:
        st.error(f"Đã xảy ra lỗi: {str(e)}")
        logger.error(f"Lỗi khi xử lý audio: {str(e)}", exc_info=True)


# Chạy app
if __name__ == "__main__":
    main()
