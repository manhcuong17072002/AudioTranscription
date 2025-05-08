"""
Audio Transcription - A library for audio transcription and alignment using Google Gemini API.
"""

from .version import __version__
from .transcriber import AudioTranscriber
from .aligner import TextAligner
from .processor import AudioProcessor

__all__ = [
    "__version__",
    "AudioTranscriber",
    "TextAligner",
    "AudioProcessor",
]
