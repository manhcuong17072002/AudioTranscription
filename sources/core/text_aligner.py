import os
import random
import string
from io import BytesIO
from tempfile import NamedTemporaryFile
from typing import Dict, List, Optional, Tuple, Union

import stable_whisper
from stable_whisper.result import WhisperResult
from pydub import AudioSegment

model = stable_whisper.load_model('large-v3', device = "cpu")

def get_audio_chunks(text: Union[str, list[str]], audio_file: Union[str, BytesIO, bytes], save_folder: Optional[str] = None):
    """
    Align text với audio, cắt audio thành các đoạn theo timestamp từ file SRT.
    
    Args:
        text: Văn bản cần align với audio, có thể là string hoặc list of strings
        audio_file: File audio, có thể là đường dẫn, BytesIO hoặc bytes
        save_folder: Thư mục để lưu các đoạn audio và text, nếu None thì không lưu
        
    Returns:
        Nếu save_folder là None: Danh sách các đoạn audio dạng pydub.AudioSegment
        Nếu save_folder được cung cấp: Đường dẫn đến thư mục chứa các file đã lưu
    """
    if isinstance(text, list):
        text = "\n".join(text)
        
    if isinstance(audio_file, BytesIO):
        audio_file = audio_file.read()
    
    # Align text với audio sử dụng stable_whisper
    result: WhisperResult = model.align(audio_file, text, language='vi', original_split=True)
    
    # Load file audio gốc
    audio = load_audio(audio_file)
    
    # Cắt audio theo timestamps từ segments
    audio_chunks = []
    for segment in result.segments:
        # Lấy timestamp (đã là milliseconds) và text từ segment
        start_time_ms = int(segment.start * 1000)  # Chuyển từ giây sang milliseconds
        end_time_ms = int(segment.end * 1000)      # Chuyển từ giây sang milliseconds
        subtitle = segment.text.strip()
        
        # Cắt audio theo timestamps
        chunk = audio[start_time_ms:end_time_ms]
        audio_chunks.append((chunk, subtitle))
    
    # Xử lý output tùy thuộc vào save_folder
    if save_folder:
        # Tạo thư mục nếu chưa tồn tại
        os.makedirs(save_folder, exist_ok=True)
        
        # Lưu từng đoạn audio và text
        for i, (chunk, subtitle) in enumerate(audio_chunks):
            # Tạo tên file ngẫu nhiên
            random_name = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
            
            # Lưu file audio
            audio_path = os.path.join(save_folder, f"{random_name}.wav")
            chunk.export(audio_path, format="wav")
            
            # Lưu file text
            text_path = os.path.join(save_folder, f"{random_name}.txt")
            with open(text_path, 'w', encoding='utf-8') as f:
                f.write(subtitle)
        
        return save_folder
    else:
        # Trả về danh sách các đoạn audio
        return [chunk for chunk, _ in audio_chunks]

def load_audio(audio_file: Union[str, BytesIO, bytes]) -> AudioSegment:
    """
    Load file audio từ các định dạng khác nhau thành AudioSegment.
    
    Args:
        audio_file: File audio, có thể là đường dẫn, BytesIO hoặc bytes
        
    Returns:
        AudioSegment: Đối tượng AudioSegment
    """
    if isinstance(audio_file, str):
        # Đường dẫn file
        return AudioSegment.from_file(audio_file)
    elif isinstance(audio_file, BytesIO):
        # BytesIO object
        return AudioSegment.from_file(audio_file)
    elif isinstance(audio_file, bytes):
        # Bytes data
        with BytesIO(audio_file) as audio_bytes:
            return AudioSegment.from_file(audio_bytes)
    else:
        raise ValueError("Định dạng audio không được hỗ trợ")
