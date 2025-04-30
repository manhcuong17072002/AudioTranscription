import os
import random
import string
from io import BytesIO
from tempfile import NamedTemporaryFile
from typing import Dict, List, Optional, Tuple, Union

import stable_whisper
from stable_whisper.result import WhisperResult
from pydub import AudioSegment

model = stable_whisper.load_model("large-v3", device="cpu")


def get_audio_chunks(
    text: Union[str, list[str]],
    audio_file: Union[str, BytesIO, bytes],
    save_folder: Optional[str] = None,
    leading_silence_ms: int = 0,
    trailing_silence_ms: int = 0,
) -> List[Dict]:
    """
    Align text với audio, cắt audio thành các đoạn theo timestamp từ file SRT.

    Args:
        text: Văn bản cần align với audio, có thể là string hoặc list of strings
        audio_file: File audio, có thể là đường dẫn, BytesIO hoặc bytes
        save_folder: Thư mục để lưu các đoạn audio và text, nếu None thì không lưu
        leading_silence_ms: Khoảng lặng (ms) thêm vào đầu mỗi audio chunk, mặc định là 0
        trailing_silence_ms: Khoảng lặng (ms) thêm vào cuối mỗi audio chunk, mặc định là 0

    Returns:
        Nếu save_folder là None: Danh sách các dictionary chứa {"audio": AudioSegment, "text": str, "filename": str}
        Nếu save_folder được cung cấp: Danh sách các dictionary chứa {"filename": str, "text": str, "full_path": str}
    """
    if isinstance(text, list):
        text = "\n".join(text)

    if isinstance(audio_file, BytesIO):
        audio_file = audio_file.read()

    # Align text với audio sử dụng stable_whisper
    result: WhisperResult = model.align(
        audio_file, text, language="vi", original_split=True
    )

    # Load file audio gốc
    audio = load_audio(audio_file)

    # Tạo khoảng lặng để sử dụng nếu cần
    silence = AudioSegment.silent(duration=1)  # 1ms silence để nhân bản

    # Cắt audio theo timestamps từ segments
    audio_chunks = []
    for segment in result.segments:
        # Lấy timestamp (đã là milliseconds) và text từ segment
        start_time_ms = int(segment.start * 1000)  # Chuyển từ giây sang milliseconds
        end_time_ms = int(segment.end * 1000)  # Chuyển từ giây sang milliseconds
        subtitle = segment.text.strip()

        # Cắt audio theo timestamps
        chunk = audio[start_time_ms:end_time_ms]

        # Thêm khoảng lặng nếu cần
        if leading_silence_ms > 0:
            leading_silence = silence * leading_silence_ms
            chunk = leading_silence + chunk

        if trailing_silence_ms > 0:
            trailing_silence = silence * trailing_silence_ms
            chunk = chunk + trailing_silence

        # Tạo tên file ngẫu nhiên cho mỗi chunk
        random_name = "".join(
            random.choices(string.ascii_lowercase + string.digits, k=10)
        )
        filename = f"{random_name}.wav"

        audio_chunks.append({"audio": chunk, "text": subtitle, "filename": filename})

    # Xử lý output tùy thuộc vào save_folder
    if save_folder:
        # Tạo thư mục nếu chưa tồn tại
        os.makedirs(save_folder, exist_ok=True)

        saved_files = []

        # Lưu từng đoạn audio và text
        for chunk_data in audio_chunks:
            chunk = chunk_data["audio"]
            subtitle = chunk_data["text"]
            filename = chunk_data["filename"]

            # Lưu file audio
            audio_path = os.path.join(save_folder, filename)
            chunk.export(audio_path, format="wav")

            # Lưu file text
            text_name = filename.replace(".wav", ".txt")
            text_path = os.path.join(save_folder, text_name)
            with open(text_path, "w", encoding="utf-8") as f:
                f.write(subtitle)

            # Thêm thông tin vào kết quả
            saved_files.append(
                {"filename": filename, "text": subtitle, "full_path": audio_path}
            )

        return saved_files
    else:
        # Trả về danh sách các dictionary chứa audio, text và filename
        return audio_chunks


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
