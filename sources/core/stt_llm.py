import json
import mimetypes
import os
import random
import string
import time
from io import BytesIO
from typing import Dict, List, Optional, Union

from google import genai
from magic import Magic

from .api_key import *

# Khởi tạo với mime=True để lấy MIME type thay vì mô tả
magic = Magic(mime=True)

# Đảm bảo mimetypes được khởi tạo
mimetypes.init()

# Danh sách API key - sử dụng tất cả API keys có sẵn
API_KEYS = [API_KEY1, API_KEY2]
current_key_index = 0  # Bắt đầu với API_KEY1

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
        "text": "The plain text transcription that accurately reflects the content of the audio. Each item should be one sentence, transcribed exactly as spoken in the audio.",
        "description": "Provide a detailed description of the speaker's voice characteristics, including gender, tone, emotion, pronunciation, and speaking style. For example: A female speaker delivers a slightly expressive and animated speech with a very high-pitched voice, sounding very close-up in the recording. Almost no noise is present in the background, contributing to a clear and crisp listening experience. Each description must be distinct and not repeated across different entries."
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


def get_normalized_mime_type(file_data: bytes, filename: str) -> str:
    """
    Xác định MIME type chuẩn cho file audio.

    Args:
        file_data: Nội dung file dưới dạng bytes
        filename: Tên file

    Returns:
        str: MIME type chuẩn
    """
    # Sử dụng python-magic để lấy MIME type từ nội dung file
    magic_mime = magic.from_buffer(file_data)

    # Sử dụng mimetypes để lấy MIME type từ tên file
    filename_mime, _ = mimetypes.guess_type(filename)

    print(f"MIME từ magic: {magic_mime}, MIME từ tên file: {filename_mime}")

    # Ánh xạ MIME types phổ biến sang dạng chuẩn
    mime_mapping = {
        "audio/x-wav": "audio/wav",
        "audio/x-mp3": "audio/mpeg",
        "audio/mp3": "audio/mpeg",
        "application/octet-stream": None,  # Sẽ dựa vào filename_mime
    }

    # Ưu tiên sử dụng magic_mime nếu nó là audio/*
    if magic_mime and magic_mime.startswith("audio/"):
        return mime_mapping.get(magic_mime, magic_mime)

    # Nếu magic_mime không phải audio/*, thử dùng filename_mime
    if filename_mime and filename_mime.startswith("audio/"):
        return filename_mime

    # Fallback: dựa vào phần mở rộng file
    if filename.lower().endswith(".wav"):
        return "audio/wav"
    elif filename.lower().endswith((".mp3", ".mpeg")):
        return "audio/mpeg"
    elif filename.lower().endswith(".ogg"):
        return "audio/ogg"
    elif filename.lower().endswith(".flac"):
        return "audio/flac"

    # Nếu không xác định được, trả về magic_mime mặc định
    return magic_mime


