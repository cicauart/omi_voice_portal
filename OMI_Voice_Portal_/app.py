
from flask import Flask, request, render_template, jsonify
from google.cloud import texttospeech
import requests
import os

app = Flask(__name__)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_ENDPOINT = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"

def hablar(texto):
    client = texttospeech.TextToSpeechClient()
    synthesis_input = texttospeech.SynthesisInput(text=texto)
    voice = texttospeech.VoiceSelectionParams(language_code="es-ES", ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL)
    audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)
    response = client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)
    with open("static/respuesta.mp3", "wb") as out:
        out.write(response.audio_content)

@app.route("/", methods=["GET", "POST"])
def index():
    respuesta = ""
    if request.method == "POST":
        mensaje = request.form.get("mensaje")
        payload = {
            "contents": [{
                "parts": [{"text": f"Explicá el tema si alguien dice: '{mensaje}'. Sugerí 2 respuestas inteligentes."}]
            }]
        }
        headers = {"Content-Type": "application/json"}
        r = requests.post(GEMINI_ENDPOINT, headers=headers, json=payload)
        try:
            respuesta = r.json()['candidates'][0]['content']['parts'][0]['text']
        except:
            respuesta = "No se pudo generar respuesta."
        hablar(respuesta)
    return render_template("index.html", respuesta=respuesta)

@app.route("/audio")
def audio():
    return jsonify({"audio_url": "/static/respuesta.mp3"})
