from moviepy.editor import *
import os
import shutil

BASE_DIR = r"C:\Users\jhons\mi_primer_bot"
FRUTAS_DIR = os.path.join(BASE_DIR, "frutas")

# Asegurar que la carpeta frutas existe
os.makedirs(FRUTAS_DIR, exist_ok=True)

def imagen_a_video(imagen_path, output_path, duracion=15):
    clip = ImageClip(imagen_path).set_duration(duracion)
    clip.write_videofile(output_path, fps=24)
    print(f"✅ Video creado: {output_path}")

# Buscar imágenes nuevas (las que terminen en .jpg y no tengan su video aún)
imagenes = [f for f in os.listdir(BASE_DIR) if f.startswith("frutinovela_escena") and f.endswith(".jpg")]
imagenes.sort()

if not imagenes:
    print("❌ No hay nuevas imágenes para convertir.")
else:
    for img in imagenes:
        video_name = img.replace(".jpg", ".mp4")
        video_path = os.path.join(FRUTAS_DIR, video_name)
        # Si el video ya existe, no lo sobrescribe (evita duplicados)
        if not os.path.exists(video_path):
            imagen_a_video(os.path.join(BASE_DIR, img), video_path)
        else:
            print(f"⏭️ Video ya existe: {video_name}")
    print("🎉 Todos los videos generados en la carpeta 'frutas'.")