# Bối cảnh công nghệ

## Công nghệ sử dụng

### Ngôn ngữ lập trình
- **Python**: Ngôn ngữ chính cho toàn bộ dự án.
  - Phiên bản: Python 3.10+ (theo setup.py)
  - Ưu điểm: Đơn giản, có nhiều thư viện hỗ trợ xử lý audio và tích hợp API

### API và dịch vụ
- **Google Gemini API**: Sử dụng để transcribe audio và phân tích giọng nói
  - Model: gemini-2.0-flash
  - Hạn chế: Rate limits và chi phí sử dụng

### Thư viện chính
- **google-genai**: Thư viện Python chính thức để tương tác với Google Gemini API
- **pydub**: Thư viện xử lý audio, hỗ trợ cắt và phân tích file âm thanh
- **python-magic**: Thư viện để xác định MIME type của file
- **stable-ts (Stable Whisper)**: Thư viện cho text-audio alignment
- **torch**: Framework deep learning để chạy mô hình Whisper
- **BytesIO** (từ thư viện chuẩn io): Xử lý dữ liệu dạng binary trong bộ nhớ
- **streamlit**: Framework để xây dựng giao diện web
- **plotly**: Thư viện tạo đồ thị và visualization

### Định dạng dữ liệu
- **JSON**: Sử dụng để định dạng kết quả trả về từ transcription
- **WAV**: Định dạng audio được sử dụng trong các file mẫu và chủ yếu để xử lý
- **MP3**: Định dạng audio được hỗ trợ

## Thiết lập phát triển

### Môi trường phát triển
- **Jupyter Notebook**: Sử dụng để thử nghiệm và phát triển (test.ipynb)
- **Visual Studio Code**: IDE cho phát triển chính
- **Streamlit**: Framework phát triển web app và giao diện người dùng

### Quản lý dependency
- **setup.py**: Cấu hình package và dependency
  ```python
  install_requires=[
      "google-genai",
      "pydub",
      "python-magic",
      "stable-ts",
      "torch"
  ],
  extras_require={
      "demo": [
          "streamlit",
          "plotly"
      ],
  }
  ```
- **requirements.txt**: Danh sách các thư viện cần thiết cho phát triển

### Cấu trúc mã nguồn
```
/AudioTranscription/
  ├── gemini_audio_transcription/     # Thư viện chính
  │   ├── __init__.py
  │   ├── transcriber.py       # Xử lý transcription với Gemini API
  │   ├── processor.py         # Kết hợp transcription và alignment
  │   ├── aligner.py           # Text-audio alignment
  │   └── api_key_example.py   # Mẫu quản lý API key
  │
  ├── demo/                    # Ứng dụng demo với Streamlit
  │   ├── Homepage.py          # Trang chính
  │   ├── pages/               # Các trang phụ
  │   │   ├── 01_TTS_Labeling.py
  │   │   └── 02_Transcript_view.py
  │   └── utils/               # Utilities cho demo
  │       ├── cache_utils.py
  │       ├── custom_styles.py
  │       ├── display_utils.py
  │       ├── zip_utils.py
  │       └── constants.py
  │
  ├── samples/                 # File audio mẫu
  │   ├── 3.6.wav
  │   ├── 10.1.wav
  │   ├── NHLy.wav
  │   ├── NDSon.wav
  │   └── vtv.mp3
  │
  ├── memory-bank/             # Tài liệu dự án
  ├── setup.py                 # Cấu hình package
  ├── requirements.txt         # Danh sách dependency
  ├── test.ipynb               # Notebook thử nghiệm
  └── README.md                # Thông tin dự án
```

## Ràng buộc kỹ thuật

### Giới hạn API
- **Rate Limit**: Google Gemini API có giới hạn số lượng yêu cầu trong một khoảng thời gian
- **Upload Size**: Giới hạn kích thước file có thể upload lên API
- **Pricing**: Chi phí sử dụng API dựa trên số token và loại model
- **File Cleanup**: Cần xóa các file đã upload sau khi xử lý để tránh tích tụ dữ liệu

### Xử lý file âm thanh
- **Kích thước file**: File âm thanh lớn cần được xử lý và cắt phù hợp
- **Định dạng hỗ trợ**: Hiện đã hỗ trợ WAV và MP3, với khả năng mở rộng cho các định dạng khác
- **Chất lượng âm thanh**: Ảnh hưởng đến độ chính xác của transcription
- **Stereo vs Mono**: Cần xử lý chuyển đổi từ stereo sang mono trước khi phân tích

### Mạng và kết nối
- **Độ tin cậy**: Phụ thuộc vào kết nối internet để gọi API
- **Timeout**: Đã triển khai retry mechanism với exponential backoff để xử lý timeout
- **API Fallback**: Chuyển đổi giữa các model khác nhau khi gặp lỗi

## Dependency và tích hợp

### Dependency trực tiếp
- **Google Gemini API**: Phụ thuộc chính cho transcription và phân tích giọng nói
- **Stable Whisper**: Phụ thuộc chính cho text-audio alignment
- **pydub**: Xử lý và phân tích âm thanh
- **torch**: Yêu cầu để chạy mô hình Whisper
- **FFmpeg**: Cần thiết để pydub xử lý các định dạng audio
- **streamlit**: Framework web UI
- **plotly**: Visualization và đồ thị cho giao diện người dùng

### Tích hợp hiện tại
- **Frontend Web**: Đã triển khai giao diện web với Streamlit
- **Session Management**: Quản lý phiên làm việc và cache trong Streamlit
- **Audio Player**: Tích hợp trình phát audio cho từng phân đoạn
- **ZIP Export**: Xuất kết quả dạng ZIP bao gồm audio và text

### Tích hợp tương lai
- **Database**: Lưu trữ thông tin người dùng, API key và kết quả transcription
- **Authentication System**: Quản lý người dùng và phân quyền
- **RESTful API**: Cung cấp dịch vụ transcription thông qua API
- **Containerization**: Đóng gói ứng dụng với Docker

## Khả năng mở rộng
- **Horizontal Scaling**: Khả năng xử lý nhiều yêu cầu đồng thời
- **Multi-model Support**: Đã hỗ trợ lựa chọn giữa các model Gemini khác nhau
- **Multi-language Support**: Đã chuẩn bị cơ sở để hỗ trợ nhiều ngôn ngữ
- **Hardware Acceleration**: Hỗ trợ xử lý alignment trên CPU, CUDA (GPU) hoặc MPS (Apple Silicon)
- **Caching System**: Đã triển khai hệ thống cache để tối ưu hóa hiệu suất

## Các kế hoạch kỹ thuật tương lai
- **Containerization**: Đóng gói ứng dụng trong Docker để dễ dàng triển khai
- **CI/CD Pipeline**: Thiết lập quy trình tích hợp và triển khai liên tục
- **Multi-worker Processing**: Triển khai xử lý song song cho nhiều file audio
- **Monitoring**: Theo dõi hiệu suất và sử dụng tài nguyên của hệ thống
- **Testing Framework**: Phát triển bộ test tự động để đảm bảo chất lượng
- **API Documentation**: Sử dụng Swagger/OpenAPI để tài liệu hóa API
