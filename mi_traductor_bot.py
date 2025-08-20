from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters
from deep_translator import GoogleTranslator
import pytz

# Token del bot de Telegram
TOKEN = "8053096806:AAFGPbZUYPUqU_bKTqzvB4wqgD4fpIMcM5Y"

# Lista de idiomas soportados
IDIOMAS_DISPONIBLES = {
    "es": "Español",
    "en": "Inglés",
    "fr": "Francés",
    "de": "Alemán",
    "it": "Italiano"
}

# Diccionario para almacenar el idioma seleccionado por el usuario
idioma_seleccionado = {}

# Comando /start (inicio)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    # Si ya se ha seleccionado un idioma, mostrar las opciones de idioma
    if user_id in idioma_seleccionado:
        return await mostrar_menu_idiomas(update)

    # Si no, mostrar las opciones de idioma
    return await mostrar_menu_idiomas(update)

# Mostrar el menú de selección de idioma
async def mostrar_menu_idiomas(update: Update):
    user_id = update.message.from_user.id

    # Mostrar los idiomas disponibles
    keyboard = [
        [InlineKeyboardButton(name, callback_data=code)] for code, name in IDIOMAS_DISPONIBLES.items()
    ]
    keyboard.append([InlineKeyboardButton("Cambiar de idioma", callback_data="cambiar_idioma")])

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "🌐 ¡Bienvenido! Elige el idioma al que deseas traducir:",
        reply_markup=reply_markup
    )

# Responder a la selección de idioma o cambiar idioma
async def boton_seleccionado(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id

    if query.data == "cambiar_idioma":
        # Si el usuario elige cambiar de idioma, mostramos nuevamente el menú de idiomas
        return await mostrar_menu_idiomas(update)

    idioma_seleccionado[user_id] = query.data  # Guardar el idioma seleccionado
    await query.answer()
    await query.edit_message_text(text=f"✅ Has seleccionado el idioma: {IDIOMAS_DISPONIBLES[query.data]}.\nEscribe un texto para traducir.")

# Comando /translate (traducir el texto)
async def translate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

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
    app.add_handler(CommandHandler("translate", translate))

    # Añadir el handler para el botón de selección de idioma o cambiar idioma
    app.add_handler(CallbackQueryHandler(boton_seleccionado))

    # Añadir el handler para recibir textos para traducir
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, translate))

    print("🤖 Bot iniciado. Esperando mensajes en Telegram...")
    # Usar polling para mantener el bot ejecutándose en Render como Background Worker
    app.run_polling()

if __name__ == "__main__":
    main()
