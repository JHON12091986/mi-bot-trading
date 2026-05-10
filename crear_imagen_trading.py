# crear_imagen_trading.py
from PIL import Image, ImageDraw, ImageFont
import sys
import os

def crear_imagen(guion, fondo_path, salida_path):
    with Image.open(fondo_path) as img:
        img = img.resize((1080, 1920), Image.Resampling.LANCZOS)
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("arial.ttf", 50)
        except:
            font = ImageFont.load_default()
        lineas = guion.split('\n')
        y = 900
        for linea in lineas:
            draw.text((540, y), linea, fill=(255, 255, 0), font=font, anchor="mm")
            y += 60
        img.save(salida_path)
        print(f"Imagen guardada: {salida_path}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python crear_imagen_trading.py \"texto\" salida.jpg")
        sys.exit(1)
    texto = sys.argv[1]
    fondo = r"C:\Users\jhons\mi_primer_bot\fondo_trading.jpg"  # Asegúrate de tener esta imagen
    salida = sys.argv[2]
    crear_imagen(texto, fondo, salida)