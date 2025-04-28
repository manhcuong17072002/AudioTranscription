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
from .split_audio import split_audio_on_silence

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


def transcript_audios(
    files: Union[str, List[str], BytesIO, List[BytesIO]],
    batch_size: Optional[int] = 10,
    max_retries: int = 3,
    split_audio: bool = False,
    **kwargs,
) -> List[Dict[str, str]]:
    """
    Phiên âm nội dung của file audio sử dụng Google Gemini API.

    Args:
        files: Đường dẫn đến file audio hoặc BytesIO object, có thể là một đối tượng đơn lẻ hoặc danh sách
        batch_size: Số lượng file tối đa xử lý trong một lần gọi API
        max_retries: Số lần thử lại tối đa khi gặp lỗi rate limit
        split_audio: Tự động cắt file audio dài thành các đoạn nhỏ
        kwargs: Các tham số bổ sung cho việc cắt file audio

    Returns:
        List[Dict[str, str]]: Danh sách các kết quả phiên âm dưới dạng JSON

    Raises:
        ValueError: Nếu loại file không được hỗ trợ
        RuntimeError: Nếu không thể phiên âm sau số lần thử lại tối đa
    """

    # Chuẩn bị danh sách file
    if split_audio:
        if not isinstance(files, (str, BytesIO)):
            raise ValueError("Chỉ hỗ trợ cắt file audio đơn lẻ")

        files = split_audio_on_silence(
            files,
            **kwargs,
        )

    else:
        if isinstance(files, str):
            # If a single file is provided, convert it to a list
            files = [files]
        elif isinstance(files, BytesIO):
            # If a single BytesIO object is provided, convert it to a list
            files = [files]

    # Xử lý theo batch_size
    all_results = []
    
    # Chia files thành các batch
    for i in range(0, len(files), batch_size):
        batch_files = files[i:i + batch_size]
        batch_results = process_batch(batch_files, max_retries)
        all_results.extend(batch_results)
    
    return all_results

def process_batch(files: List[Union[str, BytesIO]], max_retries: int) -> List[Dict[str, str]]:
    """
    Xử lý một batch các file âm thanh.

    Args:
        files: Danh sách các file âm thanh cần xử lý
        max_retries: Số lần thử lại tối đa khi gặp lỗi rate limit

    Returns:
        List[Dict[str, str]]: Kết quả phiên âm cho batch này
        
    Raises:
        ValueError: Nếu loại file không được hỗ trợ
        RuntimeError: Nếu không thể phiên âm sau số lần thử lại tối đa
    """
    try:
        uploaded_files = []
        filenames = []

        # Upload các file trong batch
        for file in files:
            if isinstance(file, str):
                filenames.append(os.path.basename(file))
                config = {}

            elif isinstance(file, BytesIO):
                # Determine MIME type for BytesIO objects
                mime_type = magic.from_buffer(file.getvalue(), mime=True)
                config = {"mime_type": mime_type}

                # Xử lý tên file cho BytesIO
                if hasattr(file, "name") and file.name:
                    filenames.append(os.path.basename(file.name))
                else:
                    filenames.append(f"audio_{generate_random_string(8)}.wav")
            else:
                raise ValueError("Unsupported file type")

            uploaded_file = client.files.upload(file=file, config=config)
            uploaded_files.append(uploaded_file)

        print(f"Đã upload {len(uploaded_files)} files trong batch")

        # Thử lại nếu gặp lỗi rate limit
        for attempt in range(max_retries):
            try:
                response = client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=[prompt, uploaded_files],
                )

                # Lấy text từ response
                response_text = response.text

                # Phân tích kết quả JSON
                results = parse_response(response_text)

                # Thêm tên file vào kết quả
                for i, result in enumerate(results):
                    file_index = min(i, len(filenames) - 1) if filenames else 0
                    if not "Filename" in result and filenames:
                        result["Filename"] = filenames[file_index]

                print(f"Phiên âm thành công batch {len(results)} kết quả")
                return results

            except Exception as e:
                error_message = str(e).lower()

                # Kiểm tra nếu là lỗi rate limit
                if "rate limit" in error_message or "quota" in error_message:
                    print(
                        f"Gặp lỗi rate limit, đang thử lại ({attempt+1}/{max_retries})..."
                    )
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
