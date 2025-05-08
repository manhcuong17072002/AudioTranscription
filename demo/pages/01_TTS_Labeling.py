"""
Transcription and segmentation page for the Audio Transcription demo.
"""

import logging
import time
from io import BytesIO
from typing import Dict, List

import pandas as pd
import streamlit as st
from streamlit.runtime.uploaded_file_manager import UploadedFile

# Import from utils
from demo.utils.constants import (
    APP_TITLE,
    BUTTON_PROCESS_AUDIO,
    DEFAULT_PROCESSING_MODE_INDEX,
    MODEL_OPTIONS,
    PROCESSING_MODES,
    SUPPORTED_AUDIO_FORMATS,
    TRANSCRIPT_PREVIEW_HEIGHT,
    DEFAULT_MODEL,
    DEVICE_OPTIONS,
    DEFAULT_DEVICE,
    APP_FOOTER
)
from demo.utils.cache_utils import (
    get_current_settings,
    update_settings,
    generate_cache_key,
    clear_cache,
)
from demo.utils.display_utils import show_transcript_details
from demo.utils.custom_styles import load_css

# Import from audio_transcription library
from audio_transcription import AudioTranscriber, AudioProcessor


# Create cached functions to avoid reinitializing processor/transcriber unnecessarily
@st.cache_resource
def get_processor(api_key, transcription_model, whisper_model, device):
    """
    Create and cache an AudioProcessor instance.
    Will only be recreated if any of the input parameters change.

    Args:
        api_key: Google API key
        transcription_model: Gemini model to use
        whisper_model: Whisper model to use
        device: Processing device (cpu, cuda, mps)

    Returns:
        AudioProcessor: Cached processor instance
    """
    return AudioProcessor(
        api_key=api_key,
        transcription_model=transcription_model,
        whisper_model=whisper_model,
        device=device,
    )


@st.cache_resource
def get_transcriber(api_key, model):
    """
    Create and cache an AudioTranscriber instance.
    Will only be recreated if any of the input parameters change.

    Args:
        api_key: Google API key
        model: Gemini model to use

    Returns:
        AudioTranscriber: Cached transcriber instance
    """
    return AudioTranscriber(api_key=api_key, model=model)


# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# Settings functions copied from demo/pages/02_Settings.py
def show_general_settings(settings):
    """
    Display general settings.

    Args:
        settings (dict): Current application settings
    """
    st.subheader("General Settings")

    # Model selection
    model = st.selectbox(
        "Default AI Model",
        options=MODEL_OPTIONS,
        index=(
            MODEL_OPTIONS.index(settings.get("model", DEFAULT_MODEL))
            if settings.get("model", DEFAULT_MODEL) in MODEL_OPTIONS
            else 0
        ),
        help="Select the default AI model for transcription",
    )

    # Language settings (for future expansion)
    language = st.selectbox(
        "Default Language",
        options=["English", "Vietnamese", "Auto-detect"],
        index=0,  # Default to English
        help="Language used for transcription and alignment (Auto-detect will attempt to identify the language)",
    )

    # Save button
    if st.button("Save General Settings"):
        # Update settings
        updated_settings = settings.copy()
        updated_settings["model"] = model
        if language == "English":
            updated_settings["language_code"] = "en"
        elif language == "Vietnamese":
            updated_settings["language_code"] = "vi"
        else:
            updated_settings["language_code"] = "auto"

        update_settings(updated_settings)
        st.session_state.settings_updated = True
        st.rerun()


