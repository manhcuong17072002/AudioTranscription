"""
Homepage for the Audio Transcription demo application.
"""

import logging
import streamlit as st
import plotly.graph_objects as go

from demo.utils.constants import APP_TITLE, APP_PAGE_TITLE, APP_FOOTER
from demo.utils.cache_utils import render_cache_ui

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Set page title and info
st.set_page_config(page_title=APP_PAGE_TITLE, layout="wide")

def render_hero_section():
    """Display hero section with gradient background"""
    with st.container():
        # Use container with gradient background
        st.markdown(
            """
            <style>
            .hero-container {
                background: linear-gradient(to right, #5D8BF4, #9AC5F4);
                padding: 2rem;
                border-radius: 10px;
                color: white;
                text-align: center;
                margin-bottom: 2rem;
            }
            </style>
            """, 
            unsafe_allow_html=True
        )
        
        # Only use HTML for container, use Streamlit native for content
        st.title(APP_TITLE)
        st.markdown("### High-precision audio transcription and segmentation solution")
        st.markdown("Advanced AI technology · Smart segmentation · Easy to use")
        
        cols = st.columns([1, 2, 1])
        with cols[0]:
            # Add navigation to transcription page when button is clicked
            if st.button("Get Started ➡️", use_container_width=True):
                js = """
                <script>
                    window.parent.open('/TTS_Labeling', '_self');
                </script>
                """
                st.components.v1.html(js, height=0)
        
        st.markdown('</div>', unsafe_allow_html=True)

def render_feature_cards():
    """Display key features as cards"""
    st.header("Key Features")
    
    # Define data for cards
    features_row1 = [
        {
            "icon": "🎯",
            "title": "Precise Transcription", 
            "desc": "Use Google Gemini API to transcribe audio with high accuracy, supporting various voices and languages."
        },
        {
            "icon": "✂️",
            "title": "Smart Segmentation", 
            "desc": "Automatically analyze and split audio into meaningful segments by sentences or paragraphs."
        },
        {
            "icon": "📦",
            "title": "Flexible Output", 
            "desc": "Easily export results in multiple formats: JSON, plain text, or ZIP containing audio + text."
        }
    ]
    
    features_row2 = [
        {
            "icon": "🎧",
            "title": "Listen to Segments", 
            "desc": "View and listen to each segmented audio to verify transcription quality directly."
        },
        {
            "icon": "⚙️",
            "title": "Customizable Settings", 
            "desc": "Adjust transcription and segmentation parameters according to your project's specific needs."
        },
        {
            "icon": "💾",
            "title": "Smart Caching", 
            "desc": "Cache system helps store and reuse results, saving processing time."
        }
    ]
    
    # Display first row of feature cards
    cols = st.columns(len(features_row1))
    for i, col in enumerate(cols):
        with col:
            with st.container():
                st.markdown(f"### {features_row1[i]['icon']} {features_row1[i]['title']}")
                st.write(features_row1[i]['desc'])
    
    # Display second row of feature cards
    cols = st.columns(len(features_row2))
    for i, col in enumerate(cols):
        with col:
            with st.container():
                st.markdown(f"### {features_row2[i]['icon']} {features_row2[i]['title']}")
                st.write(features_row2[i]['desc'])

def render_metrics():
    """Display information as metrics"""
    st.header("Performance & Capabilities")
    
    col1, col2, col3 = st.columns(3)
    col1.metric(label="Accuracy", value="98%")
    col2.metric(label="Processing Time", value="<30s")
    col3.metric(label="Supported Formats", value="2", help="WAV and MP3")

