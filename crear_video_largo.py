import os
import time
from moviepy.editor import ImageClip, concatenate_videoclips, AudioFileClip, concatenate_audioclips
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import pickle
from PIL import Image

# ========== CONFIGURACIÓN ==========
DURACION_VIDEO_MINUTOS = 10        # Cambia a 15, 20, etc. si quieres
DURACION_POR_IMAGEN = 15           # segundos por imagen
MUSICA_FONDO = "musica_fondo_original.mp3"
ARCHIVO_REGISTRO = "videos_largos_subidos.txt"
TAMANO_VIDEO = (720, 1280)         # Reducido para evitar errores de memoria

def autenticar_youtube():
    if not os.path.exists('token.pickle'):
        print("❌ No se encuentra token.pickle")
        return None
    with open('token.pickle', 'rb') as token:
        creds = pickle.load(token)
    return build('youtube', 'v3', credentials=creds)

def redimensionar_imagen(imagen_path, output_path, tamaño=TAMANO_VIDEO):
    """Redimensiona la imagen al tamaño deseado (más ligera)"""
    try:
        img = Image.open(imagen_path)
        img = img.resize(tamaño, Image.Resampling.LANCZOS)
        img.save(output_path)
        return output_path
    except Exception as e:
        print(f"   ❌ Error redimensionando: {e}")
        return imagen_path

def imagenes_a_video_largo(imagenes, output_path, duracion_por_imagen, duracion_total_minutos):
    """Convierte imágenes en un video largo de X minutos con música repetida"""
    if not imagenes:
        return False
    
    duracion_total_seg = duracion_total_minutos * 60
    total_imagenes_necesarias = duracion_total_seg // duracion_por_imagen
    
    print(f"🎬 Creando video de {duracion_total_minutos} minutos...")
    print(f"📸 Usando {len(imagenes)} imágenes, se repetirán en ciclo hasta completar {total_imagenes_necesarias} clips.")
    
    clips = []
    for i in range(total_imagenes_necesarias):
        img_path = imagenes[i % len(imagenes)]
        
        # Redimensionar imagen temporalmente
        img_temp = f"temp_{os.path.basename(img_path)}"
        img_redim = redimensionar_imagen(img_path, img_temp)
        
        clip = ImageClip(img_redim).set_duration(duracion_por_imagen).set_fps(24)
        clips.append(clip)
        
        # Limpiar temporal
        if os.path.exists(img_temp):
            os.remove(img_temp)
        
        if (i+1) % 50 == 0:
            print(f"   Procesando clip {i+1}/{total_imagenes_necesarias}")
    
    print("🎬 Concatenando clips...")
    video_final = concatenate_videoclips(clips, method="compose")
    
    # Añadir música de fondo (repetir si es más corta que el video)
    if os.path.exists(MUSICA_FONDO):
        print(f"🎵 Procesando música desde '{MUSICA_FONDO}'...")
        audio_original = AudioFileClip(MUSICA_FONDO)
        
        # Repetir el audio concatenando clips de audio
        audios_a_concatenar = []
        duracion_necesaria = video_final.duration
        duracion_actual = 0
        
        while duracion_actual < duracion_necesaria:
            audios_a_concatenar.append(audio_original)
            duracion_actual += audio_original.duration
        
        # Concatenar todos los clips de audio
        audio_final = concatenate_audioclips(audios_a_concatenar)
        audio_final = audio_final.subclip(0, video_final.duration)
        audio_final = audio_final.volumex(0.3)  # Bajar volumen 30%
        video_final = video_final.set_audio(audio_final)
        print(f"   ✅ Música añadida (duración: {audio_final.duration:.0f} segundos)")
    else:
        print("⚠️ No se encontró archivo de música. El video será sin audio.")
    
    print("💾 Guardando video...")
    video_final.write_videofile(output_path, codec='libx264', audio_codec='aac', 
                                fps=24, logger=None, verbose=False, threads=2)
    print(f"✅ Video de {duracion_total_minutos} minutos creado: {output_path}")
    return True

def subir_video(youtube, video_path, titulo, descripcion):
    print(f"📤 Subiendo {video_path} a YouTube...")
    body = {
        'snippet': {
            'title': titulo,
            'description': descripcion,
            'tags': ['frutinovela', 'cuentos', 'frutas', 'compilado'],
            'categoryId': '22'
        },
        'status': {'privacyStatus': 'public'}
    }
    media = MediaFileUpload(video_path, chunksize=-1, resumable=True)
    request = youtube.videos().insert(part='snippet,status', body=body, media_body=media)
    response = request.execute()
    print(f"✅ Video subido exitosamente: {video_path}")
    return response['id']

def ya_subido(video_name):
    if not os.path.exists(ARCHIVO_REGISTRO):
        return False
    with open(ARCHIVO_REGISTRO, 'r') as f:
        return video_name in f.read()

def guardar_subido(video_name):
    with open(ARCHIVO_REGISTRO, 'a') as f:
        f.write(f"{video_name}\n")

def obtener_lista_imagenes():
    """Obtiene todas las imágenes frutinovela_escenaX.jpg ordenadas"""
    imagenes = []
    i = 1
    while True:
        img = f"frutinovela_escena{i}.jpg"
        if os.path.exists(img):
            imagenes.append(img)
            i += 1
        else:
            break
    return imagenes

def main():
    print("🎬 INICIANDO CREACIÓN DE VIDEO LARGO DE FRUTINOVELAS")
    
    # 1. Obtener imágenes
    imagenes = obtener_lista_imagenes()
    if not imagenes:
        print("❌ No se encontraron imágenes")
        return
    
    print(f"📸 Imágenes encontradas: {len(imagenes)}")
    
    # 2. Crear video largo
    timestamp = time.strftime('%Y%m%d_%H%M%S')
    video_name = f"frutinovela_larga_{DURACION_VIDEO_MINUTOS}min_{timestamp}.mp4"
    
    if ya_subido(video_name):
        print(f"⏭️ {video_name} ya fue subido, saltando.")
        return
    
    if imagenes_a_video_largo(imagenes, video_name, DURACION_POR_IMAGEN, DURACION_VIDEO_MINUTOS):
        youtube = autenticar_youtube()
        if youtube:
            titulo = f"🍎 Frutinovela: El Secreto del Huerto - ESPECIAL {DURACION_VIDEO_MINUTOS} MINUTOS"
            descripcion = "Disfruta de las mejores aventuras de Ana la Manzana y Mando la Mandarina en este compilado especial.\n\n#Frutinovela #CuentosInfantiles #Compilado"
            subir_video(youtube, video_name, titulo, descripcion)
            guardar_subido(video_name)
            print("🎉 Video largo publicado en YouTube")
        else:
            print(f"⚠️ Video guardado localmente: {video_name}")
    else:
        print("❌ Error al generar el video")

if __name__ == "__main__":
    main()