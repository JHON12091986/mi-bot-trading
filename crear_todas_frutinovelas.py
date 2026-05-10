from moviepy.editor import *
import os
import requests
from dotenv import load_dotenv

# Cargar credenciales de Telegram
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def enviar_video_telegram(ruta_video, caption=""):
    """Envía un video a Telegram y devuelve el mensaje con enlace (opcional)"""
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("⚠️ Telegram no configurado, no se enviará el video.")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendVideo"
    try:
        with open(ruta_video, 'rb') as video:
            files = {'video': video}
            data = {'chat_id': TELEGRAM_CHAT_ID, 'caption': caption}
            r = requests.post(url, files=files, data=data, timeout=30)
            if r.status_code == 200:
                print(f"📤 Video enviado a Telegram: {ruta_video}")
            else:
                print(f"❌ Error al enviar: {r.text}")
    except Exception as e:
        print(f"❌ Error: {e}")

def imagen_a_video(imagen_path, output_path, duracion=15):
    """Convierte una imagen en video (sin enviar aún)"""
    clip = ImageClip(imagen_path).set_duration(duracion)
    clip.write_videofile(output_path, fps=24, verbose=False, logger=None)
    print(f"✅ Video creado: {output_path}")

# ========== 1. Encontrar todas las imágenes que existan ==========
imagenes = []
i = 1
while True:
    img = f"frutinovela_escena{i}.jpg"
    if os.path.exists(img):
        imagenes.append(img)
        i += 1
    else:
        break

if not imagenes:
    print("❌ No hay imágenes JPG. Ejecuta primero el generador de imágenes.")
    exit()

print(f"📸 Imágenes encontradas: {len(imagenes)}")

# ========== 2. Para cada imagen, crear video solo si no existe ==========
for idx, img in enumerate(imagenes, start=1):
    video_name = f"frutinovela_video{idx}.mp4"
    if os.path.exists(video_name):
        print(f"⏭️ Video {video_name} ya existe, saltando...")
        continue
    
    print(f"🎬 Creando video {idx}/{len(imagenes)}: {video_name}")
    imagen_a_video(img, video_name)
    enviar_video_telegram(video_name, caption=f"🎬 Frutinovela {idx}")

# ========== 3. Actualizar el contador para la próxima imagen ==========
# Calculamos el próximo número libre
proximo = len(imagenes) + 1
with open("contador_frutinovelas.txt", "w") as f:
    f.write(str(proximo))
print(f"✅ Contador actualizado. La próxima escena será la número {proximo}.")
print("🎉 Proceso completado.")