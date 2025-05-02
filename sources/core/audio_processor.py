import json
import logging
import os
from io import BytesIO
from typing import Dict, List, Tuple, Union, Optional, Any

from pydub import AudioSegment

from .stt_llm import transcript_audio
from .text_aligner import get_audio_chunks

# Thiết lập logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def convert_to_mono(audio_file: Union[str, BytesIO]) -> BytesIO:
    """
    Chuyển đổi file audio sang mono channel nếu nó là stereo.
    
    Args:
        audio_file: Đường dẫn đến file audio hoặc BytesIO object
        
    Returns:
        BytesIO: Buffer chứa audio đã chuyển đổi sang mono
        
    Raises:
        ValueError: Nếu không thể đọc file audio
    """
    try:
        # Tải audio
        if isinstance(audio_file, BytesIO):
            # Đảm bảo con trỏ ở đầu file
            if hasattr(audio_file, 'seek'):
                audio_file.seek(0)
                
        audio: AudioSegment = AudioSegment.from_file(audio_file)
        
        # Kiểm tra nếu audio là stereo (2 channels) thì chuyển sang mono
        if audio.channels > 1:
            logger.info(f"Chuyển đổi audio từ {audio.channels} channels sang mono")
            audio = audio.set_channels(1)
        
        # Xuất audio sang BytesIO
        output_buffer = BytesIO()
        audio.export(output_buffer, format="wav")
        output_buffer.seek(0)
        
        return output_buffer
    except Exception as e:
        logger.error(f"Lỗi khi chuyển đổi audio sang mono: {str(e)}")
        raise ValueError(f"Không thể chuyển đổi audio sang mono: {str(e)}")

def transcribe_audio(
    audio_file: Union[str, BytesIO], 
    max_retries: int = 3,
    model: str = "gemini-2.0-flash"
) -> List[Dict[str, str]]:
    """
    Phiên âm nội dung của file audio sử dụng Google Gemini API.
    
    Args:
        audio_file: Đường dẫn đến file audio hoặc BytesIO object
        max_retries: Số lần thử lại tối đa khi gặp lỗi rate limit
        model: Model Gemini sử dụng cho transcription
        
    Returns:
        List[Dict[str, str]]: Danh sách kết quả phiên âm từ Gemini
        
    Raises:
        RuntimeError: Nếu không thể phiên âm sau số lần thử lại tối đa
    """
    try:
        logger.info("Bắt đầu phiên âm audio")
        transcription_results = transcript_audio(audio_file, max_retries, model)
        logger.info(f"Phiên âm thành công: nhận được {len(transcription_results)} kết quả")
        return transcription_results
    except Exception as e:
        logger.error(f"Lỗi khi phiên âm audio: {str(e)}")
        raise RuntimeError(f"Không thể phiên âm audio: {str(e)}")

def extract_transcript_text(transcription_results: List[Dict[str, str]]) -> str:
    """
    Trích xuất văn bản từ kết quả phiên âm.
    
    Args:
        transcription_results: Kết quả phiên âm từ hàm transcribe_audio
        
    Returns:
        str: Văn bản đã được trích xuất và ghép lại
    """
    transcript = []
    for result in transcription_results:
        if "text" in result:
            transcript.append(result["text"])
    
    transcript_text = "\n".join(transcript)
    logger.debug(f"Đã trích xuất văn bản: {len(transcript_text)} ký tự")
    return transcript_text

