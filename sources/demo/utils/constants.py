"""
Các hằng số và cấu hình dùng chung cho ứng dụng.
"""

# Tiêu đề và thông tin chung
APP_TITLE = "Công cụ phiên âm và phân đoạn audio"
APP_PAGE_TITLE = "Audio Transcription Demo"
APP_FOOTER = "Audio Transcription Demo © 2025"

# Các tùy chọn model
MODEL_OPTIONS = ["gemini-2.0-flash", "gemini-2.0-flash-lite"]
DEFAULT_MODEL = "gemini-2.0-flash"

# Các chế độ xử lý
PROCESSING_MODES = ["Chỉ phiên âm", "Phiên âm và phân đoạn"]
DEFAULT_PROCESSING_MODE_INDEX = 1  # Phiên âm và phân đoạn

# Các giá trị mặc định
DEFAULT_MAX_RETRIES = 3
DEFAULT_LEADING_SILENCE_MS = 100
DEFAULT_TRAILING_SILENCE_MS = 100
DEFAULT_CACHE_RESULTS = True

# Định dạng audio được hỗ trợ
SUPPORTED_AUDIO_FORMATS = ["wav", "mp3"]

# Các thông số hiển thị
TRANSCRIPT_PREVIEW_HEIGHT = 200
ITEMS_PER_PAGE_MIN = 5
ITEMS_PER_PAGE_MAX = 20
ITEMS_PER_PAGE_DEFAULT = 10

# Các nút và nhãn
BUTTON_PROCESS_AUDIO = "Xử lý Audio"
BUTTON_CLEAR_CACHE = "Xóa cache"
BUTTON_SAVE_SETTINGS = "Lưu cài đặt"
BUTTON_PREV_PAGE = "◀️ Trước"
BUTTON_NEXT_PAGE = "▶️ Sau"

# Tab labels
TAB_LABELS = ["Cài đặt phiên âm", "Cài đặt căn chỉnh", "Cài đặt hệ thống"]

# Các nhãn download
DOWNLOAD_JSON_LABEL = "Tải JSON"
DOWNLOAD_TEXT_ZIP_LABEL = "Tải văn bản (ZIP)"
DOWNLOAD_ALL_ZIP_LABEL = "Tải audio, text & metadata (ZIP)"

# File names
JSON_FILENAME = "transcription_results.json"
TEXT_ZIP_FILENAME = "text_files.zip"
ALL_ZIP_FILENAME = "audio_text_files.zip"
