"""
Example file for Google Gemini API key management.

IMPORTANT: Do not store your actual API keys in this file for a public repository!
Instead, use environment variables or secure configuration methods.

Rename this file to 'api_key.py' for local development only.
"""

# Method 1: Set API keys directly (NOT RECOMMENDED for public repositories)
# Replace these with your actual API keys if using this approach
API_KEY = "your-api-key-here"

# Method 2: Using environment variables (RECOMMENDED)
# To use this method, set the GOOGLE_API_KEY environment variable:
# export GOOGLE_API_KEY="your-api-key-here"
#
# import os
# API_KEY = os.environ.get("GOOGLE_API_KEY")
# if not API_KEY:
#     raise ValueError("GOOGLE_API_KEY environment variable not set")

# Method 3: Load from a local configuration file (NOT in version control)
# import json
# import os
#
# CONFIG_PATH = os.path.expanduser("~/.config/gemini_audio_transcription/config.json")
#
# try:
#     with open(CONFIG_PATH, "r", encoding="utf-8") as f:
#         config = json.load(f)
#         API_KEY = config.get("api_key")
# except FileNotFoundError:
#     raise FileNotFoundError(f"Configuration file not found at {CONFIG_PATH}")
# except json.JSONDecodeError:
#     raise ValueError(f"Invalid JSON in configuration file at {CONFIG_PATH}")
# 
# if not API_KEY:
#     raise ValueError("API key not found in configuration")