def align_audio_with_text(
    transcript_text: str,
    audio_file: Union[str, BytesIO],
    save_folder: Optional[str] = None,
    leading_silence_ms: int = 0,
    trailing_silence_ms: int = 0
) -> List[Dict]:
    """
    Căn chỉnh text với audio để tạo các đoạn audio.
    
    Args:
        transcript_text: Văn bản cần căn chỉnh
        audio_file: Đường dẫn đến file audio hoặc BytesIO object
        save_folder: Thư mục để lưu các đoạn audio và text
        leading_silence_ms: Khoảng lặng (ms) thêm vào đầu mỗi audio chunk
        trailing_silence_ms: Khoảng lặng (ms) thêm vào cuối mỗi audio chunk
        
    Returns:
        List[Dict]: Danh sách các đoạn audio đã được cắt
        
    Raises:
        ValueError: Nếu không thể căn chỉnh text với audio
    """
    try:
        logger.info("Bắt đầu căn chỉnh text với audio")
        aligned_chunks = get_audio_chunks(
            text=transcript_text,
            audio_file=audio_file,
            save_folder=save_folder,
            leading_silence_ms=leading_silence_ms,
            trailing_silence_ms=trailing_silence_ms
        )
        logger.info(f"Căn chỉnh thành công: cắt được {len(aligned_chunks)} đoạn")
        return aligned_chunks
    except Exception as e:
        logger.error(f"Lỗi khi căn chỉnh text với audio: {str(e)}")
        raise ValueError(f"Không thể căn chỉnh text với audio: {str(e)}")

def combine_transcription_with_alignment(
    transcription_results: List[Dict[str, str]], 
    aligned_chunks: List[Dict]
) -> List[Dict[str, Any]]:
    """
    Kết hợp kết quả phiên âm với các đoạn audio đã cắt.
    
    Args:
        transcription_results: Kết quả phiên âm từ hàm transcribe_audio
        aligned_chunks: Các đoạn audio từ hàm align_audio_with_text
        
    Returns:
        List[Dict[str, Any]]: Danh sách kết quả đã được kết hợp
    """
    combined_results = []
    
    # Copy transcription_results để không làm thay đổi bản gốc
    combined_results = transcription_results.copy()
    
    # Đảm bảo số lượng phần tử trong hai danh sách là tương đương
    min_length = min(len(combined_results), len(aligned_chunks))
    
    if min_length != len(combined_results):
        logger.warning(f"Số lượng kết quả phiên âm ({len(combined_results)}) không khớp với số lượng đoạn audio ({len(aligned_chunks)})")
        
    # Kết hợp thông tin từ aligned_chunks vào combined_results
    for i in range(min_length):
        combined_results[i].update(aligned_chunks[i])
    
    logger.info(f"Kết hợp thành công kết quả phiên âm với {min_length} đoạn audio")
    return combined_results[:min_length]

