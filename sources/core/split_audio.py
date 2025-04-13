from io import BytesIO
from typing import List, Tuple, Union, Optional
import os
import tempfile

from pydub import AudioSegment
from pydub.silence import split_on_silence, detect_silence

def detect_silence_intervals(
    audio_file: Union[str, BytesIO],
    min_silence_len: int = 500,  # ms
    silence_thresh: int = -40,   # dB
    keep_silence: int = 150      # ms
) -> List[Tuple[int, int]]:
    """
    Phát hiện các khoảng lặng trong file audio.
    
    Args:
        audio_file: Đường dẫn đến file audio hoặc BytesIO object
        min_silence_len: Độ dài tối thiểu của khoảng lặng (ms)
        silence_thresh: Ngưỡng âm lượng để xác định khoảng lặng (dB)
        keep_silence: Giữ lại bao nhiêu khoảng lặng ở đầu và cuối mỗi đoạn (ms)
        
    Returns:
        List[Tuple[int, int]]: Danh sách các khoảng lặng dưới dạng (start_ms, end_ms)
    """
    # Xử lý đầu vào
    if isinstance(audio_file, str):
        audio = AudioSegment.from_file(audio_file)
    elif isinstance(audio_file, BytesIO):
        audio = AudioSegment.from_file(audio_file)
    else:
        raise ValueError("Unsupported audio file type")

    # Phát hiện khoảng lặng
    silence_intervals = detect_silence(
        audio,
        min_silence_len=min_silence_len,
        silence_thresh=silence_thresh
    )
    
    return silence_intervals

def split_audio_on_silence(
    audio_file: Union[str, BytesIO],
    min_silence_len: int = 500,  # ms
    silence_thresh: int = -40,   # dB
    keep_silence: int = 150,     # ms
    min_segment_length: int = 2000,  # ms
    max_segment_length: Optional[int] = 10  # ms, None = không giới hạn
) -> List[BytesIO]:
    """
    Cắt file audio thành nhiều đoạn dựa trên khoảng lặng.
    
    Args:
        audio_file: Đường dẫn đến file audio hoặc BytesIO object
        min_silence_len: Độ dài tối thiểu của khoảng lặng (ms)
        silence_thresh: Ngưỡng âm lượng để xác định khoảng lặng (dB)
        keep_silence: Giữ lại bao nhiêu khoảng lặng ở đầu và cuối mỗi đoạn (ms)
        min_segment_length: Độ dài tối thiểu của mỗi đoạn audio (ms)
        max_segment_length: Độ dài tối đa của mỗi đoạn audio (ms), None = không giới hạn
        
    Returns:
        List[BytesIO]: Danh sách các đoạn audio đã được cắt
    """
    # Xử lý đầu vào
    if isinstance(audio_file, str):
        audio = AudioSegment.from_file(audio_file)
    elif isinstance(audio_file, BytesIO):
        audio = AudioSegment.from_file(audio_file)
    else:
        raise ValueError("Unsupported audio file type")
    
    # Cắt audio dựa trên khoảng lặng
    chunks = split_on_silence(
        audio,
        min_silence_len=min_silence_len,
        silence_thresh=silence_thresh,
        keep_silence=keep_silence
    )
    
    processed_chunks = []
    current_chunk = None
    current_duration = 0
    
    for chunk in chunks:
        # Bỏ qua các đoạn quá ngắn
        if len(chunk) < min_segment_length:
            continue
            
        # Nếu chưa có đoạn hiện tại hoặc đoạn hiện tại đủ dài
        if current_chunk is None or (max_segment_length and current_duration + len(chunk) > max_segment_length):
            # Lưu đoạn hiện tại (nếu có) vào danh sách
            if current_chunk is not None and current_duration >= min_segment_length:
                output = BytesIO()
                current_chunk.export(output, format="wav")
                output.seek(0)
                processed_chunks.append(output)
                
            # Bắt đầu đoạn mới
            current_chunk = chunk
            current_duration = len(chunk)
        else:
            # Nối với đoạn hiện tại
            current_chunk += chunk
            current_duration += len(chunk)
    
    # Xử lý đoạn cuối cùng
    if current_chunk is not None and current_duration >= min_segment_length:
        output = BytesIO()
        current_chunk.export(output, format="wav")
        output.seek(0)
        processed_chunks.append(output)
    
    return processed_chunks

