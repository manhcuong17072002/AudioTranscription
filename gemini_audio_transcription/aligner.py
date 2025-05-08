"""
Text-to-audio alignment module.

This module provides functionality to align text with audio and segment audio files 
into chunks based on the text.
"""

import os
import random
import string
from io import BytesIO
from typing import Dict, List, Optional, Tuple, Union

import stable_whisper
from stable_whisper.result import WhisperResult
from pydub import AudioSegment
from stable_whisper.whisper_word_level.hf_whisper import WhisperHF

class TextAligner:
    """
    Class for aligning text with audio and creating audio segments.
    """

    def __init__(self, model_name="large-v3", device="cpu"):
        """
        Initialize TextAligner with a specific model and device.
        
        Args:
            model_name (str): Whisper model name ("tiny", "base", "small", "medium", "large", "large-v3")
            device (str): Device to run the model on ("cpu", "cuda", "mps")
        """
        self.model_name = model_name
        self.device = device
        self.model = self._load_model(model_name, device)

    def _load_model(self, model_name, device) -> WhisperHF:
        """
        Load the stable_whisper model.
        
        Args:
            model_name (str): Whisper model name
            device (str): Device to run the model on
            
        Returns:
            The loaded model
        """
        print(f"Loading stable_whisper model {model_name} on {device}")
        return stable_whisper.load_model(model_name, device=device)
    
    def align_text(
        self,
        text: Union[str, list[str]],
        audio_file: Union[str, BytesIO, bytes],
        save_folder: Optional[str] = None,
        leading_silence_ms: int = 0,
        trailing_silence_ms: int = 0,
        language: str = "en",
    ) -> List[Dict]:
        """
        Align text with audio and segment into chunks.
        
        Args:
            text: Text to align with audio, can be a string or list of strings
            audio_file: Audio file, can be path, BytesIO or bytes
            save_folder: Folder to save audio chunks and text, if None doesn't save
            leading_silence_ms: Silence (ms) to add at the beginning of each chunk
            trailing_silence_ms: Silence (ms) to add at the end of each chunk
            language: Language code for alignment, default is English ("en")
            
        Returns:
            If save_folder is None: List of dictionaries with {"audio": AudioSegment, "text": str, "filename": str}
            If save_folder is provided: List of dictionaries with {"filename": str, "text": str, "full_path": str}
            
        Raises:
            ValueError: If audio format is not supported
        """
        # Convert text list to string if needed
        if isinstance(text, list):
            text = "\n".join(text)

        # Handle BytesIO conversion
        if isinstance(audio_file, BytesIO):
            audio_file = audio_file.read()

        # Align text with audio using stable_whisper
        result: WhisperResult = self.model.align(
            audio_file, text, language=language, original_split=True
        )

        # Load original audio file
        audio = self._load_audio(audio_file)

        # Create silence for use if needed
        silence = AudioSegment.silent(duration=1)  # 1ms silence to multiply

        # Segment audio according to timestamps from segments
        audio_chunks = []
        for segment in result.segments:
            # Get timestamp (already in milliseconds) and text from segment
            start_time_ms = int(segment.start * 1000)  # Convert from seconds to milliseconds
            end_time_ms = int(segment.end * 1000)  # Convert from seconds to milliseconds
            subtitle = segment.text.strip()

            # Cut audio according to timestamps
            chunk = audio[start_time_ms:end_time_ms]

            # Add silence if needed
            if leading_silence_ms > 0:
                leading_silence = silence * leading_silence_ms
                chunk = leading_silence + chunk

            if trailing_silence_ms > 0:
                trailing_silence = silence * trailing_silence_ms
                chunk = chunk + trailing_silence

            # Create random filename for each chunk
            random_name = "".join(
                random.choices(string.ascii_lowercase + string.digits, k=10)
            )
            filename = f"{random_name}.wav"

            audio_chunks.append({"audio": chunk, "text": subtitle, "filename": filename})

        # Process output depending on save_folder
        if save_folder:
            # Create directory if it doesn't exist
            os.makedirs(save_folder, exist_ok=True)

            saved_files = []

            # Save each audio chunk and text
            for chunk_data in audio_chunks:
                chunk = chunk_data["audio"]
                subtitle = chunk_data["text"]
                filename = chunk_data["filename"]

                # Save audio file
                audio_path = os.path.join(save_folder, filename)
                chunk.export(audio_path, format="wav")

                # Save text file
                text_name = filename.replace(".wav", ".txt")
                text_path = os.path.join(save_folder, text_name)
                with open(text_path, "w", encoding="utf-8") as f:
                    f.write(subtitle)

                # Add information to result
                saved_files.append(
                    {"filename": filename, "text": subtitle, "full_path": audio_path}
                )

            return saved_files
        else:
            # Return list of dictionaries with audio, text and filename
            return audio_chunks

    def _load_audio(self, audio_file: Union[str, BytesIO, bytes]) -> AudioSegment:
        """
        Load audio file from different formats into AudioSegment.

        Args:
            audio_file: Audio file, can be path, BytesIO or bytes

        Returns:
            AudioSegment: AudioSegment object
            
        Raises:
            ValueError: If audio format is not supported
        """
        if isinstance(audio_file, str):
            # File path
            return AudioSegment.from_file(audio_file)
        elif isinstance(audio_file, BytesIO):
            # BytesIO object
            return AudioSegment.from_file(audio_file)
        elif isinstance(audio_file, bytes):
            # Bytes data
            with BytesIO(audio_file) as audio_bytes:
                return AudioSegment.from_file(audio_bytes)
        else:
            raise ValueError("Unsupported audio format")
