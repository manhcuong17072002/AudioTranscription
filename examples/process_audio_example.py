import os
import sys
import json
from typing import List, Dict

# Thêm thư mục gốc vào sys.path để import module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import các module đã tạo
from sources.core.audio_understanding import transcript_audios, transcript_split_audio
from sources.core.split_audio import process_audio_file

def process_single_audio(audio_path: str, output_json: str = None) -> List[Dict[str, str]]:
    """
    Xử lý một file audio: phiên âm và trả về kết quả JSON.
    
    Args:
        audio_path: Đường dẫn đến file audio
        output_json: Đường dẫn để lưu kết quả JSON (tuỳ chọn)
        
    Returns:
        List[Dict[str, str]]: Kết quả phiên âm dưới dạng JSON
    """
    print(f"Đang xử lý file: {audio_path}")
    
    # Phiên âm trực tiếp
    try:
        results = transcript_audios(audio_path)
        
        # Lưu kết quả vào file nếu cần
        if output_json:
            with open(output_json, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print(f"Đã lưu kết quả vào: {output_json}")
            
        return results
        
    except Exception as e:
        print(f"Lỗi khi phiên âm file {audio_path}: {e}")
        return []

def process_long_audio(
    audio_path: str, 
    output_json: str = None,
    min_silence_len: int = 500,
    silence_thresh: int = -40,
    max_segment_length: int = 30000
) -> List[Dict[str, str]]:
    """
    Xử lý file audio dài: cắt theo khoảng lặng, phiên âm từng đoạn và tổng hợp kết quả.
    
    Args:
        audio_path: Đường dẫn đến file audio
        output_json: Đường dẫn để lưu kết quả JSON (tuỳ chọn)
        min_silence_len: Độ dài tối thiểu của khoảng lặng (ms)
        silence_thresh: Ngưỡng âm lượng để xác định khoảng lặng (dB)
        max_segment_length: Độ dài tối đa của mỗi đoạn audio (ms)
        
    Returns:
        List[Dict[str, str]]: Kết quả phiên âm tổng hợp dưới dạng JSON
    """
    print(f"Đang xử lý file dài: {audio_path}")
    
    # Cắt file audio thành các đoạn
    audio_chunks = process_audio_file(
        audio_path,
        min_silence_len=min_silence_len,
        silence_thresh=silence_thresh,
        max_segment_length=max_segment_length,
        save_to_disk=False
    )
    
    print(f"Đã cắt thành {len(audio_chunks)} đoạn audio")
    
    # Phiên âm tất cả các đoạn
    try:
        results = transcript_split_audio(audio_chunks)
        
        # Lưu kết quả vào file nếu cần
        if output_json:
            with open(output_json, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print(f"Đã lưu kết quả vào: {output_json}")
            
        return results
        
    except Exception as e:
        print(f"Lỗi khi phiên âm các đoạn audio: {e}")
        return []

def process_multiple_audio(audio_paths: List[str], output_dir: str = None) -> Dict[str, List[Dict[str, str]]]:
    """
    Xử lý nhiều file audio cùng lúc.
    
    Args:
        audio_paths: Danh sách đường dẫn đến các file audio
        output_dir: Thư mục để lưu kết quả JSON (tuỳ chọn)
        
    Returns:
        Dict[str, List[Dict[str, str]]]: Dictionary với key là tên file và value là kết quả phiên âm
    """
    results = {}
    
    for audio_path in audio_paths:
        filename = os.path.basename(audio_path)
        output_json = None
        
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            output_json = os.path.join(output_dir, f"{os.path.splitext(filename)[0]}.json")
            
        # Kiểm tra kích thước file để quyết định cách xử lý
        file_size = os.path.getsize(audio_path)
        
        # Nếu file lớn hơn 2MB, xử lý như file dài
        if file_size > 2 * 1024 * 1024:  # 2MB
            result = process_long_audio(audio_path, output_json)
        else:
            result = process_single_audio(audio_path, output_json)
            
        results[filename] = result
        
    return results

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Audio Transcription Tool")
    parser.add_argument("audio_files", nargs="+", help="Đường dẫn đến file audio cần phiên âm")
    parser.add_argument("--output", "-o", help="Thư mục đầu ra cho kết quả JSON")
    parser.add_argument("--silence-len", type=int, default=500, help="Độ dài tối thiểu của khoảng lặng (ms)")
    parser.add_argument("--silence-thresh", type=int, default=-40, help="Ngưỡng âm lượng để xác định khoảng lặng (dB)")
    parser.add_argument("--segment-length", type=int, default=30000, help="Độ dài tối đa của mỗi đoạn audio (ms)")
    
    args = parser.parse_args()
    
    results = process_multiple_audio(args.audio_files, args.output)
    
    # In tổng quan kết quả
    print("\nKết quả phiên âm:")
    for filename, result in results.items():
        print(f"- {filename}: {len(result)} đoạn")
