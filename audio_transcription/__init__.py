"""
Audio Transcription Library.

A library for audio transcription and alignment using Google Gemini API, 
designed for TTS labeling.
"""

from .transcriber import AudioTranscriber
from .aligner import TextAligner
from .processor import AudioProcessor

__version__ = "0.1.0"
