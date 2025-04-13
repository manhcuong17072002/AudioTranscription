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
Accurately transcribe the audio without adding or omitting any words. If parts of the audio are unclear, rely on contextual clues to infer the missing words.

Ensure the entire transcript is in plain text format. Do not use any numerical formatting or special characters.3. The output must follow the structure below:
```json 
[
    {
        "Transcript": "The plain text transcription that accurately reflects the content of the audio.",
        "Voice Description": "Provide a detailed description of the speaker's voice characteristics, including gender, tone, emotion, pronunciation, and speaking style. For example: A female speaker delivers a slightly expressive and animated speech with a very high-pitched voice, sounding very close-up in the recording. Almost no noise is present in the background, contributing to a clear and crisp listening experience. Each voice description must be distinct and not repeated across different entries."
    }
]
```
4. Do not add any information outside of the format above.
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

    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def transcript_audios(
    files: Union[str, List[str], BytesIO, List[BytesIO]],
    max_retries: int = 3,
    split_audio: bool = False,
    min_silence_len: int = 500,  # ms
    silence_thresh: int = -40,   # dB
    keep_silence: int = 150,     # ms
    min_segment_length: int = 2000,  # ms
    max_segment_length: Optional[int] = 30000,  # ms, ~30s
) -> List[Dict[str, str]]:
    """
    Phiên âm nội dung của file audio sử dụng Google Gemini API.

    Args:
        files: Đường dẫn đến file audio hoặc BytesIO object, có thể là một đối tượng đơn lẻ hoặc danh sách
        max_retries: Số lần thử lại tối đa khi gặp lỗi rate limit
        split_audio: Tự động cắt file audio dài thành các đoạn nhỏ
        min_silence_len: Độ dài tối thiểu của khoảng lặng (ms)
        silence_thresh: Ngưỡng âm lượng để xác định khoảng lặng (dB)
        keep_silence: Giữ lại bao nhiêu khoảng lặng ở đầu và cuối mỗi đoạn (ms)
        min_segment_length: Độ dài tối thiểu của mỗi đoạn audio (ms)
        max_segment_length: Độ dài tối đa của mỗi đoạn audio (ms)

    Returns:
        List[Dict[str, str]]: Danh sách các kết quả phiên âm dưới dạng JSON

    Raises:
        ValueError: Nếu loại file không được hỗ trợ
        RuntimeError: Nếu không thể phiên âm sau số lần thử lại tối đa
    """
    # Kiểm tra nếu cần cắt file audio
    if split_audio:
        from sources.core.split_audio import process_audio_file
        
        # Nếu có nhiều file, xử lý từng file một
        if isinstance(files, list) and len(files) > 1:
            all_results = []
            for file in files:
                results = transcript_audios(
                    file, 
                    max_retries=max_retries,
                    split_audio=True,
                    min_silence_len=min_silence_len,
                    silence_thresh=silence_thresh,
                    keep_silence=keep_silence,
                    min_segment_length=min_segment_length,
                    max_segment_length=max_segment_length
                )
                all_results.extend(results)
            return all_results
        
        # Nếu chỉ có một file, cắt nó thành các đoạn
        single_file = files[0] if isinstance(files, list) else files
        
        # Lấy tên file gốc trước khi cắt
        original_filename = ""
        if isinstance(single_file, str):
            original_filename = os.path.basename(single_file)
        elif isinstance(single_file, BytesIO) and hasattr(single_file, 'name'):
            original_filename = os.path.basename(single_file.name)
        else:
            original_filename = f"audio_{generate_random_string(8)}"
        
        # Cắt file thành các đoạn
        audio_chunks = process_audio_file(
            single_file,
            min_silence_len=min_silence_len,
            silence_thresh=silence_thresh,
            keep_silence=keep_silence,
            min_segment_length=min_segment_length,
            max_segment_length=max_segment_length,
            save_to_disk=False
        )
        
        # Nếu không cần cắt (chỉ có 1 đoạn), sử dụng file gốc
        if len(audio_chunks) <= 1:
            return transcript_audios(single_file, max_retries=max_retries, split_audio=False)
        
        # Phiên âm từng đoạn và thêm tên file
        chunk_results = []
        for i, chunk in enumerate(audio_chunks):
            chunk_name = f"{original_filename}_part{i+1}"
            result = transcript_audios(chunk, max_retries=max_retries, split_audio=False)
            for item in result:
                item["Filename"] = chunk_name
            chunk_results.extend(result)
        
        return chunk_results
    
    # Xử lý phiên âm thông thường (không cắt)
    uploaded_files = []

    if isinstance(files, str):
        # If a single file is provided, convert it to a list
        files = [files]
    elif isinstance(files, BytesIO):
        # If a single BytesIO object is provided, convert it to a list
        files = [files]

    filenames = []

    for file in files:
        if isinstance(file, str):
            filenames.append(os.path.basename(file))
            config = {}
            
        elif isinstance(file, BytesIO):
            # Determine MIME type for BytesIO objects
            mime_type = magic.from_buffer(file.getvalue(), mime=True)
            config = {"mime_type": mime_type}
            
            # Xử lý tên file cho BytesIO
            if hasattr(file, 'name') and file.name:
                filenames.append(os.path.basename(file.name))
            else:
                filenames.append(f"audio_{generate_random_string(8)}.wav")
        else:
            raise ValueError("Unsupported file type")

        uploaded_file = client.files.upload(file=file, config=config)
        uploaded_files.append(uploaded_file)

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


def transcript_split_audio(
    audio_chunks: List[Union[str, BytesIO]],
) -> List[Dict[str, str]]:
    """
    Phiên âm nhiều đoạn audio đã được cắt.

    Args:
        audio_chunks: Danh sách các file audio sau khi đã cắt

    Returns:
        List[Dict[str, str]]: Danh sách kết quả phiên âm từ tất cả các đoạn audio
    """
    # Sử dụng transcript_audios với split_audio=False
    all_results = []

    # Phiên âm từng đoạn audio
    for i, chunk in enumerate(audio_chunks):
        try:
            result = transcript_audios(chunk, split_audio=False)
            # Thêm thông tin về phần nếu chưa có
            for item in result:
                if not "Filename" in item:
                    if isinstance(chunk, str):
                        chunk_name = os.path.basename(chunk)
                    elif hasattr(chunk, 'name') and chunk.name:
                        chunk_name = os.path.basename(chunk.name)
                    else:
                        chunk_name = f"audio_part{i+1}"
                    item["Filename"] = chunk_name
            all_results.extend(result)
        except Exception as e:
            print(f"Lỗi khi phiên âm đoạn audio: {e}")

    return all_results
