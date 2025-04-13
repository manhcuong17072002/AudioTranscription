# Bối cảnh công nghệ

## Công nghệ sử dụng

### Ngôn ngữ lập trình
- **Python**: Ngôn ngữ chính cho toàn bộ dự án.
  - Phiên bản: *chưa xác định*
  - Ưu điểm: Đơn giản, có nhiều thư viện hỗ trợ xử lý audio và tích hợp API

### API và dịch vụ
- **Google Gemini API**: Sử dụng để transcribe audio và phân tích giọng nói
  - Model: gemini-2.0-flash
  - Hạn chế: Rate limits và chi phí sử dụng

### Thư viện chính
- **google-genai**: Thư viện Python chính thức để tương tác với Google Gemini API
- **pydub**: Thư viện xử lý audio, hỗ trợ cắt và phân tích file âm thanh
- **python-magic**: Thư viện để xác định MIME type của file
- **BytesIO** (từ thư viện chuẩn io): Xử lý dữ liệu dạng binary trong bộ nhớ

### Định dạng dữ liệu
- **JSON**: Sử dụng để định dạng kết quả trả về từ transcription
- **WAV**: Định dạng audio được sử dụng trong các file mẫu và có thể được xử lý

## Thiết lập phát triển

### Môi trường phát triển
- **Jupyter Notebook**: Sử dụng để thử nghiệm và phát triển (test.ipynb)
- **Visual Studio Code**: IDE cho phát triển chính

### Quản lý dependency
- **requirements.txt**: Danh sách các thư viện cần thiết cho dự án
  ```
  google-genai
  pydub
  python-magic
  ```

### Cấu trúc mã nguồn
```
/AudioTranscription/
  ├── audio_understanding.py  # Xử lý transcription với Gemini API
  ├── split_audio.py          # Cắt file audio dựa trên khoảng lặng
  ├── api_key.py              # Quản lý API key
  ├── test.ipynb              # Notebook thử nghiệm
  ├── requirements.txt        # Danh sách dependency
  ├── docs.md                 # Tài liệu về Gemini API
  ├── README.md               # Thông tin dự án
  └── [các file .wav]         # File audio mẫu cho testing
```

## Ràng buộc kỹ thuật

### Giới hạn API
- **Rate Limit**: Google Gemini API có giới hạn số lượng yêu cầu trong một khoảng thời gian
- **Upload Size**: Giới hạn kích thước file có thể upload lên API
- **Pricing**: Chi phí sử dụng API dựa trên số token và loại model

### Xử lý file âm thanh
- **Kích thước file**: File âm thanh lớn cần được cắt thành nhiều phần nhỏ
- **Định dạng hỗ trợ**: Cần xác định các định dạng âm thanh được hỗ trợ bởi cả hệ thống và API
- **Chất lượng âm thanh**: Ảnh hưởng đến độ chính xác của transcription

### Mạng và kết nối
- **Độ tin cậy**: Phụ thuộc vào kết nối internet để gọi API
- **Timeout**: Xử lý trường hợp API phản hồi chậm hoặc không phản hồi

## Dependency và tích hợp

### Dependency trực tiếp
- **Google Gemini API**: Phụ thuộc chính của hệ thống
- **pydub**: Xử lý và phân tích âm thanh
- **FFmpeg**: Có thể cần thiết để pydub hoạt động với một số định dạng audio (chưa xác định)

### Tích hợp tương lai
- **Frontend Web**: Dự kiến phát triển giao diện web
- **Database**: Lưu trữ thông tin người dùng, API key và kết quả transcription
- **Authentication System**: Quản lý người dùng và phân quyền
- **RESTful API**: Cung cấp dịch vụ transcription thông qua API

## Khả năng mở rộng
- **Horizontal Scaling**: Khả năng xử lý nhiều yêu cầu đồng thời
- **Multi-model Support**: Tương lai có thể hỗ trợ nhiều model AI khác nhau
- **Multi-language Support**: Mở rộng hỗ trợ nhiều ngôn ngữ khác nhau

## Các kế hoạch kỹ thuật tương lai
- **Containerization**: Đóng gói ứng dụng trong Docker để dễ dàng triển khai
- **CI/CD Pipeline**: Thiết lập quy trình tích hợp và triển khai liên tục
- **Monitoring**: Theo dõi hiệu suất và sử dụng tài nguyên của hệ thống
- **Testing Framework**: Phát triển bộ test tự động để đảm bảo chất lượng
