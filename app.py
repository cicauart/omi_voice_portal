from flask import Flask, request, render_template, jsonify
from google.cloud import texttospeech
import google.generativeai as genai
import os

# 🌐 Configurar Flask
app = Flask(__name__)

# 🔐 Configurar Google Gemini API Key (desde variables de entorno en Render)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

# 🔐 Configurar Google TTS usando Secret File de Render
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/etc/secrets/google_tts_key.json"

# 🎤 Función para convertir texto en audio con Google TTS
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

# 🌐 Ruta principal con procesamiento de mensaje
@app.route("/", methods=["GET", "POST"])
def index():
    respuesta = ""

    if request.method == "POST":
        mensaje = request.form.get("mensaje")
        print("📩 MENSAJE RECIBIDO:", mensaje)

        # 🔍 Mostrar los modelos disponibles (una sola vez, útil para debugging)
        try:
            modelos = genai.list_models()
            print("🔍 Modelos disponibles:")
            for modelo in modelos:
                print("✅", modelo.name)
        except Exception as e:
            print("⚠️ No se pudieron listar los modelos:", str(e))

        # ⚡ Ejecutar el modelo Gemini
        try:
            modelo = genai.GenerativeModel("models/gemini-1.5-pro-latest")  # Usa este o cambia según tu lista
            result = modelo.generate_content(f"Explicá el tema si alguien dice: '{mensaje}'. Sugerí 2 respuestas inteligentes.")
            respuesta = result.text
            print("🧠 RESPUESTA GEMINI:", respuesta)
        except Exception as e:
            print("⚠️ ERROR AL LLAMAR A GEMINI:", str(e))
            respuesta = "No se pudo generar respuesta."

        # 🔊 Generar audio de la respuesta
        hablar(respuesta)

    return render_template("index.html", respuesta=respuesta)

# 🔊 Ruta para acceder al audio
@app.route("/audio")
def audio():
    return jsonify({ "audio_url": "/static/respuesta.mp3" })
