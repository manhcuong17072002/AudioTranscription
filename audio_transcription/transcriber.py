"""
Audio transcription module using Google Gemini API.
"""

import json
import mimetypes
import os
import random
import string
import time
from io import BytesIO
from typing import Dict, List, Optional, Union

from google import genai
from magic import Magic

# Initialize with mime=True to get MIME type instead of description
magic = Magic(mime=True)

# Ensure mimetypes is initialized
mimetypes.init()


DEFAULT_PROMPT = """
**Please evaluate this TTS-generated audio file based on the provided text input, following these guidelines:**

1. Carefully listen to the audio and compare it to the input text to ensure the speech matches the text exactly, without missing, mispronounced, or added words.

2. The input text is preprocessed such that:

   * All numbers are converted to words.
   * The text does not contain any special characters or symbols.

3. Return the output in the following JSON structure:

```json
[
    {
        "text": "The original text input used to generate the speech. Each text segment is a single, complete sentence",
        "description": "Provide a detailed and objective description of the synthesized voice characteristics, including speaker gender (if perceivable), tone, emotion, pronunciation clarity, prosody (rhythm, intonation), and overall naturalness. For example: A male voice with a neutral tone, moderately expressive speaking style, and clearly articulated words. Slight robotic timbre but minimal distortion. No background noise detected. Each description must be specific, varied, and not repeated across entries."
    }
]
```

4. Do not include any commentary or content outside the specified JSON format.
"""


