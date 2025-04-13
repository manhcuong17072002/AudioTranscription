from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as f:
    requirements = f.read().splitlines()

setup(
    name="audio_transcription",
    version="0.1.0",
    description="Hệ thống phiên âm audio sử dụng Google Gemini API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/manhcuong17072002/AudioTranscription",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
    install_requires=requirements,
)