def process_audio_with_alignment(
    audio_file: Union[str, BytesIO],
    leading_silence_ms: int = 0,
    trailing_silence_ms: int = 0,
    save_folder: Optional[str] = None,
    max_retries: int = 3,
    model: str = "gemini-2.0-flash"
) -> List[Dict[str, Any]]:
    """
    Xử lý file audio: phiên âm và căn chỉnh text-audio.
    
    Args:
        audio_file: Đường dẫn đến file audio hoặc BytesIO object
        leading_silence_ms: Khoảng lặng (ms) thêm vào đầu mỗi audio chunk
        trailing_silence_ms: Khoảng lặng (ms) thêm vào cuối mỗi audio chunk
        save_folder: Thư mục để lưu các đoạn audio và text, nếu None thì không lưu
        max_retries: Số lần thử lại tối đa khi gặp lỗi rate limit
        model: Model Gemini sử dụng cho transcription
        
    Returns:
        List[Dict[str, Any]]: Danh sách kết quả phiên âm đã được bổ sung thông tin audio
    
    Raises:
        ValueError: Nếu file audio không hợp lệ hoặc không thể căn chỉnh
        RuntimeError: Nếu không thể phiên âm sau số lần thử lại tối đa
    """
    # Kiểm tra đầu vào
    if not isinstance(audio_file, (str, BytesIO)):
        raise ValueError("audio_file phải là đường dẫn (str) hoặc BytesIO object")
        
    if save_folder is not None and not isinstance(save_folder, str):
        raise ValueError("save_folder phải là None hoặc string")
    
    # Tạo bản sao của BytesIO để tránh vấn đề con trỏ file
    if isinstance(audio_file, BytesIO):
        # Lưu lại nội dung bytes
        audio_file.seek(0)
        audio_bytes = audio_file.getvalue()
        # Tạo BytesIO mới để sử dụng trong quá trình xử lý
        audio_file_copy = BytesIO(audio_bytes)
        audio_file = audio_file_copy
    
    # Bước 0: Chuyển đổi audio sang mono nếu là stereo
    try:
        # Lưu giữ đường dẫn file nếu audio_file là string
        original_path = audio_file if isinstance(audio_file, str) else None
        
        # Chuyển đổi audio sang mono
        mono_audio = convert_to_mono(audio_file)
        
        # Nếu đầu vào là đường dẫn, cần duy trì thông tin đó cho các module khác
        if original_path:
            # Một số module có thể yêu cầu đường dẫn string, chúng ta ghi chú thông tin
            logger.info(f"Đã chuyển đổi file {original_path} sang mono")
            # Sử dụng mono_audio (BytesIO) cho các bước tiếp theo
            audio_file = mono_audio
        else:
            # Nếu đầu vào là BytesIO, thay thế nó bằng phiên bản mono
            audio_file = mono_audio
            
    except Exception as e:
        logger.warning(f"Không thể chuyển đổi audio sang mono: {str(e)}. Tiếp tục xử lý với định dạng ban đầu.")
        # Nếu không thể chuyển đổi, vẫn tiếp tục với file gốc
    
    # Bước 1: Phiên âm audio file
    logger.info("Bắt đầu xử lý audio")
    
    # Đảm bảo BytesIO ở đầu file trước khi phiên âm
    if isinstance(audio_file, BytesIO):
        audio_file.seek(0)
        logger.debug("Reset con trỏ BytesIO trước khi phiên âm")
        
    transcription_results = transcribe_audio(audio_file, max_retries, model)
    
    # Bước 2: Trích xuất transcript từ kết quả phiên âm
    transcript_text = extract_transcript_text(transcription_results)
    if not transcript_text:
        logger.warning("Không có văn bản được trích xuất từ kết quả phiên âm")
        return transcription_results
    
    # Đảm bảo BytesIO ở đầu file trước khi căn chỉnh
    if isinstance(audio_file, BytesIO):
        audio_file.seek(0)
        logger.debug("Reset con trỏ BytesIO trước khi căn chỉnh")
    
    # Bước 3: Căn chỉnh text với audio để tạo các đoạn audio
    aligned_chunks = align_audio_with_text(
        transcript_text=transcript_text,
        audio_file=audio_file,
        save_folder=save_folder,
        leading_silence_ms=leading_silence_ms,
        trailing_silence_ms=trailing_silence_ms
    )
    
    # Bước 4: Kết hợp kết quả phiên âm với thông tin audio chunk
    combined_results = combine_transcription_with_alignment(transcription_results, aligned_chunks)
    
    logger.info("Hoàn thành xử lý audio")
    return combined_results

def save_transcription_json(
    transcription_results: List[Dict[str, Any]], 
    output_path: str
) -> str:
    """
    Lưu kết quả phiên âm vào file JSON.
    
    Args:
        transcription_results: Kết quả phiên âm từ hàm process_audio_with_alignment
        output_path: Đường dẫn đến file JSON đầu ra
        
    Returns:
        str: Đường dẫn đến file JSON đã lưu
    
    Raises:
        IOError: Nếu không thể tạo thư mục hoặc ghi file
    """
    try:
        # Tạo thư mục chứa file nếu chưa tồn tại
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Lưu kết quả vào file JSON
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(transcription_results, f, ensure_ascii=False, indent=4)
        
        logger.info(f"Đã lưu kết quả phiên âm vào {output_path}")
        return output_path
    except Exception as e:
        logger.error(f"Lỗi khi lưu kết quả phiên âm: {str(e)}")
        raise IOError(f"Không thể lưu kết quả phiên âm: {str(e)}")
