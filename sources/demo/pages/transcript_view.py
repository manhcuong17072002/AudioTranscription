"""
Trang hiển thị chi tiết kết quả phiên âm và phân đoạn.
"""
import sys
from pathlib import Path
from typing import Dict, List

import streamlit as st

# Đảm bảo import đúng các modules từ thư mục cha
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from sources.demo.utils.display_utils import show_transcript_details as utils_show_transcript_details

def show_transcript_details(transcription_results: List[Dict]):
    """
    Hiển thị chi tiết kết quả phiên âm và phân đoạn.
    
    Args:
        transcription_results: Kết quả phiên âm và phân đoạn
    """
    st.title("Chi tiết kết quả phiên âm")
    
    # Sử dụng hàm từ display_utils.py để hiển thị chi tiết
    utils_show_transcript_details(transcription_results, page_state_key='page_number')
        
if __name__ == "__main__":
    if "transcription_results" in st.session_state:
        show_transcript_details(st.session_state.transcription_results)
    else:
        st.warning("Không có kết quả phiên âm nào để hiển thị.")