def transcript_audio(
    file: Union[str, BytesIO],
    max_retries: int = 5,
    model: str = "gemini-2.0-flash",
) -> List[Dict[str, str]]:
    """
    Phiên âm nội dung của file audio sử dụng Google Gemini API.

    Args:
        file: Đường dẫn đến file audio hoặc BytesIO object
        max_retries: Số lần thử lại tối đa khi gặp lỗi
        model: Model AI sử dụng (mặc định: gemini-2.0-flash)

    Returns:
        List[Dict[str, str]]: Kết quả phiên âm dưới dạng JSON

    Raises:
        ValueError: Nếu loại file không được hỗ trợ
        RuntimeError: Nếu không thể phiên âm sau số lần thử lại tối đa
    """
    # Biến để theo dõi file đã upload
    uploaded_file = None

    # Tạo một bản sao của file để không ảnh hưởng đến đối tượng gốc
    if isinstance(file, BytesIO):
        # Tạo bản sao an toàn của BytesIO
        file.seek(0)
        file_copy = BytesIO(file.getvalue())
        # Reset con trỏ về đầu trên cả file gốc và bản sao
        file.seek(0)  # Reset file gốc về đầu cho các xử lý khác
        file = file_copy  # Sử dụng bản sao cho xử lý của chúng ta

    try:
        # Xử lý file input và chuẩn bị config
        if isinstance(file, str):
            with open(file, "rb") as f:
                file_data = f.read()
            filename = os.path.basename(file)
            file_source = file  # Lưu đường dẫn gốc
        elif isinstance(file, BytesIO):
            # BytesIO đã được reset về đầu khi tạo bản sao
            file_data = file.getvalue()

            # Xác định tên file
            if hasattr(file, "name") and file.name:
                filename = os.path.basename(file.name)
            else:
                filename = f"audio_{generate_random_string()}.wav"

            file_source = file  # File source là bản sao BytesIO
        else:
            raise ValueError("Định dạng file không được hỗ trợ")

        # Xác định MIME type chuẩn hóa
        mime_type = get_normalized_mime_type(file_data, filename)
        config = {"mime_type": mime_type}
        print(f"Sử dụng MIME type: {mime_type} cho file {filename}")

        # Thử upload và xử lý với retry
        for attempt in range(max_retries):
            try:
                # Xóa file đã upload từ lần trước nếu có
                if uploaded_file:
                    try:
                        client.files.delete(name=uploaded_file.name)
                        print(f"Đã xóa file tạm trước đó: {uploaded_file.name}")
                    except Exception as e:
                        print(f"Không thể xóa file tạm: {str(e)}")

                # Reset file về đầu trước khi upload
                if isinstance(file_source, BytesIO) and hasattr(file_source, "seek"):
                    file_source.seek(0)

                # Upload file
                uploaded_file = client.files.upload(file=file_source, config=config)
                print(f"Đã upload file {filename} với ID: {uploaded_file.name}")

                # Gọi API Gemini
                response = client.models.generate_content(
                    model=model,
                    contents=[prompt, uploaded_file],
                )

                # Lấy text từ response
                response_text = response.text

                # Phân tích kết quả JSON
                results = parse_response(response_text)

                print(f"Phiên âm thành công file {filename}: {len(results)} kết quả")
                return results

            except Exception as e:
                error_message = str(e).lower()
                last_attempt = attempt == max_retries - 1

                # Kiểm tra các loại lỗi khác nhau
                if "rate limit" in error_message or "quota" in error_message:
                    # Xử lý rate limit bằng cách đổi API key
                    print(
                        f"Gặp lỗi rate limit, đang thử lại ({attempt+1}/{max_retries})..."
                    )
                    change_api_key()
                    time.sleep(1)  # Chờ 1 giây trước khi thử lại
                elif (
                    "overloaded" in error_message
                    or "unavailable" in error_message
                    or "busy" in error_message
                ):
                    # Xử lý model overloaded bằng cách chờ lâu hơn
                    wait_time = min(
                        30, 2**attempt + 1
                    )  # Tăng thời gian chờ theo cấp số nhân, tối đa 30s
                    print(
                        f"Model đang quá tải, chờ {wait_time}s trước khi thử lại ({attempt+1}/{max_retries})..."
                    )
                    time.sleep(wait_time)

                    # Nếu là lần cuối và model vẫn overloaded, thử model không có hậu tố lite
                    if last_attempt and "-lite" in model:
                        non_lite_model = model.replace("-lite", "")
                        print(f"Thử với model không lite: {non_lite_model}")
                        try:
                            response = client.models.generate_content(
                                model=non_lite_model,
                                contents=[prompt, uploaded_file],
                            )
                            response_text = response.text
                            results = parse_response(response_text)
                            print(f"Phiên âm thành công với model {non_lite_model}")
                            return results
                        except Exception as model_e:
                            print(
                                f"Không thành công với model {non_lite_model}: {model_e}"
                            )

                    if last_attempt:
                        print("Cố gắng thêm lần cuối với thời gian chờ dài hơn...")
                        time.sleep(10)  # Chờ thêm 10 giây
                        max_retries += 1  # Thêm một lần thử nữa

                elif not last_attempt:  # Nếu còn lần thử khác
                    # Lỗi khác nhưng vẫn còn cơ hội thử lại
                    wait_time = 2 * (attempt + 1)
                    print(f"Lỗi khi gọi API: {e}. Thử lại sau {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    # Lỗi khác và đã hết lần thử
                    print(f"Lỗi khi gọi API: {e}")
                    raise

        # Nếu đã thử tất cả các lần mà vẫn không thành công
        raise RuntimeError(f"Không thể phiên âm sau {max_retries} lần thử lại")

    finally:
        # Xóa các file đã upload để giải phóng tài nguyên
        try:
            # Xóa theo tên file đã biết
            if uploaded_file and hasattr(uploaded_file, "name"):
                try:
                    print(f"Xóa file đã upload: {uploaded_file.name}")
                    client.files.delete(name=uploaded_file.name)
                except Exception as e:
                    print(f"Lỗi khi xóa file đã upload: {e}")

            # Xóa thêm các file khác có thể còn sót lại
            try:
                for f in client.files.list():
                    if hasattr(f, "name"):
                        print(f"Xóa file sót: {f.name}")
                        client.files.delete(name=f.name)
            except Exception as e:
                print(f"Lỗi khi liệt kê/xóa files sót: {e}")
        except Exception as e:
            print(f"Lỗi tổng thể khi xóa files đã upload: {e}")
