from flask import Flask, request, render_template, jsonify
from google.cloud import texttospeech
import google.generativeai as genai
import os

# 🌐 Configurar Flask
app = Flask(__name__)

# 🔐 Configurar Google Gemini API (vía SDK)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

# 🔐 Configurar Google TTS
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/etc/secrets/google_tts_key.json"

# 🎤 Convertir texto a voz
def hablar(texto):
    client = texttospeech.TextToSpeechClient()
    synthesis_input = texttospeech.SynthesisInput(text=texto)
    voice = texttospeech.VoiceSelectionParams(
        language_code="es-ES",
        ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
    )
    audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)
    response = client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)

    with open("static/respuesta.mp3", "wb") as out:
        out.write(response.audio_content)

# 🌐 Ruta principal
@app.route("/", methods=["GET", "POST"])
def index():
    respuesta = ""

    if request.method == "POST":
        mensaje = request.form.get("mensaje")
        print("📩 MENSAJE RECIBIDO:", mensaje)

        try:
            modelo = genai.GenerativeModel("gemini-pro-1.0")
            result = modelo.generate_content(f"Explicá el tema si alguien dice: '{mensaje}'. Sugerí 2 respuestas inteligentes.")
            respuesta = result.text
            print("🧠 RESPUESTA GEMINI:", respuesta)
        except Exception as e:
            print("⚠️ ERROR GEMINI SDK:", str(e))
            respuesta = "No se pudo generar respuesta."

        hablar(respuesta)

    return render_template("index.html", respuesta=respuesta)

# Ruta opcional para el audio
@app.route("/audio")
def audio():
    return jsonify({ "audio_url": "/static/respuesta.mp3" })

