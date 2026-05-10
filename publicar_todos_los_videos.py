import os
import re
import time
from moviepy.editor import ImageClip
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import pickle
from PIL import Image

# ========== CONFIGURACIÓN ==========
MAX_VIDEOS_POR_TANDA = 100  # Sube todos los que pueda hasta el límite diario
ARCHIVO_REGISTRO = "videos_subidos.txt"
TAMANO_VIDEO = (720, 1280)  # Reducido para evitar errores de memoria

def autenticar_youtube():
    if not os.path.exists('token.pickle'):
        print("❌ No se encuentra token.pickle")
        return None
    with open('token.pickle', 'rb') as token:
        creds = pickle.load(token)
    return build('youtube', 'v3', credentials=creds)

def redimensionar_imagen(imagen_path, output_path, tamaño=TAMANO_VIDEO):
    """Redimensiona la imagen al tamaño deseado (más ligera)"""
    if os.path.exists(output_path):
        return output_path
    
    try:
        img = Image.open(imagen_path)
        img = img.resize(tamaño, Image.Resampling.LANCZOS)
        img.save(output_path)
        print(f"   ✅ Imagen redimensionada: {output_path}")
        return output_path
    except Exception as e:
        print(f"   ❌ Error redimensionando: {e}")
        return imagen_path

def generar_video_desde_imagen(imagen_path, output_path):
    """Convierte una imagen en video de 15 segundos (con redimensionamiento)"""
    if os.path.exists(output_path):
        return True
    
    if not os.path.exists(imagen_path):
        print(f"❌ Imagen no encontrada: {imagen_path}")
        return False
    
    # Crear una versión redimensionada temporal
    img_temp = f"temp_{os.path.basename(imagen_path)}"
    img_redimensionada = redimensionar_imagen(imagen_path, img_temp)
    
    print(f"🎬 Creando video: {output_path}")
    try:
        clip = ImageClip(img_redimensionada).set_duration(15).set_fps(24)
        clip.write_videofile(output_path, codec='libx264', fps=24, 
                            logger=None, verbose=False, threads=2)
        print(f"✅ Video creado: {output_path}")
        return True
    except Exception as e:
        print(f"❌ Error creando video {output_path}: {e}")
        return False
    finally:
        # Limpiar imagen temporal
        if os.path.exists(img_temp):
            os.remove(img_temp)

def subir_video(youtube, video_path, titulo, descripcion):
    """Sube el video a YouTube"""
    print(f"📤 Subiendo {video_path}...")
    body = {
        'snippet': {
            'title': titulo,
            'description': descripcion,
            'tags': ['frutinovela', 'cuentos', 'frutas', 'shorts'],
            'categoryId': '22'
        },
        'status': {'privacyStatus': 'public'}
    }
    media = MediaFileUpload(video_path, chunksize=-1, resumable=True)
    request = youtube.videos().insert(part='snippet,status', body=body, media_body=media)
    response = request.execute()
    print(f"✅ Video subido: {video_path}")
    return response['id']

def cargar_registro():
    if os.path.exists(ARCHIVO_REGISTRO):
        with open(ARCHIVO_REGISTRO, 'r') as f:
            return set(line.strip() for line in f)
    return set()

def guardar_registro(video_name):
    with open(ARCHIVO_REGISTRO, 'a') as f:
        f.write(f"{video_name}\n")

def extraer_numero_desde_video(nombre_video):
    """Extrae el número de escena del nombre del video (ej: frutinovela_video4.mp4 -> 4)"""
    match = re.search(r'video(\d+)', nombre_video)
    if match:
        return match.group(1)
    return None

def extraer_numero_escena(nombre_archivo):
    """Extrae el número de escena del nombre de la imagen"""
    match = re.search(r'escena(\d+)', nombre_archivo)
    if match:
        return match.group(1)
    return None

def obtener_lista_imagenes():
    """Obtiene todas las imágenes frutinovela_escenaX.jpg ordenadas"""
    imagenes = []
    for archivo in os.listdir('.'):
        if archivo.startswith('frutinovela_escena') and archivo.endswith('.jpg'):
            numero = extraer_numero_escena(archivo)
            if numero:
                imagenes.append((int(numero), archivo))
    
    imagenes.sort(key=lambda x: x[0])
    return [img for _, img in imagenes]

def main():
    print("🎬 INICIANDO PUBLICACIÓN MASIVA DE FRUTINOVELAS")
    
    # 1. Obtener todas las imágenes
    imagenes = obtener_lista_imagenes()
    if not imagenes:
        print("❌ No se encontraron imágenes en la carpeta")
        return
    
    print(f"📸 Imágenes encontradas: {len(imagenes)}")
    
    # 2. Generar videos para todas las imágenes (si no existen)
    print("\n🎬 Generando videos faltantes...")
    videos_generados = []
    for img in imagenes:
        numero = extraer_numero_escena(img)
        video_name = f"frutinovela_video{numero}.mp4"
        
        if not os.path.exists(video_name):
            if generar_video_desde_imagen(img, video_name):
                videos_generados.append(video_name)
        else:
            videos_generados.append(video_name)
            print(f"⏭️ Video ya existe: {video_name}")
    
    print(f"\n✅ Videos disponibles: {len(videos_generados)}")
    
    # 3. Filtrar los que ya se subieron
    ya_subidos = cargar_registro()
    videos_pendientes = [v for v in videos_generados if v not in ya_subidos]
    
    if not videos_pendientes:
        print("✅ No hay videos pendientes por subir")
        return
    
    print(f"📤 Videos pendientes de subir: {len(videos_pendientes)}")
    
    # 4. Autenticar YouTube
    youtube = autenticar_youtube()
    if not youtube:
        print("❌ No se pudo autenticar YouTube")
        return
    
    # 5. Subir videos (respetando límite diario de YouTube)
    subidos_hoy = 0
    for video in videos_pendientes:
        if subidos_hoy >= MAX_VIDEOS_POR_TANDA:
            print(f"\n⏸️ Límite de {MAX_VIDEOS_POR_TANDA} videos por tanda alcanzado")
            break
        
        # Extraer número de escena desde el nombre del video (CORREGIDO)
        numero = extraer_numero_desde_video(video)
        if not numero:
            # Si falla, intentamos con el nombre alternativo
            numero = extraer_numero_escena(video)
        
        titulo = f"🍎 Frutinovela: El Secreto del Huerto - escena {numero if numero else '?'}"
        descripcion = "Ana la Manzana y Mando la Mandarina siguen su aventura. #Frutinovela #Shorts"
        
        try:
            subir_video(youtube, video, titulo, descripcion)
            guardar_registro(video)
            subidos_hoy += 1
            print(f"✅ Subido {subidos_hoy} hoy")
            time.sleep(5)  # Pausa entre videos para no saturar
        except Exception as e:
            error_msg = str(e)
            if 'uploadLimitExceeded' in error_msg:
                print(f"⚠️ Límite diario de YouTube alcanzado. Subidos hoy: {subidos_hoy}")
                print(f"   Ejecuta este script de nuevo mañana para continuar.")
            else:
                print(f"❌ Error subiendo {video}: {e}")
            break
    
    print(f"\n🎉 Proceso completado. Subidos hoy: {subidos_hoy} videos.")
    if subidos_hoy < len(videos_pendientes):
        print(f"💡 Faltan {len(videos_pendientes) - subidos_hoy} videos por subir.")
        print(f"   Ejecuta 'python publicar_todos_los_videos.py' mañana para continuar.")

if __name__ == "__main__":
    main()