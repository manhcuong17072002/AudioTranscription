"""
Cache utilities for the Audio Transcription demo application.
"""

import json
import hashlib
import streamlit as st

def generate_cache_key(audio_bytes, processing_mode, model, leading_silence_ms=0, trailing_silence_ms=0):
    """
    Generate a unique cache key based on audio content and processing parameters.
    
    Args:
        audio_bytes: Audio content as bytes
        processing_mode: Processing mode selection
        model: Model name used for processing
        leading_silence_ms: Leading silence in milliseconds
        trailing_silence_ms: Trailing silence in milliseconds
        
    Returns:
        str: Unique hash key for caching
    """
    # Create hash from audio content (first 1MB for large files)
    audio_hash = hashlib.md5(audio_bytes[:1024*1024]).hexdigest()
    
    # Combine with processing parameters to create unique key
    params_string = f"{processing_mode}_{model}_{leading_silence_ms}_{trailing_silence_ms}"
    combined_key = f"{audio_hash}_{params_string}"
    
    # Return MD5 hash of the combined key
    return hashlib.md5(combined_key.encode()).hexdigest()

def get_current_settings():
    """
    Get current application settings from session state.
    Initialize with defaults if not yet set.
    
    Returns:
        dict: Current settings
    """
    if "app_settings" not in st.session_state:
        # Initialize default settings
        st.session_state.app_settings = {
            "cache_results": True,
            "model": "gemini-2.0-flash",
            "max_retries": 3,
            "leading_silence_ms": 100,
            "trailing_silence_ms": 100,
        }
    
    return st.session_state.app_settings

def update_settings(settings):
    """
    Update application settings in session state.
    
    Args:
        settings (dict): New settings to update
    """
    current_settings = get_current_settings()
    current_settings.update(settings)
    st.session_state.app_settings = current_settings

def clear_cache():
    """Clear cached results from session state."""
    if "audio_cache" in st.session_state:
        st.session_state.audio_cache = {}
        return True
    return False

def render_cache_ui():
    """
    Render cache control UI in the sidebar.
    
    Returns:
        bool: True if cache settings were changed
    """
    settings = get_current_settings()
    
    st.sidebar.subheader("Cache Settings")
    
    # Cache toggle
    cache_enabled = st.sidebar.checkbox(
        "Enable caching",
        value=settings.get("cache_results", True),
        help="Cache processed results to avoid reprocessing the same audio"
    )
    
    # Update cache setting if changed
    if cache_enabled != settings.get("cache_results", True):
        settings["cache_results"] = cache_enabled
        update_settings(settings)
        return True
    
    # Cache info and clear button
    if "audio_cache" in st.session_state:
        cache_count = len(st.session_state.audio_cache)
        st.sidebar.caption(f"Cache contains {cache_count} results")
        
        if cache_count > 0 and st.sidebar.button("Clear cache"):
            if clear_cache():
                st.sidebar.success("Cache cleared!")
                return True
    else:
        st.sidebar.caption("Cache is empty")
    
    return False