def render_workflow_diagram():
    """Display workflow diagram using Plotly"""
    st.subheader("Processing Workflow")
    
    # Create workflow diagram with Plotly
    # Nodes and edges data
    nodes = ["Upload Audio", "Transcribe with<br>Gemini AI", "Segment?", 
             "Context Analysis", "Text-Audio<br>Alignment", 
             "Cut Audio<br>by Sentence", "Segmentation<br>Results", "Text<br>Results"]
    
    # Create Sankey diagram
    fig = go.Figure(go.Sankey(
        arrangement = "snap",
        node = dict(
            pad = 20,
            thickness = 20,
            line = dict(color = "black", width = 0.5),
            label = nodes,
            color = ["#5D8BF4", "#5D8BF4", "#FF6B6B", "#5D8BF4", 
                     "#5D8BF4", "#5D8BF4", "#4CAF50", "#4CAF50"]
        ),
        link = dict(
            source = [0, 1, 2, 2, 3, 4, 5],
            target = [1, 2, 3, 7, 4, 5, 6],
            value = [10, 10, 7, 3, 7, 7, 7],
            color = ["rgba(93, 139, 244, 0.4)", "rgba(93, 139, 244, 0.4)", 
                    "rgba(93, 139, 244, 0.4)", "rgba(93, 139, 244, 0.4)", 
                    "rgba(93, 139, 244, 0.4)", "rgba(93, 139, 244, 0.4)", 
                    "rgba(93, 139, 244, 0.4)"]
        )
    ))
    
    fig.update_layout(
        title_text="Audio Data Processing Flow", 
        font=dict(size=14),
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)

def render_usage_guide():
    """Display usage guide with icons"""
    st.header("How to Use")
    
    # CSS for steps container
    st.markdown(
        """
        <style>
        .steps-container {
            background-color: #f1f3f9;
            border-radius: 10px;
            padding: 20px;
            margin: 10px 0;
        }
        </style>
        """, 
        unsafe_allow_html=True
    )
    
    # Define steps
    steps = [
        {"icon": "📁", "title": "Upload audio file", 
         "desc": "Supports WAV, MP3 formats"},
        {"icon": "⚙️", "title": "Select processing mode", 
         "desc": "Transcription only or transcription + segmentation"},
        {"icon": "🔧", "title": "Adjust parameters", 
         "desc": "Customize processing parameters if needed"},
        {"icon": "▶️", "title": "Process and wait", 
         "desc": "System will process audio and return text"},
        {"icon": "💾", "title": "View and download", 
         "desc": "View results and download in desired format"}
    ]
        
    cols = st.columns(len(steps))
    for i, col in enumerate(cols):
        with col:
            st.subheader(f"{steps[i]['icon']} {i+1}")
            st.markdown(f"**{steps[i]['title']}**")
            st.caption(steps[i]['desc'])
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_introduction():
    """Display introduction section"""
    st.header("Introduction")
    
    # CSS for info section
    st.markdown(
        """
        <style>
        .info-section {
            border-left: 4px solid #5D8BF4;
            padding-left: 15px;
        }
        </style>
        """, 
        unsafe_allow_html=True
    )
    
    # Use columns for better layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('<div class="info-section">', unsafe_allow_html=True)
        st.markdown("""
        This tool provides high-accuracy audio transcription and segmentation capabilities 
        using Google Gemini API. The system is designed to support the creation of quality data 
        for text-to-speech and speech-to-text systems.
        
        With a user-friendly interface and flexible options, this tool is suitable for both 
        individual users and businesses requiring high-quality audio transcription and segmentation.
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        # Create card showing benefits with Streamlit native
        with st.container():
            st.markdown("### Why Choose Us?")
            st.markdown("""
            - ✅ High accuracy
            - ⚡ Fast processing
            - 🔧 Flexible customization
            - 💼 Support for common formats
            """)

def main():
    """Main function to display homepage"""
    # Sidebar options
    st.sidebar.title("Menu")
    
    st.sidebar.markdown("""
    - [📄 Home](/)
    - [🎤 Transcription & Segmentation](/TTS_Labeling)
    - [👁️ View Results](/Transcript_view)
    """)
        
    # Display cache information
    render_cache_ui()
    
    # Display UI components
    render_hero_section()
    render_introduction()  # Moved introduction up
    render_feature_cards()
    render_metrics()
    render_workflow_diagram()
    render_usage_guide()
        
    # Footer with inline style instead of CSS class
    st.sidebar.markdown("---")
    st.sidebar.markdown(
        f"""
        <div style="
            background-color: #f8f9fa;
            padding: 1rem;
            border-radius: 0.5rem;
            border-left: 4px solid #5D8BF4;
            margin-top: 1rem;
            font-size: 0.9rem;
            color: #666;
        ">
            {APP_FOOTER}
        </div>
        """, 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
