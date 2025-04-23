from flask import Flask, request, render_template, jsonify
from google.cloud import texttospeech
import requests
import os

# Configuración inicial
app = Flask(__name__)

# 🔐 Clave API de Gemini desde variables de entorno
GEMINI_API_KEY = os.getenv("AIzaSyD3Q_aku2VflGthDZm6v8Exep9_pbugo-k")
GEMINI_ENDPOINT = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"

# 📁 Ruta al archivo de credenciales de Google TTS
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/etc/secrets/google_tts_key.json"

# 🎤 Función que convierte texto en audio
def hablar(texto):
    print("🔊 Generando audio...")
    client = texttospeech.TextToSpeechClient()
    synthesis_input = texttospeech.SynthesisInput(text=texto)
    voice = texttospeech.VoiceSelectionParams(
        language_code="es-ES",
        ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
    )
    audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)
    response = client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)

    # 💾 Guarda el audio en la carpeta static/
    with open("static/respuesta.mp3", "wb") as out:
        out.write(response.audio_content)

# 🌐 Ruta principal
@app.route("/", methods=["GET", "POST"])
def index():
    respuesta = ""

    if request.method == "POST":
        mensaje = request.form.get("mensaje")
        print("📩 MENSAJE RECIBIDO:", mensaje)

        payload = {
            "contents": [{
                "parts": [{"text": f"Explicá el tema si alguien dice: '{mensaje}'. Sugerí 2 respuestas inteligentes."}]
            }]
        }
        headers = { "Content-Type": "application/json" }

        # Enviamos la solicitud a Gemini
        r = requests.post(GEMINI_ENDPOINT, headers=headers, json=payload)
        print("🔍 RESPUESTA DE GEMINI (RAW):", r.text)

        try:
            data = r.json()
            respuesta = data['candidates'][0]['content']['parts'][0]['text']
        except Exception as e:
            print("⚠️ ERROR AL PROCESAR RESPUESTA DE GEMINI:", str(e))
            respuesta = "No se pudo generar respuesta."

        # Generamos el audio
        hablar(respuesta)

    return render_template("index.html", respuesta=respuesta)

# 🔉 Ruta opcional para obtener el audio por separado
@app.route("/audio")
def audio():
    return jsonify({ "audio_url": "/static/respuesta.mp3" })
