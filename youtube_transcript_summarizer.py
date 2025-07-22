from flask import Flask, request, render_template, jsonify
from youtube_transcript_api import YouTubeTranscriptApi
import spacy
from summa import summarizer
import re

app = Flask(__name__)

# Load spaCy model once at startup
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("Error: spaCy model 'en_core_web_sm' not found. Please install it by running: python -m spacy download en_core_web_sm")
    exit(1)

def extract_video_id(url_or_id):
    """Extract video ID from a YouTube URL or return the ID if already provided"""
    # Regular expression pattern to extract YouTube video ID
    youtube_regex = r'(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})'
    match = re.search(youtube_regex, url_or_id)
    
    if match:
        return match.group(1)
    elif re.match(r'^[a-zA-Z0-9_-]{11}$', url_or_id):
        return url_or_id
    else:
        return None

def get_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        text = ' '.join([entry['text'] for entry in transcript])
        return text
    except Exception as e:
        print(f"Error fetching transcript for video {video_id}: {e}")
        return None

def preprocess_text(text):
    if text is None or text.strip() == '':
        return []
    
    try:
        doc = nlp(text)
        sentences = [sent.text for sent in doc.sents]
        return sentences
    except Exception as e:
        print(f"Error processing text with spaCy: {e}")
        # Fallback to basic sentence splitting if spaCy fails
        return [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]

def summarize_text(sentences):
    if not sentences:
        return "No text to summarize."
    
    try:
        full_text = ' '.join(sentences)
        summarized_text = summarizer.summarize(full_text, ratio=0.2)
        
        # If summary is empty, return a reduced version of the original
        if not summarized_text.strip():
            # Take first few sentences as a fallback summary
            return ' '.join(sentences[:min(5, len(sentences))])
        
        return summarized_text
    except Exception as e:
        print(f"Error during summarization: {e}")
        return "Error creating summary."

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/summarize', methods=['GET'])
def summarize():
    url_or_id = request.args.get('videoId', '')
    
    if not url_or_id:
        return jsonify({
            'success': False,
            'message': 'No video ID or URL provided.'
        }), 400
    
    video_id = extract_video_id(url_or_id)
    
    if not video_id:
        return jsonify({
            'success': False,
            'message': 'Invalid YouTube video ID or URL.'
        }), 400
        
    transcript_text = get_transcript(video_id)

    if transcript_text:
        sentences = preprocess_text(transcript_text)
        summary = summarize_text(sentences)
        
        return jsonify({
            'success': True,
            'summary': summary,
            'videoId': video_id
        })
    else:
        return jsonify({
            'success': False,
            'message': 'Failed to obtain transcript. The video may not have subtitles or they might be disabled.'
        }), 404

if __name__ == '__main__':
    app.run(debug=True)