def show_api_settings(settings):
    """
    Display API settings.

    Args:
        settings (dict): Current application settings
    """
    st.subheader("API Settings")
    st.markdown(
        """
    - Your API key is stored in the session state and will persist only during your browser session
    - The key is never sent to our servers and is only used to communicate with Google's Gemini API
    - For production use, consider setting the GOOGLE_API_KEY environment variable instead
    -------
    """
    )

    # Display existing API key information
    current_api_key = settings.get("api_key", "")
    has_api_key = bool(current_api_key)

    if has_api_key:
        st.info(
            "Google Gemini API key is currently set. You can update it below if needed."
        )
        # Show a masked version of the key
        masked_key = (
            current_api_key[:4]
            + "*" * (len(current_api_key) - 8)
            + current_api_key[-4:]
            if len(current_api_key) > 8
            else "****"
        )
        st.text(f"Current API key: {masked_key}")
    else:
        st.warning(
            "No API key is currently set. Please enter your Google Gemini API key below."
        )

    # Input for API key
    new_api_key = st.text_input(
        "Google Gemini API Key",
        type="password",
        help="Enter your Google Gemini API key. Get one from https://aistudio.google.com/",
        value="",
    )

    # Option to clear the API key
    col1, col2 = st.columns(2)

    with col1:
        if st.button("Save API Key", type="primary", disabled=not new_api_key):
            # Update settings
            updated_settings = settings.copy()
            updated_settings["api_key"] = new_api_key
            update_settings(updated_settings)
            st.session_state.settings_updated = True
            st.success("API key saved successfully!")
            st.rerun()

    with col2:
        if st.button("Clear API Key", disabled=not has_api_key):
            # Update settings
            updated_settings = settings.copy()
            updated_settings.pop("api_key", None)
            update_settings(updated_settings)
            st.session_state.settings_updated = True
            st.success("API key removed successfully!")
            st.rerun()


def show_advanced_settings(settings):
    """
    Display advanced settings.

    Args:
        settings (dict): Current application settings
    """
    st.subheader("Advanced Settings")

    # API retry settings
    max_retries = st.slider(
        "Max API Retry Attempts",
        min_value=1,
        max_value=10,
        value=settings.get("max_retries", 3),
        help="Maximum number of retry attempts when API calls fail due to rate limiting",
    )

    # Segmentation settings
    col1, col2 = st.columns(2)

    with col1:
        leading_silence_ms = st.slider(
            "Leading Silence (ms)",
            min_value=0,
            max_value=1000,
            value=settings.get("leading_silence_ms", 100),
            step=10,
            help="Silence to add at the beginning of each audio segment (milliseconds)",
        )

    with col2:
        trailing_silence_ms = st.slider(
            "Trailing Silence (ms)",
            min_value=0,
            max_value=1000,
            value=settings.get("trailing_silence_ms", 100),
            step=10,
            help="Silence to add at the end of each audio segment (milliseconds)",
        )

    # Hardware acceleration settings
    # Get the current device setting
    current_device = settings.get("device", DEFAULT_DEVICE)

    # Map the internal device value to display value
    device_display_map = {
        "cpu": "CPU",
        "cuda": "GPU (CUDA)",
        "mps": "Apple Silicon (MPS)",
    }

    device_display = device_display_map.get(current_device, "CPU")

    device = st.selectbox(
        "Processing Device",
        options=["CPU", "GPU (CUDA)", "Apple Silicon (MPS)"],
        index=(
            list(device_display_map.values()).index(device_display)
            if device_display in device_display_map.values()
            else 0
        ),
        help="Hardware to use for Whisper model processing. GPU options require appropriate hardware and drivers.",
    )

    # Save button
    if st.button("Save Advanced Settings"):
        # Update settings
        updated_settings = settings.copy()
        updated_settings["max_retries"] = max_retries
        updated_settings["leading_silence_ms"] = leading_silence_ms
        updated_settings["trailing_silence_ms"] = trailing_silence_ms

        # Map device selection back to internal value
        if device == "CPU":
            updated_settings["device"] = "cpu"
        elif device == "GPU (CUDA)":
            updated_settings["device"] = "cuda"
        else:
            updated_settings["device"] = "mps"

        update_settings(updated_settings)
        st.session_state.settings_updated = True
        st.rerun()


def show_cache_settings(settings):
    """
    Display cache settings.

    Args:
        settings (dict): Current application settings
    """
    st.subheader("Cache Settings")

    # Cache toggle
    cache_enabled = st.checkbox(
        "Enable Results Caching",
        value=settings.get("cache_results", True),
        help="Cache processed results to avoid reprocessing the same audio files",
    )

    # Display cache statistics
    cache_count = len(st.session_state.get("audio_cache", {}))
    st.info(f"Current cache contains {cache_count} audio processing results")

    # Cache management buttons
    col1, col2 = st.columns(2)

    with col1:
        if st.button("Clear Cache", type="primary", disabled=cache_count == 0):
            if clear_cache():
                st.success("Cache cleared successfully!")
                st.session_state.settings_updated = True
                st.rerun()
            else:
                st.error("Failed to clear cache")

    with col2:
        if st.button("Save Cache Settings"):
            # Update settings
            updated_settings = settings.copy()
            updated_settings["cache_results"] = cache_enabled
            update_settings(updated_settings)
            st.session_state.settings_updated = True
            st.rerun()


