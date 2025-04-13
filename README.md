# Kế hoạch đã hoàn thành

1. audio_understanding.py
- ✅ Sử dụng Gemini API để transcript nội dung của audio và trả dưới dạng json
- ✅ Cho phép thay đổi api key nếu bị lỗi rate limit 
- ✅ Cho phép đẩy nhiều file vào cùng một lúc để transcript

2. split_audio.py
- ✅ Cho phép cắt audio theo từng khoảng lặng nếu audio quá dài 
- ✅ Tích hợp vào audio_understanding.py

# Hướng dẫn sử dụng

## Cài đặt

```bash
pip install -r requirements.txt
```

## Phiên âm file audio đơn giản

```python
from sources.core.audio_understanding import transcript_audios

# Phiên âm một file
results = transcript_audios("path/to/audio.wav")

# Phiên âm nhiều file
results = transcript_audios(["path/to/audio1.wav", "path/to/audio2.wav"])

# Kết quả trả về dưới dạng JSON
print(results)
```

## Xử lý file audio dài

```python
from sources.core.audio_understanding import transcript_split_audio
from sources.core.split_audio import process_audio_file

# Cắt file audio thành các đoạn
audio_chunks = process_audio_file(
    "path/to/long_audio.wav",
    min_silence_len=500,  # Độ dài tối thiểu của khoảng lặng (ms)
    silence_thresh=-40,   # Ngưỡng âm lượng (dB)
    max_segment_length=30000  # Độ dài tối đa của mỗi đoạn (30s)
)

# Phiên âm các đoạn audio
results = transcript_split_audio(audio_chunks)
```

## Sử dụng script mẫu

Chúng tôi đã cung cấp một script mẫu `examples/process_audio_example.py` cho phép phiên âm file audio từ command line:

```bash
python examples/process_audio_example.py path/to/audio.wav --output output_dir
```

Thêm nhiều file để xử lý cùng lúc:

```bash
python examples/process_audio_example.py file1.wav file2.wav file3.wav --output output_dir
```

Tùy chỉnh các tham số cắt audio:

```bash
python examples/process_audio_example.py long_audio.wav --silence-len 700 --silence-thresh -45 --segment-length 20000
```

# Kế hoạch tiếp theo
1. Xây dựng trang demo cho phép liên kết với python có các chức năng: 
- Cho người dùng đẩy file vào để transcript và tải về file json
- Hiển thị từng đoạn audio ra, thêm toggle cho phép người dùng có muốn cắt audio đó hay không
- Nếu muốn cho người khác dùng, hãy cho phép tạo account và nhập nhiều api key vào để có thể thay đổi nếu bị rate limit (tài khoản admin thì không cần nhập) 

2. Viết api.
3. Triển khai.
