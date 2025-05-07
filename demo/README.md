# Audio Transcription Demo Application

A streamlit-based demo application for the Audio Transcription library. This application provides a user-friendly interface for audio transcription and segmentation using Google Gemini API.

## Features

- **Interactive UI**: Easy-to-use web interface for audio processing
- **Audio Transcription**: Transcribe audio files using Google Gemini API
- **Audio Segmentation**: Segment audio files by sentences
- **Result Visualization**: View and listen to segmented audio
- **Export Options**: Download results in various formats (JSON, CSV, ZIP)
- **Settings Management**: Configure processing parameters
- **Cache System**: Reuse previous results for faster processing

## Prerequisites

- Python 3.10+
- Audio Transcription library
- Streamlit
- Plotly

## Installation

1. First, make sure you have the Audio Transcription library installed:
   ```bash
   # Install the library with demo extras
   pip install -e ".[demo]"
   ```
   
2. Set up your Google Gemini API key:
   ```bash
   # Set as environment variable
   export GOOGLE_API_KEY="your-api-key-here"
   ```

## Running the Demo

To run the demo application:

```bash
streamlit run demo/homepage.py
```

The application will open in your default web browser.

## Demo Pages

### 1. Home Page

The landing page with overview information about the application and its features.

### 2. Transcription & Segmentation

Main processing page where you can:
- Upload audio files
- Choose processing mode
- Adjust processing parameters
- Process audio and view results

### 3. Transcript Viewer

Dedicated page for viewing and analyzing transcription results:
- View full transcript text
- Examine individual segments with audio playback
- Download results in different formats

### 4. Settings

Configure application settings:
- Default AI model selection
- Processing parameters
- Cache management

## Configuration Options

### Processing Options

- **AI Model**: Choose between different Google Gemini models
- **Processing Mode**: Transcription only or transcription with segmentation
- **Language**: Select language for processing
- **Device**: Choose hardware device for processing (CPU, CUDA, MPS)

### Segmentation Options

- **Leading Silence**: Add silence at the beginning of each segment (ms)
- **Trailing Silence**: Add silence at the end of each segment (ms)

## Cache System

The application includes a cache system that stores processed results to avoid reprocessing the same audio files with the same parameters. You can:

- Enable/disable caching
- Clear cache when needed

## Tips for Best Results

1. Use high-quality audio files with clear speech
2. Choose the appropriate AI model for your needs
3. For large files, ensure you have enough memory
4. When using GPU acceleration, make sure your drivers are up to date

## Troubleshooting

- If you encounter API errors, check your API key and internet connection
- For memory issues, try processing smaller audio files
- If segmentation results are poor, adjust silence thresholds
- Clear cache if you experience unexpected behavior

## License

This demo application is part of the Audio Transcription project and is licensed under the MIT License. See the LICENSE file for details.