class AudioTranscriber:
    """
    Class for audio transcription using Google Gemini API.
    """

    def __init__(self, api_key=None, model="gemini-2.0-flash", custom_prompt=None):
        """
        Initialize AudioTranscriber.
        
        Args:
            api_key (str, optional): Google Gemini API key. If None, will be retrieved from environment.
            model (str): Gemini model name used for transcription.
            custom_prompt (str, optional): Custom prompt for the transcription. If None, default prompt will be used.
        
        Raises:
            ValueError: If no API key is provided and GOOGLE_API_KEY environment variable is not set.
        """
        self.api_key = self._get_api_key(api_key)
        self.model = model
        self.client = genai.Client(api_key=self.api_key)
        
        # Use custom prompt if provided, otherwise use default
        self.prompt = custom_prompt if custom_prompt else self._get_default_prompt()
    
    def _get_api_key(self, api_key=None):
        """
        Get Google Gemini API key with the following priority:
        1. From api_key parameter passed directly
        2. From GOOGLE_API_KEY environment variable
        
        Returns:
            str: API key
            
        Raises:
            ValueError: If no API key is provided and GOOGLE_API_KEY environment variable is not set.
        """
        # If api_key is passed directly
        if api_key:
            return api_key
            
        # Check environment variable
        env_key = os.environ.get("GOOGLE_API_KEY")
        if env_key:
            return env_key
            
        # API key not found
        raise ValueError("API key not provided. Please pass API key when initializing or set the GOOGLE_API_KEY environment variable")
    
    def _get_default_prompt(self):
        """
        Returns the default transcription prompt.
        
        Returns:
            str: Default prompt for the transcription API.
        """
        
        return DEFAULT_PROMPT
    
    def _parse_response(self, response_text: str) -> List[Dict[str, str]]:
        """
        Parse JSON result from Gemini API response text.

        Args:
            response_text (str): Response text from Gemini API

        Returns:
            List[Dict[str, str]]: List of parsed transcription results

        Raises:
            ValueError: If response cannot be parsed as JSON
        """
        try:
            # Find JSON string in the result
            start_index = response_text.find("[")
            end_index = response_text.rfind("]") + 1

            if start_index == -1 or end_index == 0:
                raise ValueError("Valid JSON format not found")

            json_str = response_text[start_index:end_index]
            return json.loads(json_str)

        except (json.JSONDecodeError, ValueError) as e:
            print(f"Error parsing result: {e}")
            print(f"Response text: {response_text}")
            raise ValueError(f"Cannot parse result as JSON: {e}")

    def _generate_random_string(self, length: int = 20) -> str:
        """
        Generate a random string of specified length.

        Args:
            length (int): Length of the random string

        Returns:
            str: Random string
        """
        return "".join(random.choices(string.ascii_letters + string.digits, k=length))

    def _get_normalized_mime_type(self, file_data: bytes, filename: str) -> str:
        """
        Determine standardized MIME type for audio file.

        Args:
            file_data: File content as bytes
            filename: File name

        Returns:
            str: Standardized MIME type
        """
        # Use python-magic to get MIME type from file content
        magic_mime = magic.from_buffer(file_data)

        # Use mimetypes to get MIME type from filename
        filename_mime, _ = mimetypes.guess_type(filename)

        print(f"MIME from magic: {magic_mime}, MIME from filename: {filename_mime}")

        # Map common MIME types to standardized form
        mime_mapping = {
            "audio/x-wav": "audio/wav",
            "audio/x-mp3": "audio/mpeg",
            "audio/mp3": "audio/mpeg",
            "application/octet-stream": None,  # Will rely on filename_mime
        }

        # Prioritize using magic_mime if it's audio/*
        if magic_mime and magic_mime.startswith("audio/"):
            return mime_mapping.get(magic_mime, magic_mime)

        # If magic_mime is not audio/*, try using filename_mime
        if filename_mime and filename_mime.startswith("audio/"):
            return filename_mime

        # Fallback: base on file extension
        if filename.lower().endswith(".wav"):
            return "audio/wav"
        elif filename.lower().endswith((".mp3", ".mpeg")):
            return "audio/mpeg"
        elif filename.lower().endswith(".ogg"):
            return "audio/ogg"
        elif filename.lower().endswith(".flac"):
            return "audio/flac"

        # If type cannot be determined, return default magic_mime
        return magic_mime

    def transcribe(
        self, 
        file: Union[str, BytesIO],
        max_retries: int = 5
    ) -> List[Dict[str, str]]:
        """
        Transcribe audio file content using Google Gemini API.

        Args:
            file: Path to audio file or BytesIO object
            max_retries: Maximum number of retry attempts on error

        Returns:
            List[Dict[str, str]]: Transcription results as JSON

        Raises:
            ValueError: If file format is not supported
            RuntimeError: If transcription fails after maximum retries
        """
        # Variable to track uploaded file
        uploaded_file = None

        # Create a copy of file to avoid affecting the original object
        if isinstance(file, BytesIO):
            # Create safe copy of BytesIO
            file.seek(0)
            file_copy = BytesIO(file.getvalue())
            # Reset pointer to beginning on both original and copy
            file.seek(0)  # Reset original file for other processing
            file = file_copy  # Use copy for our processing

        try:
            # Process input file and prepare config
            if isinstance(file, str):
                with open(file, "rb") as f:
                    file_data = f.read()
                filename = os.path.basename(file)
                file_source = file  # Store original path
            elif isinstance(file, BytesIO):
                # BytesIO was already reset to beginning when copy was created
                file_data = file.getvalue()

                # Determine filename
                if hasattr(file, "name") and file.name:
                    filename = os.path.basename(file.name)
                else:
                    filename = f"audio_{self._generate_random_string()}.wav"

                file_source = file  # File source is the BytesIO copy
            else:
                raise ValueError("File format not supported")

            # Determine normalized MIME type
            mime_type = self._get_normalized_mime_type(file_data, filename)
            config = {"mime_type": mime_type}
            print(f"Using MIME type: {mime_type} for file {filename}")

            # Try upload and process with retry
            for attempt in range(max_retries):
                try:
                    # Delete previously uploaded file if exists
                    if uploaded_file:
                        try:
                            self.client.files.delete(name=uploaded_file.name)
                            print(f"Deleted previous temporary file: {uploaded_file.name}")
                        except Exception as e:
                            print(f"Could not delete temporary file: {str(e)}")

                    # Reset file to beginning before upload
                    if isinstance(file_source, BytesIO) and hasattr(file_source, "seek"):
                        file_source.seek(0)

                    # Upload file
                    uploaded_file = self.client.files.upload(file=file_source, config=config)
                    print(f"Uploaded file {filename} with ID: {uploaded_file.name}")

                    # Call Gemini API
                    response = self.client.models.generate_content(
                        model=self.model,
                        contents=[self.prompt, uploaded_file],
                    )

                    # Get text from response
                    response_text = response.text

                    # Parse JSON result
                    results = self._parse_response(response_text)

                    print(f"Successfully transcribed file {filename}: {len(results)} results")
                    return results

                except Exception as e:
                    error_message = str(e).lower()
                    last_attempt = attempt == max_retries - 1

                    # Check different error types
                    if "rate limit" in error_message or "quota" in error_message:
                        # Handle rate limit by waiting
                        print(
                            f"Rate limit error, retrying ({attempt+1}/{max_retries})..."
                        )
                        time.sleep(1)  # Wait 1 second before retrying
                    elif (
                        "overloaded" in error_message
                        or "unavailable" in error_message
                        or "busy" in error_message
                    ):
                        # Handle model overloaded by waiting longer
                        wait_time = min(
                            30, 2**attempt + 1
                        )  # Exponential backoff, max 30s
                        print(
                            f"Model overloaded, waiting {wait_time}s before retrying ({attempt+1}/{max_retries})..."
                        )
                        time.sleep(wait_time)

                        # If last attempt and model is still overloaded, try non-lite model
                        if last_attempt and "-lite" in self.model:
                            non_lite_model = self.model.replace("-lite", "")
                            print(f"Trying with non-lite model: {non_lite_model}")
                            try:
                                response = self.client.models.generate_content(
                                    model=non_lite_model,
                                    contents=[self.prompt, uploaded_file],
                                )
                                response_text = response.text
                                results = self._parse_response(response_text)
                                print(f"Successfully transcribed with model {non_lite_model}")
                                return results
                            except Exception as model_e:
                                print(
                                    f"Not successful with model {non_lite_model}: {model_e}"
                                )

                        if last_attempt:
                            print("Trying one final attempt with longer wait time...")
                            time.sleep(10)  # Wait 10 more seconds
                            max_retries += 1  # Add one more try

                    elif not last_attempt:  # If there are more attempts
                        # Other error but still can retry
                        wait_time = 2 * (attempt + 1)
                        print(f"Error calling API: {e}. Retrying after {wait_time}s...")
                        time.sleep(wait_time)
                    else:
                        # Other error and no more attempts
                        print(f"Error calling API: {e}")
                        raise

            # If all attempts were unsuccessful
            raise RuntimeError(f"Could not transcribe after {max_retries} retry attempts")

        finally:
            # Delete uploaded files to free resources
            try:
                # Delete by known filename
                if uploaded_file and hasattr(uploaded_file, "name"):
                    try:
                        print(f"Deleting uploaded file: {uploaded_file.name}")
                        self.client.files.delete(name=uploaded_file.name)
                    except Exception as e:
                        print(f"Error deleting uploaded file: {e}")

                # Delete any other files that might remain
                try:
                    for f in self.client.files.list():
                        if hasattr(f, "name"):
                            print(f"Deleting leftover file: {f.name}")
                            self.client.files.delete(name=f.name)
                except Exception as e:
                    print(f"Error listing/deleting leftover files: {e}")
            except Exception as e:
                print(f"Overall error when deleting uploaded files: {e}")
