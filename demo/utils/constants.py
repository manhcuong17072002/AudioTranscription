"""
Constants for the Audio Transcription demo application.
"""

# App information
APP_TITLE = "Audio Transcription"
APP_PAGE_TITLE = "Audio Transcription Tool"
APP_FOOTER = "© 2025 Audio Transcription | Powered by Google Gemini API"

# Processing options
PROCESSING_MODES = ["Transcription only", "Transcription & Segmentation"]
DEFAULT_PROCESSING_MODE_INDEX = 1  # Default to "Transcription & Segmentation"

# Model options
MODEL_OPTIONS = [
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite",
]
DEFAULT_MODEL = "gemini-2.0-flash"

# Device options for whisper model
DEVICE_OPTIONS = ["cpu", "cuda", "mps"]  # CPU, NVIDIA GPU, Apple Silicon
DEFAULT_DEVICE = "cpu"

# UI constants
BUTTON_PROCESS_AUDIO = "Process Audio"
TRANSCRIPT_PREVIEW_HEIGHT = 100  # Height in pixels for transcript preview

# Supported formats
SUPPORTED_AUDIO_FORMATS = ["wav", "mp3"]
