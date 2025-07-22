#!/usr/bin/env python3
"""
Setup script for YouTube Transcript Summarizer
Automates the installation and setup process
"""

import subprocess
import sys
import os

def run_command(command, description=""):
    """Run a command and handle errors"""
    print(f"⏳ {description}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {description} failed")
        print(f"Error output: {e.stderr}")
        return False

def main():
    print("🎬 YouTube Transcript Summarizer Setup")
    print("=" * 50)
    
    # Check Python version
    if sys.version_info < (3, 7):
        print("❌ Python 3.7 or higher is required")
        sys.exit(1)
    
    print(f"✅ Python {sys.version.split()[0]} detected")
    
    # Install requirements
    if not run_command("pip install -r requirements.txt", "Installing Python packages"):
        sys.exit(1)
    
    # Download spaCy model
    if not run_command("python -m spacy download en_core_web_sm", "Downloading spaCy language model"):
        print("⚠️  Warning: spaCy model download failed. You may need to run this manually:")
        print("   python -m spacy download en_core_web_sm")
    
    print("\n🎉 Setup completed successfully!")
    print("\n🚀 To run the application:")
    print("   python youtube_transcript_summarizer.py")
    print("\n🌐 Then open your browser to:")
    print("   http://localhost:5000")

if __name__ == "__main__":
    main()
