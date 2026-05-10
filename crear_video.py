from moviepy.editor import *
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import os

def crear_texto_como_imagen(texto, size=(1080, 1920), fontsize=50):
    """Crea una imagen con el texto usando Pillow"""
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("arial.ttf", fontsize)
    except:
        font = ImageFont.load_default()
    
    # Dividir texto en líneas
    lineas = texto.split('\n')
    y_offset = size[1] // 2 - (len(lineas) * fontsize) // 2
    
    for linea in lineas:
        bbox = draw.textbbox((0, 0), linea, font=font)
        text_width = bbox[2] - bbox[0]
        x = (size[0] - text_width) // 2
        draw.text((x, y_offset), linea, fill=(255, 255, 0, 255), font=font)
        y_offset += fontsize + 10
    
    return np.array(img)

def crear_video_con_moviepy(guion, imagen_fondo, nombre_salida):
    """Crea un video con imagen de fondo y texto superpuesto"""
    if not os.path.exists(imagen_fondo):
        print(f"❌ Error: No se encuentra la imagen '{imagen_fondo}'")
        return
    
    # Cargar fondo y redimensionar manualmente
    clip = ImageClip(imagen_fondo).set_duration(15)
    clip = clip.resize(height=1920)
    if clip.w > 1080:
        clip = clip.resize(width=1080)
    
    # Crear texto como imagen
    txt_img = crear_texto_como_imagen(guion, size=(clip.w, clip.h), fontsize=50)
    txt_clip = ImageClip(txt_img, transparent=True).set_duration(15)
    
    # Combinar
    video = CompositeVideoClip([clip, txt_clip])
    video.write_videofile(nombre_salida, fps=24)
    print(f"✅ Video creado: {nombre_salida}")

if __name__ == "__main__":
    guion = "⚠️ SEÑAL DE VENTA - AVGO\nRSI: 77.9\nPrecio: $419.94"
    imagen_fondo = r"C:\Users\jhons\mi_primer_bot\fondo.jpg"
    crear_video_con_moviepy(guion, imagen_fondo, "video_automatico.mp4")