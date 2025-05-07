"""
Transcript viewer page for the Audio Transcription demo application.
"""

import logging
import pandas as pd
import streamlit as st
from typing import List, Dict, Any

from demo.utils.constants import APP_TITLE
from demo.utils.display_utils import show_transcript_details
from demo.utils.zip_utils import add_zip_download_button

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def show_transcript_view_page():
    """
    Display transcript viewer page.
    """
    st.title(f"{APP_TITLE} - Transcript Viewer")
    
    # Check if transcription results exist in session state
    if "transcription_results" not in st.session_state or not st.session_state.transcription_results:
        st.warning("""
        No transcription results found. 
        
        Please go to the Transcription & Segmentation page to process an audio file first.
        """)
        
        # Add button to navigate to the labeling page
        if st.button("Go to Transcription & Segmentation"):
            js = """
            <script>
                window.parent.open('/labeling_page', '_self');
            </script>
            """
            st.components.v1.html(js, height=0)
        
        return
    
    # Display overview of the transcription results
    show_transcription_overview(st.session_state.transcription_results)
    
    # Show full transcript
    show_full_transcript(st.session_state.transcription_results)
    
    # Show detailed transcript with audio playback
    st.subheader("Detailed Segments")
    show_transcript_details(
        st.session_state.transcription_results, 
        page_state_key="view_page_number",
        items_per_page=10
    )

def show_transcription_overview(transcription_results: List[Dict[str, Any]]):
    """
    Display overview information about the transcription results.
    
    Args:
        transcription_results: List of transcription result dictionaries
    """
    # Count segments and total text length
    segment_count = len(transcription_results)
    total_text = " ".join([item.get("text", "") for item in transcription_results])
    word_count = len(total_text.split())
    char_count = len(total_text)
    
    # Check if results have been segmented (contain audio chunks)
    has_audio = any("audio" in item for item in transcription_results)
    
    # Display overview metrics
    st.subheader("Transcription Overview")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Segments", f"{segment_count}")
    col2.metric("Words", f"{word_count}")
    col3.metric("Characters", f"{char_count}")
    
    # Add ZIP download button if audio segments are available
    if has_audio:
        st.markdown("---")
        add_zip_download_button(
            transcription_results,
            button_text="Download All Audio Segments as ZIP",
            include_text=True
        )

def show_full_transcript(transcription_results: List[Dict[str, Any]]):
    """
    Display the full transcript as continuous text.
    
    Args:
        transcription_results: List of transcription result dictionaries
    """
    # Extract text from all segments
    full_text = "\n".join([item.get("text", "") for item in transcription_results if "text" in item])
    
    # Display in expander
    with st.expander("View Full Transcript", expanded=False):
        st.text_area(
            label="Full transcript",
            value=full_text,
            height=300,
            disabled=False,  # Allow copying
            key="full_transcript"
        )
        
        # Add download button for the full transcript
        st.download_button(
            label="Download Full Transcript",
            data=full_text,
            file_name="full_transcript.txt",
            mime="text/plain"
        )
        
        # Show visual representations
        show_visual_data(transcription_results)

def show_visual_data(transcription_results: List[Dict[str, Any]]):
    """
    Show visual representations of the transcription data.
    
    Args:
        transcription_results: List of transcription result dictionaries
    """
    # Check if we have enough data to visualize
    if len(transcription_results) <= 1:
        return
        
    # Create DataFrame for visualization
    df = pd.DataFrame({
        "Segment": [f"Segment {i+1}" for i in range(len(transcription_results))],
        "Text Length": [len(item.get("text", "")) for item in transcription_results],
    })
    
    # Add description column if available
    if any("description" in item for item in transcription_results):
        df["Has Description"] = [1 if "description" in item else 0 for item in transcription_results]
    
    # Display simple bar chart
    st.subheader("Text Length by Segment")
    st.bar_chart(
        df.set_index("Segment")["Text Length"],
        use_container_width=True
    )

if __name__ == "__main__":
    show_transcript_view_page()
