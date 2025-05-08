"""
Display utilities for the Audio Transcription demo application.
"""

import base64
import json
import pandas as pd
import streamlit as st

def show_transcript_details(
    transcription_results, page_state_key="page_number", items_per_page=5
):
    """
    Display detailed transcription results with pagination and audio playback.
    
    Args:
        transcription_results: List of transcription result dictionaries
        page_state_key: Key for session state to track pagination 
        items_per_page: Number of items to show per page
    """
    if not transcription_results:
        st.warning("No transcription results to display")
        return

    # Initialize pagination state if not exists
    if page_state_key not in st.session_state:
        st.session_state[page_state_key] = 0

    # Calculate total pages
    total_items = len(transcription_results)
    total_pages = (total_items + items_per_page - 1) // items_per_page  # Ceiling division
    
    # Create pagination controls
    col1, col2, col3 = st.columns([5, 5, 1])
    
    with col1:
        if st.button("◀ Previous", key=f"prev_{page_state_key}", disabled=st.session_state[page_state_key] <= 0):
            st.session_state[page_state_key] -= 1
    
    with col2:
        st.write(f"Page {st.session_state[page_state_key] + 1} of {max(1, total_pages)}")
    
    with col3:
        if st.button("Next ▶", key=f"next_{page_state_key}", disabled=st.session_state[page_state_key] >= total_pages - 1):
            st.session_state[page_state_key] += 1
    
    # Ensure page is in valid range
    current_page = min(max(0, st.session_state[page_state_key]), max(0, total_pages - 1))
    
    # Display items for current page
    start_idx = current_page * items_per_page
    end_idx = min(start_idx + items_per_page, total_items)
    
    # Check if the results have been segmented (contain audio chunks)
    has_audio = any("audio" in item for item in transcription_results)
    
    # Display each item
    for i, item in enumerate(transcription_results[start_idx:end_idx], start=start_idx):
        with st.expander(f"Segment {i+1}", expanded=True):
            # Display text
            if "text" in item:
                st.markdown(f"**Text**: {item['text']}")
            
            # Display voice description if available
            if "description" in item:
                st.markdown(f"**Voice description**: {item['description']}")
            
            # If we have audio data
            if "audio" in item:
                # Convert audio to WAV format for playback
                audio_data = item["audio"].export(format="wav").read()
                
                # Create playback control
                st.audio(audio_data)
                
                # Provide download button for audio
                filename = item.get("filename", f"segment_{i+1}.wav")
                st.download_button(
                    label="Download Audio",
                    data=audio_data,
                    file_name=filename,
                    mime="audio/wav",
                    key=f"download_audio_{i}"
                )
            
            # Show filename if available
            if "filename" in item and "audio" not in item:
                st.text(f"Filename: {item['filename']}")
    
    # Add export buttons
    st.markdown("---")
    st.subheader("Export Options")
    
    col1, col2 = st.columns([7, 1])
    
    # Export as JSON option
    with col1:
        # Create a serializable version of the results
        serializable_results = []
        
        for item in transcription_results:
            # Create a copy without audio data (can't be serialized)
            serializable_item = {k: v for k, v in item.items() if k != 'audio'}
            serializable_results.append(serializable_item)
        
        # Create JSON string
        json_str = json.dumps(serializable_results, indent=2)
        
        # Download button for JSON
        st.download_button(
            label="Download as JSON",
            data=json_str,
            file_name="transcription_results.json",
            mime="application/json"
        )
    
    # Export as CSV option
    with col2:
        # Convert to dataframe (excluding audio)
        df_data = []
        
        for i, item in enumerate(transcription_results):
            row = {
                "segment": i+1,
                "text": item.get("text", ""),
                "description": item.get("description", "")
            }
            
            if "filename" in item:
                row["filename"] = item["filename"]
                
            df_data.append(row)
        
        df = pd.DataFrame(df_data)
        
        # Download button for CSV
        csv_data = df.to_csv(index=False)
        st.download_button(
            label="Download as CSV",
            data=csv_data,
            file_name="transcription_results.csv",
            mime="text/csv"
        )

def get_download_link(data, filename, text):
    """
    Generate a download link for a file.
    
    Args:
        data: File data
        filename: Name of the file to download
        text: Text to display for the download link
        
    Returns:
        str: HTML download link
    """
    b64 = base64.b64encode(data).decode()
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="{filename}">{text}</a>'
    return href
