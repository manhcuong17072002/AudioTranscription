"""
Các hàm tiện ích để hiển thị kết quả phiên âm và phân đoạn.
"""

import json
from io import BytesIO
from typing import Dict, List

import pandas as pd
import streamlit as st

from sources.demo.utils.constants import (
    BUTTON_PREV_PAGE,
    BUTTON_NEXT_PAGE,
    DOWNLOAD_JSON_LABEL,
    DOWNLOAD_TEXT_ZIP_LABEL,
    DOWNLOAD_ALL_ZIP_LABEL,
    JSON_FILENAME,
    TEXT_ZIP_FILENAME,
    ALL_ZIP_FILENAME,
    ITEMS_PER_PAGE_MIN,
    ITEMS_PER_PAGE_MAX,
    ITEMS_PER_PAGE_DEFAULT
)
from sources.demo.utils.zip_utils import create_zip_from_audio_chunks

def show_transcript_details(transcription_results: List[Dict], page_state_key: str = 'page_number'):
    """
    Hiển thị chi tiết kết quả phiên âm và phân đoạn.
    
    Args:
        transcription_results: Kết quả phiên âm và phân đoạn
        page_state_key: Khóa lưu số trang trong session state (để hỗ trợ nhiều phiên)
    """
    if not transcription_results:
        st.warning("Không có kết quả phiên âm để hiển thị")
        return
    
    # Hiển thị tổng kết
    st.info(f"Tổng số đoạn: {len(transcription_results)}")
    
    # Tạo DataFrame từ dữ liệu để hiển thị dưới dạng bảng
    table_data = []
    for i, result in enumerate(transcription_results):
        table_data.append({
            "STT": i+1,
            "Nội dung": result.get("text", ""),
            "Đặc điểm giọng nói": result.get("description", "")
        })
    
    df = pd.DataFrame(table_data)
    st.dataframe(df, use_container_width=True, hide_index = True)
    
    # Cài đặt phân trang
    if page_state_key not in st.session_state:
        st.session_state[page_state_key] = 0
        
    # Số lượng đoạn mỗi trang - cho phép người dùng điều chỉnh
    items_per_page = st.sidebar.number_input(
        "Số đoạn hiển thị mỗi trang:", 
        min_value=ITEMS_PER_PAGE_MIN, 
        max_value=ITEMS_PER_PAGE_MAX, 
        value=ITEMS_PER_PAGE_DEFAULT,
        help="Điều chỉnh để hiển thị nhiều hoặc ít đoạn hơn trên mỗi trang. Số lượng nhỏ hơn sẽ tải nhanh hơn.",
        key=f"items_per_page_{page_state_key}"
    )
    
    total_pages = (len(transcription_results) - 1) // items_per_page + 1
    
    # Đảm bảo trang hiện tại nằm trong phạm vi hợp lệ sau khi thay đổi items_per_page
    if st.session_state[page_state_key] >= total_pages:
        st.session_state[page_state_key] = total_pages - 1
        
    # Lấy các đoạn cho trang hiện tại
    start_idx = st.session_state[page_state_key] * items_per_page
    end_idx = min(start_idx + items_per_page, len(transcription_results))
    page_results = transcription_results[start_idx:end_idx]
    
    # Hiển thị thanh điều hướng
    st.subheader(f"Chi tiết từng đoạn (Trang {st.session_state[page_state_key] + 1}/{total_pages})")
    st.caption(f"Hiển thị đoạn {start_idx+1}-{end_idx} trong tổng số {len(transcription_results)} đoạn")
        
    # Hiển thị chi tiết từng đoạn trong trang hiện tại
    for i, result in enumerate(page_results, start=start_idx + 1):
        with st.expander(f"Đoạn {i}: {result.get('text', '')[:50]}..."):
            col1, col2 = st.columns(2)
            
            with col1:
                st.text_area("Nội dung", result.get("text", ""), height=100)
            
            with col2:
                st.text_area("Đặc điểm giọng nói", result.get("description", ""), height=100)
            
            # Phần hiển thị audio
            st.subheader("Audio")
            
            # Hiển thị audio nếu có, ngược lại hiển thị thông báo
            if "audio" in result:
                audio_buffer = BytesIO()
                result["audio"].export(audio_buffer, format="wav")
                audio_buffer.seek(0)
                
                st.audio(audio_buffer, format="audio/wav")
            else:
                st.warning("Không có audio cho đoạn này")
    
    # Hiển thị thanh điều hướng ở dưới
    col1, col2, col3 = st.columns([5, 5, 1])
    with col1:
        prev_key = f"prev_{page_state_key}"
        if st.button(BUTTON_PREV_PAGE, key=prev_key) and st.session_state[page_state_key] > 0:
            st.session_state[page_state_key] -= 1
            st.rerun()
    with col2:
        st.write(f"Trang {st.session_state[page_state_key] + 1}/{total_pages}")
    with col3:
        next_key = f"next_{page_state_key}"
        if st.button(BUTTON_NEXT_PAGE, key=next_key) and st.session_state[page_state_key] < total_pages - 1:
            st.session_state[page_state_key] += 1
            st.rerun()
    
    # Hiển thị các nút tải xuống
    show_download_buttons(transcription_results)

def show_download_buttons(transcription_results: List[Dict]):
    """
    Hiển thị các nút tải xuống kết quả dưới nhiều định dạng.
    
    Args:
        transcription_results: Kết quả phiên âm và phân đoạn
    """
    st.subheader("Tải xuống kết quả")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Tải xuống JSON
        json_buffer = BytesIO()
        # Tạo bản sao của transcription_results để xóa AudioSegment
        json_data = []
        for result in transcription_results:
            result_copy = result.copy()
            if "audio" in result_copy:
                del result_copy["audio"]
            json_data.append(result_copy)
            
        json_buffer.write(json.dumps(json_data, indent=2, ensure_ascii=False).encode('utf-8'))
        json_buffer.seek(0)
        
        st.download_button(
            label=DOWNLOAD_JSON_LABEL,
            data=json_buffer,
            file_name=JSON_FILENAME,
            mime="application/json"
        )
    
    with col2:
        # Tải xuống ZIP chỉ chứa text
        zip_buffer_text = create_zip_from_audio_chunks(transcription_results, include_audio=False, include_text=True)
        
        st.download_button(
            label=DOWNLOAD_TEXT_ZIP_LABEL,
            data=zip_buffer_text,
            file_name=TEXT_ZIP_FILENAME,
            mime="application/zip"
        )
    
    with col3:
        # Tải xuống ZIP chứa cả audio, text và metadata
        zip_buffer_all = create_zip_from_audio_chunks(
            transcription_results, 
            include_audio=True, 
            include_text=True,
            include_metadata=True
        )
        
        st.download_button(
            label=DOWNLOAD_ALL_ZIP_LABEL,
            data=zip_buffer_all,
            file_name=ALL_ZIP_FILENAME, 
            mime="application/zip",
            help="Tải về file ZIP chứa các file audio (.wav), văn bản (.txt) và metadata.json"
        )
