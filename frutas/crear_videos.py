from moviepy.editor import *

imagenes = [
    "frutinovela_escena1.jpg",
    "frutinovela_escena2.jpg",
    "frutinovela_escena3.jpg",
    "frutinovela_escena4.jpg"
]

for img in imagenes:
    video = img.replace(".jpg", ".mp4")
    print(f"🎬 Creando {video}...")
    clip = ImageClip(img).set_duration(15)
    clip.write_videofile(video, fps=24)
    print(f"✅ {video} listo")