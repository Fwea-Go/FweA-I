# AI Whisper-based profanity cleaner
import os
import tempfile
from flask import Flask, request, jsonify, send_file
import whisper
from better_profanity import profanity
from pydub import AudioSegment

app = Flask(__name__)

# Load Whisper model once for efficiency
model = whisper.load_model("base")

@app.route('/api/clean-edit', methods=['POST'])
def clean_edit():
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file uploaded'}), 400

    audio_file = request.files['audio']
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_audio:
        audio_file.save(temp_audio.name)
        temp_audio_path = temp_audio.name

    # Transcribe audio using Whisper
    result = model.transcribe(temp_audio_path)
    segments = result.get('segments', [])
    text = result.get('text', '')

    # Profanity detection
    profanity.load_censor_words()
    clean_segments = []
    for seg in segments:
        seg_text = seg['text']
        if profanity.contains_profanity(seg_text):
            clean_segments.append((seg['start'], seg['end']))

    # Load audio
    audio = AudioSegment.from_file(temp_audio_path)
    for start, end in clean_segments:
        # Mute the profane segment
        start_ms = int(start * 1000)
        end_ms = int(end * 1000)
        audio = audio[:start_ms] + AudioSegment.silent(duration=(end_ms - start_ms)) + audio[end_ms:]

    # Save clean audio
    clean_path = temp_audio_path.replace('.mp3', '_clean.mp3')
    audio.export(clean_path, format="mp3")

    return send_file(clean_path, as_attachment=True, download_name="clean_version.mp3")

if __name__ == '__main__':
    app.run(debug=True)