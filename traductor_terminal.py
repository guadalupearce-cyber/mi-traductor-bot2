from deep_translator import GoogleTranslator

texto = input("Escribe un texto: ")
traduccion = GoogleTranslator(source='auto', target='en').translate(texto)
print("Traducción:", traduccion)