def save_audio_chunks(chunks: List[BytesIO], output_dir: str, prefix: str = "chunk") -> List[str]:
    """
    Lưu các đoạn audio đã cắt vào thư mục.
    
    Args:
        chunks: Danh sách các đoạn audio (BytesIO)
        output_dir: Thư mục đầu ra
        prefix: Tiền tố cho tên file
        
    Returns:
        List[str]: Danh sách đường dẫn đến các file đã lưu
    """
    # Tạo thư mục nếu chưa tồn tại
    os.makedirs(output_dir, exist_ok=True)
    
    saved_paths = []
    
    for i, chunk in enumerate(chunks):
        # Đặt lại con trỏ đọc
        chunk.seek(0)
        
        # Tạo đường dẫn đầu ra
        output_path = os.path.join(output_dir, f"{prefix}_{i+1}.wav")
        
        # Lưu file
        with open(output_path, 'wb') as f:
            f.write(chunk.getvalue())
            
        saved_paths.append(output_path)
        
        # Đặt lại con trỏ đọc để có thể sử dụng lại
        chunk.seek(0)
        
    return saved_paths

def process_audio_file(
    audio_file: Union[str, BytesIO],
    min_silence_len: int = 500,  # ms
    silence_thresh: int = -40,   # dB
    keep_silence: int = 100,     # ms
    min_segment_length: int = 2000,  # ms
    max_segment_length: Optional[int] = 30000,  # ms, ~30s
    save_to_disk: bool = False,
    output_dir: Optional[str] = None,
    file_prefix: str = "segment"
) -> Union[List[BytesIO], List[str]]:
    """
    Xử lý file audio: phát hiện và cắt theo khoảng lặng.
    
    Args:
        audio_file: Đường dẫn đến file audio hoặc BytesIO object
        min_silence_len: Độ dài tối thiểu của khoảng lặng (ms)
        silence_thresh: Ngưỡng âm lượng để xác định khoảng lặng (dB)
        keep_silence: Giữ lại bao nhiêu khoảng lặng ở đầu và cuối mỗi đoạn (ms)
        min_segment_length: Độ dài tối thiểu của mỗi đoạn audio (ms)
        max_segment_length: Độ dài tối đa của mỗi đoạn audio (ms)
        save_to_disk: Có lưu các đoạn audio vào ổ đĩa không
        output_dir: Thư mục đầu ra (nếu save_to_disk=True)
        file_prefix: Tiền tố cho tên file (nếu save_to_disk=True)
        
    Returns:
        Union[List[BytesIO], List[str]]: 
            - Nếu save_to_disk=False: Danh sách các BytesIO objects
            - Nếu save_to_disk=True: Danh sách đường dẫn đến các file đã lưu
    """
    # Kiểm tra audio có cần cắt không (phát hiện khoảng lặng)
    silence_intervals = detect_silence_intervals(
        audio_file, 
        min_silence_len=min_silence_len,
        silence_thresh=silence_thresh,
        keep_silence=keep_silence
    )
    
    # Nếu không có khoảng lặng đủ dài hoặc chỉ có ít khoảng lặng
    if len(silence_intervals) <= 2:  # Chỉ có khoảng lặng đầu và cuối
        # Trả về nguyên file audio
        if isinstance(audio_file, str):
            if save_to_disk:
                return [audio_file]
            else:
                with open(audio_file, 'rb') as f:
                    data = f.read()
                    output = BytesIO(data)
                    return [output]
        else:
            audio_file.seek(0)
            return [audio_file]
    
    # Cắt audio thành các đoạn
    chunks = split_audio_on_silence(
        audio_file,
        min_silence_len=min_silence_len,
        silence_thresh=silence_thresh,
        keep_silence=keep_silence,
        min_segment_length=min_segment_length,
        max_segment_length=max_segment_length
    )
    
    # Nếu cần lưu vào ổ đĩa
    if save_to_disk:
        # Sử dụng thư mục tạm nếu không có thư mục đầu ra
        if not output_dir:
            output_dir = tempfile.mkdtemp()
            
        return save_audio_chunks(chunks, output_dir, file_prefix)
    
    return chunks
