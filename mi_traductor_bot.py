from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters
from deep_translator import GoogleTranslator
import pytz

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

# Diccionario para almacenar la selección de idioma del usuario
idioma_seleccionado = {}

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
        # Mostrar el menú de selección de idioma si ya está registrado
        keyboard = [
            [InlineKeyboardButton(name, callback_data=code)] for code, name in IDIOMAS_DISPONIBLES.items()
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            "🌐 ¡Bienvenido! Elige el idioma al que deseas traducir.",
            reply_markup=reply_markup
        )

# Comando /registrar para crear una cuenta
async def registrar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id in usuarios_registrados:
        await update.message.reply_text("❌ Ya estás registrado. Puedes comenzar a traducir.")
        return

    usuarios_registrados[user_id] = update.message.from_user.username  # Guardar el nombre de usuario
    await update.message.reply_text(f"🎉 ¡Te has registrado con éxito, {update.message.from_user.username}! Ahora puedes elegir un idioma para traducir.")
    await start(update, context)

# Responder a la selección de idioma
async def boton_seleccionado(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    idioma_seleccionado[user_id] = query.data  # Guardar el idioma seleccionado

    await query.answer()
    await query.edit_message_text(text=f"✅ Has seleccionado el idioma: {IDIOMAS_DISPONIBLES[query.data]}. Ahora, envíame el texto que deseas traducir.")

# Comando /translate (traducir el texto)
async def translate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if user_id not in usuarios_registrados:
        await update.message.reply_text("❌ No estás registrado. Usa /registrar para crear una cuenta.")
        return

    if user_id not in idioma_seleccionado:
        await update.message.reply_text("❌ Debes seleccionar un idioma primero. Usa /start para elegir un idioma.")
        return

    idioma_destino = idioma_seleccionado[user_id]
    texto = update.message.text

    try:
        traduccion = GoogleTranslator(source='auto', target=idioma_destino).translate(texto)
        await update.message.reply_text(f"✅ Traducción a {IDIOMAS_DISPONIBLES[idioma_destino]}:\n{traduccion}")
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

    # Añadir el handler para el botón de selección de idioma
    app.add_handler(CallbackQueryHandler(boton_seleccionado))

    # Añadir el handler para recibir textos para traducir
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, translate))

    print("🤖 Bot iniciado. Esperando mensajes en Telegram...")
    # Utilizar polling para la ejecución continua del bot
    app.run_polling()

if __name__ == "__main__":
    main()
