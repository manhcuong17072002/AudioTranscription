"""
Các hàm tiện ích để tạo và xử lý file zip.
"""
import json
import os
import shutil
import tempfile
import zipfile
from io import BytesIO
from typing import Dict, List, Optional, Union


def create_zip_from_audio_chunks(
    audio_chunks: List[Dict], 
    include_audio: bool = True, 
    include_text: bool = True,
    include_metadata: bool = False
) -> BytesIO:
    """
    Tạo file zip từ danh sách các audio chunks.
    
    Args:
        audio_chunks: Danh sách dictionaries chứa audio và text
        include_audio: Có bao gồm các file audio trong zip hay không
        include_text: Có bao gồm các file text trong zip hay không
        include_metadata: Có bao gồm file metadata.json hay không
        
    Returns:
        BytesIO: Buffer chứa nội dung file zip
    """
    # Tạo buffer để lưu file zip
    zip_buffer = BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for i, chunk in enumerate(audio_chunks):
            # Xác định tên file cho audio và text
            filename = chunk.get('filename', f"chunk_{i}.wav")
            basename, _ = os.path.splitext(filename)  # Lấy tên file không có phần mở rộng
            
            # Thêm file audio vào zip nếu include_audio = True
            if include_audio and 'audio' in chunk:
                # Lưu audio vào temporary file
                temp_audio = BytesIO()
                chunk['audio'].export(temp_audio, format="wav")
                temp_audio.seek(0)
                zip_file.writestr(f"{basename}.wav", temp_audio.getvalue())
                
            # Thêm file text vào zip nếu include_text = True
            if include_text and 'text' in chunk:
                zip_file.writestr(f"{basename}.txt", chunk['text'])
        
        # Thêm file metadata.json nếu include_metadata = True
        if include_metadata:
            # Tạo bản sao của transcription_results để xóa AudioSegment không thể serialize
            metadata = []
            for chunk in audio_chunks:
                chunk_copy = chunk.copy()
                if "audio" in chunk_copy:
                    del chunk_copy["audio"]
                metadata.append(chunk_copy)
                
            json_content = json.dumps(metadata, indent=2, ensure_ascii=False).encode('utf-8')
            zip_file.writestr("metadata.json", json_content)
    
    # Reset con trỏ về đầu buffer
    zip_buffer.seek(0)
    return zip_buffer


def create_zip_from_directory(directory_path: str) -> BytesIO:
    """
    Tạo file zip từ một thư mục.
    
    Args:
        directory_path: Đường dẫn đến thư mục cần nén
        
    Returns:
        BytesIO: Buffer chứa nội dung file zip
    """
    # Tạo buffer để lưu file zip
    zip_buffer = BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for root, _, files in os.walk(directory_path):
            for file in files:
                file_path = os.path.join(root, file)
                # Tạo đường dẫn tương đối trong zip
                arcname = os.path.relpath(file_path, os.path.dirname(directory_path))
                zip_file.write(file_path, arcname)
    
    # Reset con trỏ về đầu buffer
    zip_buffer.seek(0)
    return zip_buffer


def save_audio_chunks_to_temp_dir(
    audio_chunks: List[Dict], 
    include_audio: bool = True, 
    include_text: bool = True
) -> str:
    """
    Lưu các audio chunks vào thư mục tạm.
    
    Args:
        audio_chunks: Danh sách dictionaries chứa audio và text
        include_audio: Có lưu các file audio hay không
        include_text: Có lưu các file text hay không
        
    Returns:
        str: Đường dẫn đến thư mục tạm chứa các file
    """
    # Tạo thư mục tạm
    temp_dir = tempfile.mkdtemp()
    
    try:
        for i, chunk in enumerate(audio_chunks):
            filename = chunk.get('filename', f"chunk_{i}.wav")
            basename, _ = os.path.splitext(filename)
            
            # Lưu file audio
            if include_audio and 'audio' in chunk:
                audio_path = os.path.join(temp_dir, f"{basename}.wav")
                chunk['audio'].export(audio_path, format="wav")
                
            # Lưu file text
            if include_text and 'text' in chunk:
                text_path = os.path.join(temp_dir, f"{basename}.txt")
                with open(text_path, 'w', encoding='utf-8') as f:
                    f.write(chunk['text'])
                    
        return temp_dir
    except Exception as e:
        # Dọn dẹp thư mục tạm nếu có lỗi
        shutil.rmtree(temp_dir, ignore_errors=True)
        raise e
