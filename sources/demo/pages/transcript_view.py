"""
Trang hiển thị chi tiết kết quả phiên âm và phân đoạn.
"""
import json
import os
import sys
from io import BytesIO
from pathlib import Path
from typing import Dict, List

import pandas as pd
import streamlit as st

# Đảm bảo import đúng các modules từ thư mục cha
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from sources.demo.utils.zip_utils import create_zip_from_audio_chunks


def show_transcript_details(transcription_results: List[Dict]):
    """
    Hiển thị chi tiết kết quả phiên âm và phân đoạn.
    
    Args:
        transcription_results: Kết quả phiên âm và phân đoạn
    """
    st.title("Chi tiết kết quả phiên âm")
    
    if not transcription_results:
        st.warning("Không có kết quả phiên âm để hiển thị")
        return
    
    # Hiển thị tổng kết
    st.subheader("Tổng kết")
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
    st.dataframe(df, use_container_width=True)
    
    # Hiển thị chi tiết từng đoạn
    st.subheader("Chi tiết từng đoạn")
    
    for i, result in enumerate(transcription_results):
        with st.expander(f"Đoạn {i+1}: {result.get('text', '')[:50]}..."):
            col1, col2 = st.columns(2)
            
            with col1:
                st.text_area("Nội dung", result.get("text", ""), height=100)
            
            with col2:
                st.text_area("Đặc điểm giọng nói", result.get("description", ""), height=100)
            
            # Hiển thị audio nếu có
            if "audio" in result:
                # Lưu audio vào buffer
                audio_buffer = BytesIO()
                result["audio"].export(audio_buffer, format="wav")
                audio_buffer.seek(0)
                
                st.audio(audio_buffer, format="audio/wav")
    
    # Tạo nút tải xuống các định dạng khác nhau
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
            label="Tải JSON",
            data=json_buffer,
            file_name="transcription_results.json",
            mime="application/json"
        )
    
    with col2:
        # Tải xuống ZIP chỉ chứa text
        zip_buffer_text = create_zip_from_audio_chunks(transcription_results, include_audio=False, include_text=True)
        
        st.download_button(
            label="Tải văn bản (ZIP)",
            data=zip_buffer_text,
            file_name="text_files.zip",
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
            label="Tải audio, text & metadata (ZIP)",
            data=zip_buffer_all,
            file_name="audio_text_files.zip", 
            mime="application/zip",
            help="Tải về file ZIP chứa các file audio (.wav), văn bản (.txt) và metadata.json"
        )
        
if __name__ == "__main__":
    if "transcription_results" in st.session_state:
        show_transcript_details(st.session_state.transcription_results)
    else:
        st.warning("Không có kết quả phiên âm nào để hiển thị.")
        