# Audio Transcription

A library for audio transcription and alignment using Google Gemini API, designed for TTS labeling.

## Introduction

Audio Transcription is a powerful Python library that leverages Google Gemini API to convert speech to text with high accuracy. It's specifically designed for TTS (Text-to-Speech) labeling tasks, providing detailed voice descriptions and precise text-audio alignment. This library simplifies the process of transcribing audio content and matching it with corresponding text, making it an essential tool for speech analysis and TTS development. A key advantage of Audio Transcription is its ability to efficiently handle long audio files that conventional transcription solutions struggle with, breaking them down into manageable segments without sacrificing accuracy.

## Features

- **High-Accuracy Audio Transcription**: Convert speech to text using Google Gemini API
- **Long Audio Processing**: Efficiently handle lengthy audio files that conventional solutions struggle with
- **Smart Audio Segmentation**: Automatically split audio at appropriate silence points
- **Voice Description**: Provide detailed voice characterization compatible with modern LLM-based TTS systems
- **Text-Audio Alignment**: Synchronize text with audio content
- **Customizable**: Support for custom prompts and device selection for alignment

## Installation and Usage

### Installation

```bash
pip install gemini-audio-transcription
```

### Prerequisites

This library requires a Google Gemini API key. You can obtain one from [Google AI Studio](https://aistudio.google.com/).

### Basic Usage

#### Simple Transcription

```python
from gemini_audio_transcription import AudioTranscriber

# Initialize with API key
transcriber = AudioTranscriber(api_key="your-api-key")
# Or use environment variable: export GOOGLE_API_KEY="your-api-key"

# Transcribe an audio file
results = transcriber.transcribe("path/to/audio.wav")
print(results)
```

#### Complete Audio Processing

```python
from gemini_audio_transcription import AudioProcessor

# Initialize with options
processor = AudioProcessor(
    api_key="your-api-key",  # Optional if GOOGLE_API_KEY is set
    transcription_model="gemini-2.0-flash",
    whisper_model="large-v3",
    device="cpu"  # Use "cuda" for GPU or "mps" for Apple Silicon
)

# Process audio: transcribe and align
results = processor.process_audio(
    "path/to/audio.wav",
    save_folder="output_dir",  # Optional, to save audio chunks
    leading_silence_ms=100,    # Optional, silence at beginning of chunks
    trailing_silence_ms=100,   # Optional, silence at end of chunks
    language="en"              # Language code for alignment
)

# Save results to JSON
processor.save_transcription_json(results, "output_dir/results.json")
```

#### Text-Audio Alignment Only

If you already have the transcript and just want to align it with audio:

```python
from gemini_audio_transcription import TextAligner

aligner = TextAligner(
    model_name="large-v3",
    device="cuda"  # Use GPU for faster processing
)

# Align existing text with audio
text = "This is the transcript text that needs to be aligned with the audio."
chunks = aligner.align_text(
    text=text,
    audio_file="path/to/audio.wav",
    save_folder="aligned_chunks",
    language="en"
)
```

## Default Prompt and Explanation

The default prompt used by this library is designed specifically for TTS evaluation and transcription. It guides the Gemini model to:

1. Listen to audio and compare it to input text for accuracy
2. Consider text preprocessing (number-to-word conversion, special character removal)
3. Return results in a structured JSON format with transcript text and voice description

Here's the default prompt structure:

```
**Please evaluate this TTS-generated audio file based on the provided text input, following these guidelines:**

1. Carefully listen to the audio and compare it to the input text to ensure the speech matches the text exactly, without missing, mispronounced, or added words.

2. The input text is preprocessed such that:

   * All numbers are converted to words.
   * The text does not contain any special characters or symbols.

3. Return the output in the following JSON structure:
[
    {
        "text": "The original text input used to generate the speech. Each text segment is a single, complete sentence",
        "description": "Provide a detailed and objective description of the synthesized voice characteristics, including speaker gender (if perceivable), tone, emotion, pronunciation clarity, prosody (rhythm, intonation), and overall naturalness. For example: A male voice with a neutral tone, moderately expressive speaking style, and clearly articulated words. Slight robotic timbre but minimal distortion. No background noise detected. Each description must be specific, varied, and not repeated across entries."
    }
]

4. Do not include any commentary or content outside the specified JSON format.
```

The Voice Description feature is particularly valuable for modern TTS systems that leverage Large Language Models (LLMs), such as [parlerTTS](https://github.com/huggingface/parler-tts). These advanced TTS systems can utilize detailed voice characteristic descriptions to generate more natural and expressive speech. The rich metadata provided by Audio Transcription helps in:

- Training and fine-tuning voice models with specific characteristics
- Generating speech with desired emotional qualities and prosody
- Creating consistent voice personalities across different text inputs

You can customize this prompt by providing your own when initializing the transcriber:

```python
from gemini_audio_transcription import AudioTranscriber

custom_prompt = """
Your custom prompt here...
"""

transcriber = AudioTranscriber(
    api_key="your-api-key",
    custom_prompt=custom_prompt
)
```

## Note

**This library only works with a Google API key**. The transcription functionality is powered by Google Gemini API, and you must have a valid API key to use this library. Set the API key either when initializing the transcriber or as an environment variable (`GOOGLE_API_KEY`).

## Acknowledgements

- [Google Gemini API](https://ai.google.dev/) for providing the advanced transcription capabilities
- [stable-ts](https://github.com/jianfch/stable-ts) for the robust text-audio alignment functionality
