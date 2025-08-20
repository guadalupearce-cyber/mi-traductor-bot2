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

# Diccionarios para almacenar usuarios y sus credenciales
usuarios_registrados = {}
idioma_seleccionado = {}

# Comando /start (inicio)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    # Si el usuario ya está registrado, lleva a la selección de idioma
    if user_id in usuarios_registrados:
        return await mostrar_menu_idiomas(update)

    # Si no está registrado, preguntar si desea crear una cuenta
    keyboard = [
        [InlineKeyboardButton("Sí", callback_data="registrar")],
        [InlineKeyboardButton("No", callback_data="no_registrar")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "👋 ¡Hola! Para comenzar, ¿deseas crear una cuenta? (Te pediremos usuario y contraseña)",
        reply_markup=reply_markup
    )

# Respuesta de botones: Sí/No crear cuenta
async def boton_respuesta(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    if query.data == "registrar":
        # Pedir usuario y contraseña si selecciona "Sí"
        await query.edit_message_text("💬 Por favor, elige un nombre de usuario y contraseña.")

        # Cambio a estado de registro
        usuarios_registrados[user_id] = {'estado': 'esperando_usuario'}

    elif query.data == "no_registrar":
        # Si selecciona "No", se pasa a la selección de idioma
        return await mostrar_menu_idiomas(update)

# Mensaje para crear usuario y contraseña
async def crear_usuario(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    # Verifica si el usuario está esperando ingresar datos
    if user_id in usuarios_registrados and usuarios_registrados[user_id].get('estado') == 'esperando_usuario':
        # Dividir el mensaje en usuario y contraseña
        try:
            username, password = update.message.text.split()
            usuarios_registrados[user_id] = {'usuario': username, 'contraseña': password}
            usuarios_registrados[user_id]['estado'] = 'registro_completo'

            await update.message.reply_text(
                f"🎉 ¡Cuenta creada con éxito!\nUsuario: {username}\nAhora puedes elegir un idioma para traducir."
            )
            return await mostrar_menu_idiomas(update)
        except ValueError:
            await update.message.reply_text("❌ Debes ingresar un nombre de usuario y una contraseña. Ejemplo: `/registrar mi_usuario mi_contraseña`")
    else:
        await update.message.reply_text("❌ No estás en proceso de registro.")

# Mostrar el menú de selección de idioma
async def mostrar_menu_idiomas(update: Update):
    user_id = update.message.from_user.id

    if user_id not in usuarios_registrados or 'usuario' not in usuarios_registrados[user_id]:
        await update.message.reply_text("❌ Necesitas estar registrado primero. Usa /start para iniciar.")
        return

    # Mostrar los idiomas disponibles
    keyboard = [
        [InlineKeyboardButton(name, callback_data=code)] for code, name in IDIOMAS_DISPONIBLES.items()
    ]
    keyboard.append([InlineKeyboardButton("❌ Cambiar de idioma", callback_data="cambiar_idioma")])  # Agregar la opción de cambio de idioma
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "🌐 ¡Bienvenido! Elige el idioma al que deseas traducir:",
        reply_markup=reply_markup
    )

# Responder a la selección de idioma
async def boton_seleccionado(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    if query.data != "cambiar_idioma":
        idioma_seleccionado[user_id] = query.data  # Guardar el idioma seleccionado

    await query.answer()

    # Si el usuario seleccionó un idioma
    if query.data != "cambiar_idioma":
        await query.edit_message_text(text=f"✅ Has seleccionado el idioma: {IDIOMAS_DISPONIBLES[query.data]}.\nEscribe un texto para traducir.")
    else:
        # Si el usuario seleccionó cambiar de idioma, mostrar nuevamente los idiomas disponibles
        await mostrar_menu_idiomas(update)

# Comando /translate (traducir el texto)
