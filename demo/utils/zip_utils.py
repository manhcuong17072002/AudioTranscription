"""
ZIP utilities for the Audio Transcription demo application.
"""

import io
import os
import zipfile
import streamlit as st
import tempfile

def create_zip_from_files(file_paths, zip_name="audio_segments.zip"):
    """
    Create a ZIP file from a list of file paths.
    
    Args:
        file_paths (list): List of file paths to include in the ZIP
        zip_name (str): Name of the output ZIP file
        
    Returns:
        bytes: ZIP file content as bytes
    """
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in file_paths:
            # Skip if file doesn't exist
            if not os.path.exists(file_path):
                continue
                
            # Get the filename without full path
            filename = os.path.basename(file_path)
            
            # Add file to the ZIP
            zipf.write(file_path, arcname=filename)
    
    zip_buffer.seek(0)
    return zip_buffer.getvalue()

def create_zip_from_audio_chunks(audio_chunks, include_text=True):
    """
    Create a ZIP file from audio chunks (segments).
    
    Args:
        audio_chunks (list): List of dictionaries containing audio segments
        include_text (bool): Whether to include text files alongside audio files
        
    Returns:
        bytes: ZIP file content as bytes
    """
    # Create a temporary directory to store files
    with tempfile.TemporaryDirectory() as temp_dir:
        file_paths = []
        
        # Save each audio segment to the temporary directory
        for i, chunk in enumerate(audio_chunks):
            if "audio" in chunk:
                # Get the filename from the chunk or generate one
                filename = chunk.get("filename", f"segment_{i+1}.wav")
                file_path = os.path.join(temp_dir, filename)
                
                # Export audio to file
                chunk["audio"].export(file_path, format="wav")
                file_paths.append(file_path)
                
                # If including text and we have text, create a text file
                if include_text and "text" in chunk:
                    text_filename = os.path.splitext(filename)[0] + ".txt"
                    text_path = os.path.join(temp_dir, text_filename)
                    
                    with open(text_path, "w", encoding="utf-8") as f:
                        f.write(chunk["text"])
                    
                    file_paths.append(text_path)
        
        # Create ZIP file
        return create_zip_from_files(file_paths, "audio_segments.zip")

def add_zip_download_button(audio_chunks, button_text="Download All Segments as ZIP", include_text=True):
    """
    Add a download button for a ZIP file containing audio segments.
    
    Args:
        audio_chunks (list): List of dictionaries containing audio segments
        button_text (str): Text to display on the button
        include_text (bool): Whether to include text files alongside audio files
        
    Returns:
        bool: True if button was clicked
    """
    if not audio_chunks or not any("audio" in chunk for chunk in audio_chunks):
        st.warning("No audio segments available to download")
        return False
    
    # Create ZIP file
    zip_data = create_zip_from_audio_chunks(audio_chunks, include_text)
    
    # Add download button
    return st.download_button(
        label=button_text,
        data=zip_data,
        file_name="audio_segments.zip",
        mime="application/zip"
    )
