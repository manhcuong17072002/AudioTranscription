"""
Custom styles for the Audio Transcription demo application.
"""

def load_css():
    """
    Load custom CSS styles for the application.
    """
    return """
    <style>
    /* Base styles and typography */
    .main {
        background-color: #f8f9fd;
    }
    
    h1, h2, h3, h4, h5, h6 {
        color: #333;
        font-family: 'Inter', sans-serif;
    }
    
    /* Custom containers */
    .custom-container {
        background-color: white;
        border-radius: 8px;
        padding: 1.5rem;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
        margin-bottom: 1.5rem;
    }
    
    /* Hero section styles */
    .hero-container {
        background: linear-gradient(135deg, #5D8BF4, #9AC5F4);
        color: white;
        padding: 3rem 2rem;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 2rem;
        position: relative;
        overflow: hidden;
    }
    
    .hero-container::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><path d="M30,20 L70,20 L70,80 L30,80 Z" stroke="rgba(255,255,255,0.1)" stroke-width="5" fill="none" /></svg>') 0 0 / 100px 100px repeat;
        opacity: 0.2;
    }
    
    .hero-container h1 {
        color: white;
        font-size: 2.5rem;
        margin-bottom: 1rem;
    }
    
    .hero-container h3 {
        color: white;
        font-weight: 300;
        margin-bottom: 1.5rem;
    }
    
    /* Feature card styles */
    .feature-card {
        background-color: white;
        border-radius: 8px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        transition: all 0.3s ease;
        height: 100%;
        border-left: 4px solid #5D8BF4;
        box-shadow: 0 3px 10px rgba(0, 0, 0, 0.08);
        color: #333;
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
    }
    
    .feature-card h3 {
        color: #333;
        margin-bottom: 0.5rem;
    }
    
    .feature-card p {
        color: #333;
    }
    
    /* Card with icon styles */
    .icon-card {
        padding: 1.5rem;
        background-color: white;
        border-radius: 8px;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
        transition: all 0.3s ease;
        height: 100%;
        color: #333;
    }
    
    .icon-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
    }
    
    .icon-card h3 {
        color: #333;
    }
    
    .icon-card p {
        color: #333;
    }
    
    .icon-card .icon {
        font-size: 2.5rem;
        margin-bottom: 1rem;
        color: #5D8BF4;
    }
    
    /* Section styles */
    .section-title {
        margin-top: 2rem;
        margin-bottom: 1.5rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #f0f0f0;
        display: flex;
        align-items: center;
    }
    
    .section-title h2 {
        margin: 0;
        color: #333;
        font-weight: 600;
    }
    
    .section-title-icon {
        margin-right: 0.75rem;
        color: #5D8BF4;
    }
    
    /* Info box styles */
    .info-box {
        background-color: #f0f7ff;
        border-left: 4px solid #5D8BF4;
        padding: 1rem;
        border-radius: 4px;
        margin-bottom: 1.5rem;
        color: #333;
    }
    
    .info-box h1, .info-box h2, .info-box h3, .info-box h4, .info-box h5, .info-box h6 {
        color: #333;
    }
    
    .info-box p {
        color: #333;
    }
    
    .info-box ul li, .info-box ol li {
        color: #333;
    }
    
    /* Metrics styles */
    .metrics-container {
        background: linear-gradient(to right, #f8f9fa, #eef1f8);
        border-radius: 8px;
        padding: 1.5rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    }
    
    .metric-card {
        background-color: white;
        padding: 1.5rem;
        border-radius: 8px;
        text-align: center;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
        height: 100%;
        color: #333;
    }
    
    .metric-card h1 {
        color: #5D8BF4;
        font-size: 2rem;
        margin-bottom: 0.5rem;
    }
    
    .metric-card h3 {
        color: #333;
    }
    
    .metric-card p {
        color: #666;
        margin-bottom: 0;
    }
    
    /* Steps styles */
    .step-card {
        background-color: white;
        border-radius: 8px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
        height: 100%;
        border-top: 4px solid #5D8BF4;
        color: #333;
    }
    
    .step-card h3 {
        color: #333;
    }
    
    .step-card p {
        color: #333;
    }
    
    .step-number {
        background-color: #5D8BF4;
        color: white;
        width: 36px;
        height: 36px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        font-size: 1.25rem;
        margin: 0 auto 1rem auto;
    }
    
    /* Form control styles */
    .custom-form-container {
        background-color: white;
        border-radius: 8px;
        padding: 1.5rem;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
        margin-bottom: 1.5rem;
    }
    
    /* Settings section styles */
    .settings-container {
        background-color: white;
        border-radius: 8px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
    }
    
    .settings-section {
        border-bottom: 1px solid #f0f0f0;
        padding-bottom: 1rem;
        margin-bottom: 1rem;
    }
    
    .settings-section:last-child {
        border-bottom: none;
        margin-bottom: 0;
    }
    
    /* Footer styles */
    .footer {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #5D8BF4;
        margin-top: 2rem;
        font-size: 0.9rem;
        color: #666;
    }
    
    /* Results section styles */
    .results-container {
        background-color: white;
        border-radius: 8px;
        padding: 1.5rem;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
        margin-bottom: 1.5rem;
        color: #333;
    }
    
    .results-container h1, .results-container h2, 
    .results-container h3, .results-container h4, 
    .results-container h5, .results-container h6 {
        color: #333;
    }
    
    .results-container p, .results-container span, 
    .results-container li, .results-container label {
        color: #333;
    }
    
    /* Audio player custom styles */
    .audio-player-container {
        background-color: #f8f9fd;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    /* Sidebar styles */
    .sidebar-menu {
        background-color: white;
        border-radius: 8px;
        margin-bottom: 1rem;
        overflow: hidden;
    }
    
    .sidebar-menu a {
        display: block;
        padding: 0.75rem 1rem;
        text-decoration: none;
        color: #333;
        transition: all 0.2s ease;
    }
    
    .sidebar-menu a:hover {
        background-color: #f0f7ff;
        color: #5D8BF4;
    }
    
    .sidebar-menu a.active {
        background-color: #5D8BF4;
        color: white;
    }
    
    /* Expander custom styles */
    .streamlit-expanderHeader {
        background-color: #f8f9fd;
        border-radius: 4px;
    }
    
    /* Divider */
    .custom-divider {
        margin: 2rem 0;
        border: none;
        height: 1px;
        background-color: #eaeaea;
    }
    </style>
    """
