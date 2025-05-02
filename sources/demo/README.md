# Demo Phiên Âm và Phân Đoạn Audio

Demo này giúp bạn phiên âm nội dung audio và phân đoạn thành các đoạn audio nhỏ tương ứng với từng câu/đoạn văn bản.

## Tính năng

- Phiên âm audio sử dụng Google Gemini API
- Phân đoạn audio theo từng câu/đoạn văn bản
- Tải xuống kết quả dưới nhiều định dạng: JSON, ZIP (chỉ text), ZIP (cả audio, text và metadata)
- Nghe trực tiếp từng đoạn audio đã cắt
- Tùy chỉnh các thông số xử lý: model AI, khoảng lặng đầu/cuối, v.v.

## Cài đặt

Đảm bảo bạn đã cài đặt các thư viện cần thiết:

```bash
pip install -r requirements.txt
```

## Cách sử dụng

1. Chạy ứng dụng Streamlit:

```bash
streamlit run sources/demo/tts_labeling.py
```

2. Tải lên file audio (định dạng WAV, MP3, OGG)
3. Chọn chế độ xử lý (chỉ phiên âm hoặc phiên âm và phân đoạn)
4. Nhấn nút "Xử lý Audio" và đợi kết quả
5. Xem kết quả chi tiết trong tab "Kết quả phiên âm"
6. Tải xuống kết quả dưới dạng JSON hoặc file ZIP chứa audio/text

## Cấu trúc thư mục

```
sources/demo/
├── tts_labeling.py        # File chính - trang home
├── pages/                 # Thư mục chứa các trang phụ
│   ├── __init__.py
│   ├── transcript_view.py  # Trang xem chi tiết phiên âm
│   └── settings.py         # Trang cài đặt nâng cao
└── utils/                  # Các hàm tiện ích
    ├── __init__.py
    └── zip_utils.py        # Chức năng tạo và xử lý file zip
```

## Yêu cầu hệ thống

- Python 3.8 trở lên
- 4GB RAM trở lên
- Kết nối internet để sử dụng Google Gemini API

## API Key

Đảm bảo bạn đã cấu hình API key của Google Gemini trong file `sources/core/api_key.py`.
