from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import requests
import os


app = Flask(__name__)
CORS(app)  # Enable CORS for frontend-backend communication

# OpenAI API Key
openai.api_key = "***********"

# Lemonfox.ai API Key
LEMONFOX_API_KEY = "**********"
LEMONFOX_API_URL = "https://api.lemonfox.ai/v1/speech-to-text"

# IELTS Scoring Weights
FLUENCY_WEIGHT = 0.4
VOCAB_WEIGHT = 0.3
GRAMMAR_WEIGHT = 0.3

@app.route("/transcribe", methods=["POST"])
def transcribe_audio():
    """Transcribe audio using Lemonfox.ai Speech-to-Text API."""
    audio_file = request.files["audio"]
    audio_content = audio_file.read()

    # Send audio to Lemonfox.ai API
    headers = {
        "Authorization": f"Bearer {LEMONFOX_API_KEY}",
    }
    files = {
        "file": ("audio.wav", audio_content, "audio/wav"),
    }
    response = requests.post(LEMONFOX_API_URL, headers=headers, files=files)

    if response.status_code != 200:
        return jsonify({"error": "Failed to transcribe audio"}), 500

    transcript = response.json().get("text", "")
    return jsonify({"transcript": transcript})

@app.route("/evaluate", methods=["POST"])
def evaluate_response():
    """Evaluate user response using OpenAI GPT-4."""
    data = request.json
    transcript = data.get("transcript")

    # Generate feedback using OpenAI GPT-4
    prompt = f"""
    Evaluate the following IELTS Speaking Test response for fluency, vocabulary, and grammar. Provide feedback and a score out of 10 for each category.
    Response: {transcript}
    Feedback:
    """
    response = openai.Completion.create(
        engine="text-davinci-003",  # Use GPT-4 if available
        prompt=prompt,
        max_tokens=150,
    )
    feedback = response.choices[0].text.strip()

    # Simplified scoring logic
    fluency_score = min(len(transcript.split()) / 20, 10)  # Words per second
    vocab_score = len(set(transcript.split())) / len(transcript.split()) * 10  # Unique words
    grammar_score = 8  # Placeholder, replace with grammar-checking logic

    overall_score = (
        fluency_score * FLUENCY_WEIGHT
        + vocab_score * VOCAB_WEIGHT
        + grammar_score * GRAMMAR_WEIGHT
    )

    return jsonify({
        "feedback": feedback,
        "scores": {
            "fluency": fluency_score,
            "vocabulary": vocab_score,
            "grammar": grammar_score,
            "overall": overall_score,
        },
    })

if __name__ == "__main__":
    app.run(debug=True)