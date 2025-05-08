"""
Audio processing module for transcription and alignment.

This module combines transcription and alignment capabilities to provide 
a complete audio processing pipeline.
"""

import json
import logging
import os
from io import BytesIO
from typing import Dict, List, Optional, Union, Any

from pydub import AudioSegment

from .transcriber import AudioTranscriber
from .aligner import TextAligner

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AudioProcessor:
    """
    Class for complete audio processing including transcription and alignment.
    Combines AudioTranscriber and TextAligner functionality.
    """

    def __init__(
        self, 
        api_key=None, 
        transcription_model="gemini-2.0-flash", 
        whisper_model="large-v3", 
        device="cpu",
        custom_prompt=None
    ):
        """
        Initialize AudioProcessor.
        
        Args:
            api_key (str, optional): Google Gemini API key. If None, will be retrieved from environment.
            transcription_model (str): Gemini model name for transcription.
            whisper_model (str): Whisper model name for alignment.
            device (str): Device for running whisper model ("cpu", "cuda", "mps").
            custom_prompt (str, optional): Custom prompt for transcription. If None, default prompt will be used.
        """
        self.transcriber = AudioTranscriber(api_key=api_key, model=transcription_model, custom_prompt=custom_prompt)
        self.aligner = TextAligner(model_name=whisper_model, device=device)
    
    def process_audio(
        self, 
        audio_file: Union[str, BytesIO], 
        save_folder: Optional[str] = None, 
        leading_silence_ms: int = 0, 
        trailing_silence_ms: int = 0, 
        max_retries: int = 3,
        language: str = "en"
    ) -> List[Dict[str, Any]]:
        """
        Process audio file: transcribe and align text-audio.
        
        Args:
            audio_file: Path to audio file or BytesIO object
            save_folder: Folder to save audio chunks and text, if None doesn't save
            leading_silence_ms: Silence (ms) to add at the beginning of each chunk
            trailing_silence_ms: Silence (ms) to add at the end of each chunk
            max_retries: Maximum number of retry attempts on rate limit errors
            language: Language code for alignment
            
        Returns:
            List[Dict[str, Any]]: Transcription results with audio information
        
        Raises:
            ValueError: If audio file is invalid or alignment fails
            RuntimeError: If transcription fails after maximum retries
        """
        # Validate input
        if not isinstance(audio_file, (str, BytesIO)):
            raise ValueError("audio_file must be a path (str) or BytesIO object")
            
        if save_folder is not None and not isinstance(save_folder, str):
            raise ValueError("save_folder must be None or string")
        
        # Create a copy of BytesIO to avoid file pointer issues
        if isinstance(audio_file, BytesIO):
            # Save bytes content
            audio_file.seek(0)
            audio_bytes = audio_file.getvalue()
            # Create new BytesIO for processing
            audio_file_copy = BytesIO(audio_bytes)
            audio_file = audio_file_copy
        
        # Step 0: Convert audio to mono if stereo
        try:
            # Preserve original path if audio_file is string
            original_path = audio_file if isinstance(audio_file, str) else None
            
            # Convert audio to mono
            mono_audio = self._convert_to_mono(audio_file)
            
            # If input is path string, maintain that information for other modules
            if original_path:
                # Some modules may require string path, we log the information
                logger.info(f"Converted file {original_path} to mono")
                # Use mono_audio (BytesIO) for next steps
                audio_file = mono_audio
            else:
                # If input is BytesIO, replace with mono version
                audio_file = mono_audio
                
        except Exception as e:
            logger.warning(f"Could not convert audio to mono: {str(e)}. Continuing with original format.")
            # If conversion fails, continue with original file
        
        # Step 1: Transcribe audio file
        logger.info("Starting audio processing")
        
        # Ensure BytesIO is at beginning before transcription
        if isinstance(audio_file, BytesIO):
            audio_file.seek(0)
            logger.debug("Reset BytesIO pointer before transcription")
            
        transcription_results = self.transcriber.transcribe(audio_file, max_retries)
        
        # Step 2: Extract transcript text from transcription results
        transcript_text = self._extract_transcript_text(transcription_results)
        if not transcript_text:
            logger.warning("No text extracted from transcription results")
            return transcription_results
        
        # Ensure BytesIO is at beginning before alignment
        if isinstance(audio_file, BytesIO):
            audio_file.seek(0)
            logger.debug("Reset BytesIO pointer before alignment")
        
        # Step 3: Align text with audio to create audio chunks
        aligned_chunks = self.aligner.align_text(
            text=transcript_text,
            audio_file=audio_file,
            save_folder=save_folder,
            leading_silence_ms=leading_silence_ms,
            trailing_silence_ms=trailing_silence_ms,
            language=language
        )
        
        # Step 4: Combine transcription results with audio chunk info
        combined_results = self._combine_results(transcription_results, aligned_chunks)
        
        logger.info("Audio processing complete")
        return combined_results

    def transcribe_only(self, audio_file: Union[str, BytesIO], max_retries: int = 3) -> List[Dict[str, str]]:
        """
        Transcribe audio without alignment.
        
        Args:
            audio_file: Path to audio file or BytesIO object
            max_retries: Maximum number of retry attempts on rate limit errors
            
        Returns:
            List[Dict[str, str]]: Transcription results
        """
        mono_audio = self._convert_to_mono(audio_file)
        return self.transcriber.transcribe(mono_audio, max_retries=max_retries)
    
    def align_only(
        self, 
        text: Union[str, list[str]], 
        audio_file: Union[str, BytesIO], 
        save_folder: Optional[str] = None, 
        leading_silence_ms: int = 0, 
        trailing_silence_ms: int = 0,
        language: str = "en"
    ) -> List[Dict]:
        """
        Align text with audio without transcription.
        
        Args:
            text: Text to align with audio
            audio_file: Path to audio file or BytesIO object
            save_folder: Folder to save audio chunks and text
            leading_silence_ms: Silence (ms) to add at the beginning of each chunk
            trailing_silence_ms: Silence (ms) to add at the end of each chunk
            language: Language code for alignment
            
        Returns:
            List[Dict]: Audio chunks with aligned text
        """
        mono_audio = self._convert_to_mono(audio_file)
        return self.aligner.align_text(
            text=text,
            audio_file=mono_audio,
            save_folder=save_folder,
            leading_silence_ms=leading_silence_ms,
            trailing_silence_ms=trailing_silence_ms,
            language=language
        )
    
    def _convert_to_mono(self, audio_file: Union[str, BytesIO]) -> BytesIO:
        """
        Convert audio file to mono channel if it's stereo.
        
        Args:
            audio_file: Path to audio file or BytesIO object
            
        Returns:
            BytesIO: Buffer containing mono audio
            
        Raises:
            ValueError: If audio file cannot be read
        """
        try:
            # Load audio
            if isinstance(audio_file, BytesIO):
                # Make sure pointer is at beginning
                if hasattr(audio_file, 'seek'):
                    audio_file.seek(0)
                    
            audio: AudioSegment = AudioSegment.from_file(audio_file)
            
            # Check if audio is stereo (2+ channels) and convert to mono
            if audio.channels > 1:
                logger.info(f"Converting audio from {audio.channels} channels to mono")
                audio = audio.set_channels(1)
            
            # Export audio to BytesIO
            output_buffer = BytesIO()
            audio.export(output_buffer, format="wav")
            output_buffer.seek(0)
            
            return output_buffer
        except Exception as e:
            logger.error(f"Error converting audio to mono: {str(e)}")
            raise ValueError(f"Cannot convert audio to mono: {str(e)}")
    
    def _extract_transcript_text(self, transcription_results: List[Dict[str, str]]) -> str:
        """
        Extract text from transcription results.
        
        Args:
            transcription_results: Results from AudioTranscriber
            
        Returns:
            str: Extracted and joined text
        """
        transcript = []
        for result in transcription_results:
            if "text" in result:
                transcript.append(result["text"])
        
        transcript_text = "\n".join(transcript)
        logger.debug(f"Extracted text: {len(transcript_text)} characters")
        return transcript_text
    
    def _combine_results(self, transcription_results: List[Dict[str, str]], aligned_chunks: List[Dict]) -> List[Dict[str, Any]]:
        """
        Combine transcription results with aligned audio chunks.
        
        Args:
            transcription_results: Results from AudioTranscriber
            aligned_chunks: Audio chunks from TextAligner
            
        Returns:
            List[Dict[str, Any]]: Combined results
        """
        combined_results = []
        
        # Copy transcription_results to avoid modifying original
        combined_results = transcription_results.copy()
        
        # Ensure number of elements in both lists is equivalent
        min_length = min(len(combined_results), len(aligned_chunks))
        
        if min_length != len(combined_results):
            logger.warning(f"Mismatch between transcription results ({len(combined_results)}) and audio chunks ({len(aligned_chunks)})")
            
        # Combine information from aligned_chunks into combined_results
        for i in range(min_length):
            combined_results[i].update(aligned_chunks[i])
        
        logger.info(f"Successfully combined transcription results with {min_length} audio chunks")
        return combined_results[:min_length]
    
    def save_transcription_json(self, transcription_results: List[Dict[str, Any]], output_path: str) -> str:
        """
        Save transcription results to JSON file.
        
        Args:
            transcription_results: Transcription results
            output_path: Path to output JSON file
            
        Returns:
            str: Path to saved JSON file
        
        Raises:
            IOError: If directory cannot be created or file cannot be written
        """
        try:
            # Create directory for file if it doesn't exist
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Save results to JSON file
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(transcription_results, f, ensure_ascii=False, indent=4)
            
            logger.info(f"Saved transcription results to {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Error saving transcription results: {str(e)}")
            raise IOError(f"Cannot save transcription results: {str(e)}")
