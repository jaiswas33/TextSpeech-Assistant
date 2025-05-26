import vertexai
from flask import Flask, render_template, request, jsonify
from vertexai.preview.generative_models import GenerativeModel
import speech_recognition as sr
from google.cloud import texttospeech
import base64
import os

app = Flask(__name__)

# Initialize Vertex AI
PROJECT_ID = os.getenv("PROJECT_ID")
LOCATION = os.getenv("LOCATION") 
MODEL_NAME = os.getenv("MODEL_NAME")

vertexai.init(project=PROJECT_ID, location=LOCATION)
model = GenerativeModel(MODEL_NAME)


def synthesize_speech(text):
    client = texttospeech.TextToSpeechClient()
    input_text = texttospeech.SynthesisInput(text=text)

    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US",
        ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
    )

    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )

    response = client.synthesize_speech(
        input=input_text,
        voice=voice,
        audio_config=audio_config
    )

    audio_base64 = base64.b64encode(response.audio_content).decode("utf-8")
    return audio_base64

@app.route("/", methods=["GET", "POST"])
def index():
    response_audio = None
    if request.method == "POST":
        text = request.form.get("text")
        if text:
            response_audio = synthesize_speech(text)
    return render_template("index.html", audio_base64=response_audio)

@app.route("/api/speak", methods=["POST"])
def speak_api():
    data = request.get_json()
    text = data.get("text", "")
    if not text:
        return jsonify({"error": "No text provided"}), 400
    try:
        audio_base64 = synthesize_speech(text)
        return jsonify({"audio": audio_base64})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
