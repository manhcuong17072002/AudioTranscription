"""
Homepage for the Audio Transcription demo application.
"""

import logging
import streamlit as st
import plotly.graph_objects as go

from demo.utils.constants import APP_TITLE, APP_PAGE_TITLE, APP_FOOTER
from demo.utils.cache_utils import render_cache_ui
from demo.utils.custom_styles import load_css

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Set page title and info
st.set_page_config(page_title=APP_PAGE_TITLE, layout="wide")


def render_hero_section():
    """Display hero section with gradient background"""

    # Content inside hero container
    st.markdown(f"<h1>{APP_TITLE}</h1>", unsafe_allow_html=True)
    st.markdown(
        "<h3>High-precision audio transcription and segmentation solution</h3>",
        unsafe_allow_html=True,
    )

    # Feature tags
    st.markdown(
        """
        <div style="display: flex; justify-content: center; gap: 1rem; margin-bottom: 2rem;">
            <span style="background: rgba(255,255,255,0.2); padding: 5px 10px; border-radius: 20px; font-size: 0.9rem;">Advanced AI technology</span>
            <span style="background: rgba(255,255,255,0.2); padding: 5px 10px; border-radius: 20px; font-size: 0.9rem;">Smart segmentation</span>
            <span style="background: rgba(255,255,255,0.2); padding: 5px 10px; border-radius: 20px; font-size: 0.9rem;">Easy to use</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Button row
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


def render_feature_cards():
    """Display key features as cards"""
    # Define data for cards
    features_row1 = [
        {
            "icon": "🎯",
            "title": "Precise Transcription",
            "desc": "Use Google Gemini API to transcribe audio with high accuracy, supporting various voices and languages.",
        },
        {
            "icon": "✂️",
            "title": "Smart Segmentation",
            "desc": "Automatically analyze and split audio into meaningful segments by sentences or paragraphs.",
        },
        {
            "icon": "📦",
            "title": "Flexible Output",
            "desc": "Easily export results in multiple formats: JSON, plain text, or ZIP containing audio + text.",
        },
    ]

    features_row2 = [
        {
            "icon": "🎧",
            "title": "Listen to Segments",
            "desc": "View and listen to each segmented audio to verify transcription quality directly.",
        },
        {
            "icon": "⚙️",
            "title": "Customizable Settings",
            "desc": "Adjust transcription and segmentation parameters according to your project's specific needs.",
        },
        {
            "icon": "💾",
            "title": "Smart Caching",
            "desc": "Cache system helps store and reuse results, saving processing time.",
        },
    ]

    # Display first row of feature cards using custom feature-card class
    cols = st.columns(len(features_row1))
    for i, col in enumerate(cols):
        with col:
            st.markdown(
                f"""
                <div class="feature-card">
                    <h3>{features_row1[i]['icon']} {features_row1[i]['title']}</h3>
                    <p>{features_row1[i]['desc']}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # Display second row of feature cards
    cols = st.columns(len(features_row2))
    for i, col in enumerate(cols):
        with col:
            st.markdown(
                f"""
                <div class="feature-card">
                    <h3>{features_row2[i]['icon']} {features_row2[i]['title']}</h3>
                    <p>{features_row2[i]['desc']}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_metrics():
    """Display information as metrics"""
    # Define metrics data
    metrics = [
        {
            "icon": "🎯",
            "value": "98%",
            "label": "Accuracy",
            "desc": "High precision transcription",
        },
        {
            "icon": "⚡",
            "value": "<10s",
            "label": "Processing Time",
            "desc": "Fast audio processing",
        },
        {
            "icon": "🔊",
            "value": "2",
            "label": "Supported Formats",
            "desc": "WAV and MP3 support",
        },
    ]

    # Display metrics using custom metric-card class
    cols = st.columns(len(metrics))
    for i, col in enumerate(cols):
        with col:
            st.markdown(
                f"""
                <div class="metric-card">
                    <h3> {metrics[i]['icon']} {metrics[i]['label']}: {metrics[i]['value']}</h3>
                    <p> {metrics[i]['desc']} </p>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_workflow_diagram():
    """Display workflow diagram using Plotly"""
    # Create workflow diagram with Plotly
    # Nodes and edges data
    nodes = [
        "Upload Audio",
        "Transcribe with<br>Gemini AI",
        "Segment?",
        "Context Analysis",
        "Text-Audio<br>Alignment",
        "Cut Audio<br>by Sentence",
        "Segmentation<br>Results",
        "Text<br>Results",
    ]

    # Create Sankey diagram
    fig = go.Figure(
        go.Sankey(
            arrangement="snap",
            node=dict(
                pad=20,
                thickness=20,
                line=dict(color="black", width=0.5),
                label=nodes,
                color=[
                    "#5D8BF4",
                    "#5D8BF4",
                    "#FF6B6B",
                    "#5D8BF4",
                    "#5D8BF4",
                    "#5D8BF4",
                    "#4CAF50",
                    "#4CAF50",
                ],
            ),
            link=dict(
                source=[0, 1, 2, 2, 3, 4, 5],
                target=[1, 2, 3, 7, 4, 5, 6],
                value=[10, 10, 7, 3, 7, 7, 7],
                color=[
                    "rgba(93, 139, 244, 0.4)",
                    "rgba(93, 139, 244, 0.4)",
                    "rgba(93, 139, 244, 0.4)",
                    "rgba(93, 139, 244, 0.4)",
                    "rgba(93, 139, 244, 0.4)",
                    "rgba(93, 139, 244, 0.4)",
                    "rgba(93, 139, 244, 0.4)",
                ],
            ),
        )
    )

    fig.update_layout(
        title_text="Audio Data Processing Flow", font=dict(size=14), height=400
    )

    st.plotly_chart(fig, use_container_width=True)


def render_usage_guide():
    """Display usage guide with icons"""

    # Define steps
    steps = [
        {
            "icon": "📁",
            "title": "Upload audio file",
            "desc": "Supports WAV, MP3 formats",
        },
        {
            "icon": "⚙️",
            "title": "Select mode",
            "desc": "Transcription only or transcription + segmentation",
        },
        {
            "icon": "🔧",
            "title": "Adjust parameters",
            "desc": "Customize processing parameters if needed",
        },
        {
            "icon": "▶️",
            "title": "Process and wait",
            "desc": "System will process audio and return text",
        },
        {
            "icon": "💾",
            "title": "View and download",
            "desc": "View results and download in desired format",
        },
    ]

    # Display steps using step-card class
    cols = st.columns(len(steps))
    for i, col in enumerate(cols):
        with col:
            st.markdown(
                f"""
                <div class="step-card">
                    <div class="step-number">{i+1}</div>
                    <h3>{steps[i]['icon']} {steps[i]['title']}</h3>
                    <p>{steps[i]['desc']}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )


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
        unsafe_allow_html=True,
    )

    # Use columns for better layout
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown('<div class="info-section">', unsafe_allow_html=True)
        st.markdown(
            """
        This tool provides high-accuracy audio transcription and segmentation capabilities 
        using Google Gemini API. The system is designed to support the creation of quality data 
        for text-to-speech and speech-to-text systems.
        
        With a user-friendly interface and flexible options, this tool is suitable for both 
        individual users and businesses requiring high-quality audio transcription and segmentation.
        """
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        # Create card showing benefits with Streamlit native
        with st.container():
            st.markdown("### Why Choose Us?")
            st.markdown(
                """
            - ✅ High accuracy
            - ⚡ Fast processing
            - 🔧 Flexible customization
            - 💼 Support for common formats
            """
            )


def main():
    """Main function to display homepage"""
    # Apply custom CSS
    st.markdown(load_css(), unsafe_allow_html=True)

    # Sidebar options with better styling
    st.sidebar.title("Menu")

    # Navigation menu with custom styling
    st.sidebar.markdown(
        """
        <div class="sidebar-menu">
            <a href="/" class="active">📄 Home</a>
            <a href="/TTS_Labeling">🎤 Transcription & Segmentation</a>
            <a href="/Transcript_view">👁️ View Results</a>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.sidebar.markdown('<hr class="custom-divider">', unsafe_allow_html=True)
    # Display cache information
    render_cache_ui()

    # Display UI components
    render_hero_section()
    st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)

    # Custom container for introduction
    render_introduction()

    # Section divider
    st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)

    # Section title with icon
    st.header("✨Key Features")
    render_feature_cards()

    # Section divider
    st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)

    st.header("📊 Performance Metrics")
    render_metrics()

    # Section divider
    st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)

    # Section title with icon
    st.header("🔄 Processing Workflow")
    render_workflow_diagram()

    # Section divider
    st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)

    # Section title with icon
    st.header("🚀 How to Use")
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
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