def show_labeling_page():
    """
    Display transcription and segmentation page.
    """
    # Apply custom CSS
    st.markdown(load_css(), unsafe_allow_html=True)
    
    # Page header
    st.title(APP_TITLE)
    st.markdown("--------------")
    st.header("Transcription & Segmentation")

    # Get current settings
    settings = get_current_settings()

    # Sidebar navigation
    st.sidebar.title("Menu")
    st.sidebar.markdown(
        """
        <div class="sidebar-menu">
            <a href="/">📄 Home</a>
            <a href="/TTS_Labeling" class="active">🎤 Transcription & Segmentation</a>
            <a href="/Transcript_view">👁️ View Results</a>
        </div>
        """, 
        unsafe_allow_html=True
    )

    # Introduction in expander
    with st.expander("Introduction"):
        st.markdown(
            """
            **This tool helps you:**
            - Transcribe audio content using Google Gemini AI
            - Segment audio by sentences/paragraphs
            - Export results as JSON or separate audio and text files
            
            **How to use:**
            1. Upload audio file (WAV, MP3 format)
            2. Select processing mode (transcription only or transcription & segmentation)
            3. Click process button and wait for results
            4. View and download results
            
            **Note:** Processing time depends on audio length and processing options.
            """
        )

    # Settings Section
    st.markdown("-------------")
    st.header("⚙️ Settings")

    # Create tabs for different setting categories
    tab_general, tab_api, tab_advanced, tab_cache = st.tabs(
        ["General", "API", "Advanced", "Cache"]
    )

    with tab_general:
        show_general_settings(settings)

    with tab_api:
        show_api_settings(settings)

    with tab_advanced:
        show_advanced_settings(settings)

    with tab_cache:
        show_cache_settings(settings)

    # Show success message if settings were updated
    if "settings_updated" in st.session_state and st.session_state.settings_updated:
        st.success("Settings updated successfully!", icon="✅")
        # Note: We don't reset the flag here as it's handled after the form

    # Upload and processing section
    st.markdown("-------------")
    st.header("🔊 Process Audio")
    
    with st.form("upload_form"):
        # Upload audio file
        uploaded_file = st.file_uploader(
            "Upload audio file", type=SUPPORTED_AUDIO_FORMATS
        )

        # Select processing mode
        processing_mode = st.radio(
            "Processing mode",
            PROCESSING_MODES,
            index=DEFAULT_PROCESSING_MODE_INDEX,
            help="Choose transcription only for text, or transcription & segmentation for individual audio files for each sentence",
        )

        # Submit button
        submitted = st.form_submit_button(BUTTON_PROCESS_AUDIO)

    # Display notification if settings were updated
    if "settings_updated" in st.session_state and st.session_state.settings_updated:
        st.sidebar.success(
            "Settings automatically updated. Other pages will use these new settings.",
            icon="✅",
        )
        # Reset flag
        st.session_state.settings_updated = False

    # Process when user submits form
    if submitted and uploaded_file is not None:
        # Results section
        st.header("🔍 Processing Results")
        
        process_uploaded_audio(
            uploaded_file,
            processing_mode,
        )

    # Display results if available
    if (
        "transcription_results" in st.session_state
        and st.session_state.transcription_results
    ):
        # Results section
        st.markdown("-------------")
        st.header("📋 Transcription Results")
        
        # Show detailed results for each segment
        show_transcript_details(
            st.session_state.transcription_results,
            page_state_key="labeling_page_number",
        )
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown(APP_FOOTER)


