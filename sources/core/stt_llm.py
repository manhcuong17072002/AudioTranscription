import json
import os
import random
import string
import time
from io import BytesIO
from typing import Dict, List, Union, Optional

from api_key import *
from google import genai
from magic import Magic

magic = Magic()

# Danh sách API key
API_KEYS = [API_KEY1, API_KEY2, API_KEY3, API_KEY4]
current_key_index = 1  # Bắt đầu với API_KEY2

# Khởi tạo client với API key mặc định
client = genai.Client(api_key=API_KEYS[current_key_index])

prompt = """
Please transcribe this audio file into text following these rules:
1. Transcribe exactly what the speaker says, without adding or omitting any words.
2. Use only plain letters; do not include numbers, special characters, or any formatting.
3. Return the output in the following JSON structure:
```json 
[
    {
        "Transcript": "The plain text transcription that accurately reflects the content of the audio. Each item should be one sentence, transcribed exactly as spoken in the audio.",
        "Voice Description": "Provide a detailed description of the speaker's voice characteristics, including gender, tone, emotion, pronunciation, and speaking style. For example: A female speaker delivers a slightly expressive and animated speech with a very high-pitched voice, sounding very close-up in the recording. Almost no noise is present in the background, contributing to a clear and crisp listening experience. Each voice description must be distinct and not repeated across different entries."
    }
]
```
4. Do not add any explanations, comments, or any information outside of the format above.
"""

def change_api_key():
    """
    Thay đổi API key khi bị rate limit.
    Chuyển sang API key tiếp theo trong danh sách.
    """
    global current_key_index, client
    current_key_index = (current_key_index + 1) % len(API_KEYS)
    client = genai.Client(api_key=API_KEYS[current_key_index])
    print(f"Đã chuyển sang API key #{current_key_index + 1}")

def parse_response(response_text: str) -> List[Dict[str, str]]:
    """
    Phân tích kết quả JSON từ văn bản trả về của Gemini.

    Args:
        response_text (str): Văn bản trả về từ Gemini API

    Returns:
        List[Dict[str, str]]: Danh sách các kết quả phiên âm đã được phân tích

    Raises:
        ValueError: Nếu không thể phân tích kết quả thành JSON
    """
    try:
        # Tìm kiếm chuỗi JSON trong kết quả
        start_index = response_text.find("[")
        end_index = response_text.rfind("]") + 1

        if start_index == -1 or end_index == 0:
            raise ValueError("Không tìm thấy định dạng JSON hợp lệ")

        json_str = response_text[start_index:end_index]
        return json.loads(json_str)

    except (json.JSONDecodeError, ValueError) as e:
        print(f"Lỗi khi phân tích kết quả: {e}")
        print(f"Kết quả trả về: {response_text}")
        raise ValueError(f"Không thể phân tích kết quả thành JSON: {e}")

def generate_random_string(length: int = 20) -> str:
    """
    Tạo một chuỗi ngẫu nhiên với độ dài nhất định.

    Args:
        length (int): Độ dài của chuỗi ngẫu nhiên

    Returns:
        str: Chuỗi ngẫu nhiên
    """
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))

def transcript_audio(
    file: Union[str, BytesIO],
    max_retries: int = 3,
    model:str = "gemini-2.0-flash"
) -> List[Dict[str, str]]:
    """
    Phiên âm nội dung của file audio sử dụng Google Gemini API.

    Args:
        file: Đường dẫn đến file audio hoặc BytesIO object
        max_retries: Số lần thử lại tối đa khi gặp lỗi rate limit

    Returns:
        List[Dict[str, str]]: Kết quả phiên âm dưới dạng JSON

    Raises:
        ValueError: Nếu loại file không được hỗ trợ
        RuntimeError: Nếu không thể phiên âm sau số lần thử lại tối đa
    """
    try:
        # Khởi tạo danh sách để lưu file đã upload
        uploaded_files = []
        filename = ""

        # Xử lý file input
        if isinstance(file, str):
            filename = os.path.basename(file)
            config = {}
        elif isinstance(file, BytesIO):
            # Xác định MIME type cho BytesIO objects
            mime_type = magic.from_buffer(file.getvalue(), mime=True)
            config = {"mime_type": mime_type}

            # Xử lý tên file cho BytesIO
            if hasattr(file, "name") and file.name:
                filename = os.path.basename(file.name)
            else:
                filename = f"audio_{generate_random_string()}.wav"
        else:
            raise ValueError("Định dạng file không được hỗ trợ")

        # Upload file
        uploaded_file = client.files.upload(file=file, config=config)
        uploaded_files.append(uploaded_file)

        # Thử lại nếu gặp lỗi rate limit
        for attempt in range(max_retries):
            try:
                # Gọi API Gemini
                response = client.models.generate_content(
                    model=model,
                    contents=[prompt, uploaded_files],
                )

                # Lấy text từ response
                response_text = response.text

                # Phân tích kết quả JSON
                results = parse_response(response_text)

                print(f"Phiên âm thành công file {filename}: {len(results)} kết quả")
                return results

            except Exception as e:
                error_message = str(e).lower()

                # Kiểm tra nếu là lỗi rate limit
                if "rate limit" in error_message or "quota" in error_message:
                    print(f"Gặp lỗi rate limit, đang thử lại ({attempt+1}/{max_retries})...")
                    change_api_key()
                    time.sleep(1)  # Chờ 1 giây trước khi thử lại
                else:
                    # Lỗi khác, không phải rate limit
                    print(f"Lỗi khi gọi API: {e}")
                    raise

        # Nếu đã thử tất cả API key mà vẫn không thành công
        raise RuntimeError(f"Không thể phiên âm sau {max_retries} lần thử lại")
    
    finally:
        # Xóa các file đã upload để giải phóng tài nguyên
        try:
            for f in client.files.list():
                print(f"Xóa file đã upload: {f.name}")
                client.files.delete(name=f.name)
        except Exception as e:
            print(f"Lỗi khi xóa files đã upload: {e}")
