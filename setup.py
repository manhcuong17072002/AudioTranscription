import os
import re
from setuptools import setup, find_packages

# Đọc version từ file
with open("audio_transcription/version.py", "r", encoding="utf-8") as f:
    version_file = f.read()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    version = version_match.group(1) if version_match else "0.0.0"

# Đọc README
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Đọc requirements
with open("requirements.txt", "r", encoding="utf-8") as f:
    requirements = []
    for line in f:
        line = line.strip()
        if line and not line.startswith('#'):
            # Xử lý các dòng với version pinning như google-genai==1.10.0
            if '==' in line:
                package_name = line.split('==')[0]
                requirements.append(line)
            else:
                requirements.append(line)

# Phân tách các dependencies
core_requirements = []
demo_requirements = []

for req in requirements:
    # Nếu là streamlit hoặc plotly, đưa vào demo_requirements
    if any(pkg in req.lower() for pkg in ["streamlit", "plotly"]):
        demo_requirements.append(req)
    else:
        core_requirements.append(req)

setup(
    name="audio_transcription",
    version=version,
    description="Audio transcription and alignment library using Google Gemini API for TTS labeling",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/manhcuong17072002/AudioTranscription",
    author="Manh Cuong",
    author_email="manhcuong17072002@gmail.com",
    license="MIT",
    packages=find_packages(exclude=["demo", "demo.*", "*.demo", "*.demo.*", "sources", "sources.*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Multimedia :: Sound/Audio :: Speech",
    ],
    python_requires=">=3.10",
    install_requires=core_requirements,
    extras_require={
        "demo": demo_requirements,
        "dev": ["pytest", "black", "flake8"],
    },
    include_package_data=True,
    package_data={
        "audio_transcription": ["*.md", "*.txt"],
    },
    keywords="audio, transcription, alignment, gemini, tts, whisper, stable-ts",
    project_urls={
        "Bug Reports": "https://github.com/manhcuong17072002/AudioTranscription/issues",
        "Source": "https://github.com/manhcuong17072002/AudioTranscription",
        "Documentation": "https://github.com/manhcuong17072002/AudioTranscription/blob/main/README.md",
    },
)
