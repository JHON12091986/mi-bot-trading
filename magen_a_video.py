from moviepy.editor import *

def imagen_a_video(imagen_path, output_path, duracion=15):
    clip = ImageClip(imagen_path).set_duration(duracion)
    clip.write_videofile(output_path, fps=24)
    print(f"✅ Video creado: {output_path}")

if __name__ == "__main__":
    imagen_a_video("frutinovela_escena1.jpg", "video_short.mp4")