def process_uploaded_audio(
    uploaded_file: UploadedFile,
    processing_mode: str,
):
    """
    Process uploaded audio file.

    Args:
        uploaded_file: Uploaded audio file
        processing_mode: Processing mode ("Transcription only" or "Transcription & Segmentation")
    """
    try:
        # Display file info and processing status
        st.info(f"Processing file: {uploaded_file.name}")
        progress_bar = st.progress(0)
        status_text = st.empty()

        # Read audio content
        audio_bytes = uploaded_file.getvalue()

        # Determine whether to segment based on processing_mode
        do_alignment = processing_mode == "Transcription & Segmentation"

        # Check cache if cache_results = True
        settings = get_current_settings()
        use_cache = settings.get("cache_results", True)
        cache_used = False
        combined_results = None

        # Get settings values
        model = settings.get("model", DEFAULT_MODEL)
        max_retries = settings.get("max_retries", 3)
        leading_silence_ms = settings.get("leading_silence_ms", 100)
        trailing_silence_ms = settings.get("trailing_silence_ms", 100)
        device = settings.get("device", DEFAULT_DEVICE)

        if use_cache:
            # Create cache key from file content and processing parameters
            cache_key = generate_cache_key(
                audio_bytes,
                processing_mode,
                model,
                leading_silence_ms if do_alignment else 0,
                trailing_silence_ms if do_alignment else 0,
            )

            # Check cache in session state
            if "audio_cache" not in st.session_state:
                st.session_state.audio_cache = {}

            # If results are already in cache, use them
            if cache_key in st.session_state.audio_cache:
                status_text.text("Loading results from cache...")
                progress_bar.progress(40)

                # Get results from cache
                combined_results = st.session_state.audio_cache[cache_key]
                cache_used = True

                progress_bar.progress(80)
                status_text.text("Found results in cache!")
                time.sleep(0.5)  # Brief pause to show message

        # If not in cache or not using cache, process normally
        if not cache_used:
            # Create BytesIO from bytes for audio processing
            audio_buffer = BytesIO(audio_bytes)

            status_text.text(f"Processing audio using {model} + Whisper-large-v3...")
            progress_bar.progress(20)

            if do_alignment:
                # Process audio with segmentation
                # Get API key from settings
                api_key = settings.get("api_key", None)

                # Show API key source info
                if settings.get("api_key"):
                    st.info("Using API key from settings")
                else:
                    st.info("Using API key from environment variable (if set)")

                # Get cached AudioProcessor instance
                processor = get_processor(
                    api_key=api_key,
                    transcription_model=model,
                    whisper_model="large-v3",
                    device=device,  # Use selected device (cpu, cuda, mps)
                )

                # Process audio
                combined_results = processor.process_audio(
                    audio_file=audio_buffer,
                    leading_silence_ms=leading_silence_ms,
                    trailing_silence_ms=trailing_silence_ms,
                    save_folder=None,
                    max_retries=max_retries,
                    language="en",  # Default to English
                )

                progress_bar.progress(80)
                status_text.text("Processing complete! Preparing results...")

                # Save to cache if caching is enabled
                if use_cache and not cache_used:
                    st.session_state.audio_cache[cache_key] = combined_results

            else:
                # Transcription only
                # Get API key from settings
                api_key = settings.get("api_key", None)

                # Show API key source info
                if settings.get("api_key"):
                    st.info("Using API key from settings")
                else:
                    st.info("Using API key from environment variable (if set)")

                # Get cached AudioTranscriber instance
                transcriber = get_transcriber(api_key=api_key, model=model)

                combined_results = transcriber.transcribe(
                    file=audio_buffer, max_retries=max_retries
                )

                progress_bar.progress(80)
                status_text.text("Transcription complete! Preparing results...")

                # Save to cache if caching is enabled
                if use_cache and not cache_used:
                    st.session_state.audio_cache[cache_key] = combined_results

        # Save results to session state for access by other pages
        st.session_state.transcription_results = combined_results

        # Display cache statistics if using cache
        if use_cache:
            cache_count = len(st.session_state.get("audio_cache", {}))
            cache_status = (
                "used existing results" if cache_used else "saved new results"
            )
            st.sidebar.info(f"Cache: {cache_count} results ({cache_status})")

        # Complete
        progress_bar.progress(100)
        status_text.text("Processing complete!")

        # Success message
        st.success("Audio processed successfully!")

    except Exception as e:
        import traceback
        traceback.print_exc()
        st.error(f"An error occurred: {str(e)}")
        logger.error(f"Error processing audio: {str(e)}", exc_info=True)


if __name__ == "__main__":
    show_labeling_page()
