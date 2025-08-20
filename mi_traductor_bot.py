from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from deep_translator import GoogleTranslator
import pytz  # Para la zona horaria
from flask import Flask
import threading
import os

TOKEN = "8053096806:AAFGPbZUYPUqU_bKTqzvB4wqgD4fpIMcM5Y"

# Lista de idiomas soportados
IDIOMAS_DISPONIBLES = {
    "es": "Español",
    "en": "Inglés",
    "fr": "Francés",
    "de": "Alemán",
    "it": "Italiano"
}


# Crear una app Flask básica
flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return "Bot está corriendo 🟢"

def run_flask():
    port = int(os.environ.get("PORT", 5000))  # Render define PORT en variables de entorno
    flask_app.run(host="0.0.0.0", port=port)

# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Mostrar idiomas en líneas separadas
    idiomas = "\n".join([f"{nombre} ({codigo})" for codigo, nombre in IDIOMAS_DISPONIBLES.items()])
    await update.message.reply_text(
        f"👋 ¡Hola! Soy tu bot traductor.\n\n"
        f"🌐 Idiomas disponibles:\n{idiomas}\n\n"
        "Usa /translate <código_idioma> <texto> para traducir.\n"
        "Ejemplo: /translate es Hello world"
    )

# Comando /translate
async def translate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text(
            "❌ Por favor, escribe un idioma y un texto. Ejemplo: /translate es Hello world"
        )
        return

    lang_code = context.args[0]
    texto = " ".join(context.args[1:])

    if lang_code not in IDIOMAS_DISPONIBLES:
        await update.message.reply_text(
            f"❌ Idioma no soportado. Idiomas disponibles:\n" +
            "\n".join([f"{nombre} ({codigo})" for codigo, nombre in IDIOMAS_DISPONIBLES.items()])
        )
        return

    try:
        traduccion = GoogleTranslator(source='auto', target=lang_code).translate(texto)
        await update.message.reply_text(f"✅ Traducción:\n{traduccion}")
    except Exception as e:
        await update.message.reply_text("❌ Error al traducir. Verifica el código de idioma.")
        print("Error de traducción:", e)

def main():
    # Crear la aplicación
    app = ApplicationBuilder().token(TOKEN).build()

    # Ajustar la zona horaria del JobQueue
    app.job_queue.scheduler.timezone = pytz.UTC

    # Añadir los comandos
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("translate", translate))

    print("🤖 Bot iniciado. Esperando mensajes en Telegram...")
    app.run_polling()

if __name__ == "__main__":
    main()

def main():
    # Iniciar Flask en un hilo separado
    threading.Thread(target=run_flask).start()

    # Crear la aplicación de Telegram
    app = ApplicationBuilder().token(TOKEN).build()

    # Ajustar la zona horaria del JobQueue
    app.job_queue.scheduler.timezone = pytz.UTC

    # Añadir los comandos
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("translate", translate))

    print("🤖 Bot iniciado. Esperando mensajes en Telegram...")
    app.run_polling()





