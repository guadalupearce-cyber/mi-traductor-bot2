from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from deep_translator import GoogleTranslator
import pytz
import json

TOKEN = "8053096806:AAFGPbZUYPUqU_bKTqzvB4wqgD4fpIMcM5Y"

# Lista de idiomas soportados
IDIOMAS_DISPONIBLES = {
    "es": "Español",
    "en": "Inglés",
    "fr": "Francés",
    "de": "Alemán",
    "it": "Italiano"
}

# Diccionario para almacenar los usuarios registrados (en memoria o podrías usar una base de datos)
usuarios_registrados = {}

# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    # Verificar si el usuario ya está registrado
    if user_id not in usuarios_registrados:
        # Si no está registrado, pedirle crear una cuenta
        await update.message.reply_text(
            "👋 ¡Hola! Para comenzar, debes registrarte. Usa el comando /registrar para crear tu cuenta."
        )
    else:
        # Mostrar el menú si ya está registrado
        idiomas = "\n".join([f"{nombre} ({codigo})" for codigo, nombre in IDIOMAS_DISPONIBLES.items()])
        await update.message.reply_text(
            f"🌐 Bienvenido de nuevo! Soy tu bot traductor.\n\n"
            f"Idiomas disponibles:\n{idiomas}\n\n"
            "Usa /translate <código_idioma> <texto> para traducir.\n"
            "Ejemplo: /translate es Hello world"
        )

# Comando /registrar para crear una cuenta
async def registrar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id in usuarios_registrados:
        await update.message.reply_text("❌ Ya estás registrado. Puedes comenzar a traducir.")
        return

    usuarios_registrados[user_id] = update.message.from_user.username  # Guardar el nombre de usuario o cualquier dato adicional
    await update.message.reply_text(f"🎉 ¡Te has registrado con éxito, {update.message.from_user.username}! Ahora puedes comenzar a traducir.")
    await start(update, context)

# Comando /translate
async def translate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id not in usuarios_registrados:
        await update.message.reply_text("❌ No estás registrado. Usa /registrar para crear una cuenta.")
        return

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
    app.add_handler(CommandHandler("registrar", registrar))
    app.add_handler(CommandHandler("translate", translate))

    print("🤖 Bot iniciado. Esperando mensajes en Telegram...")
    app.run_polling()

if __name__ == "__main__":
    main()






