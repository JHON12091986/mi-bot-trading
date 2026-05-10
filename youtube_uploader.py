import os
import pickle
import sys
import time
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

# ========== CONFIGURACIÓN ==========
CLIENT_SECRET_FILE = r'C:\Users\jhons\mi_primer_bot\cliente-oauth.json'
VIDEOS_FOLDER = r"C:\Users\jhons\mi_primer_bot\frutas"
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

# Archivo para llevar el registro de videos subidos (por título + tamaño)
REGISTRO_FILE = os.path.join(os.path.dirname(__file__), "videos_subidos.txt")

def cargar_registro():
    """Carga el conjunto de videos que ya se han subido."""
    subidos = set()
    if os.path.exists(REGISTRO_FILE):
        with open(REGISTRO_FILE, "r", encoding="utf-8") as f:
            for linea in f:
                linea = linea.strip()
                if linea:
                    subidos.add(linea)
    return subidos

def guardar_registro(subidos):
    """Guarda el registro de videos subidos."""
    with open(REGISTRO_FILE, "w", encoding="utf-8") as f:
        for item in sorted(subidos):
            f.write(item + "\n")

def generar_identificador(archivo):
    """Genera un identificador único para el video basado en nombre + tamaño + fecha_modificación."""
    ruta = os.path.join(VIDEOS_FOLDER, archivo)
    if os.path.exists(ruta):
        stats = os.stat(ruta)
        # Usamos nombre, tamaño y fecha de modificación (evita falsos duplicados)
        return f"{archivo}|{stats.st_size}|{stats.st_mtime}"
    return archivo

def get_authenticated_service():
    creds = None
    token_file = os.path.join(os.path.dirname(__file__), 'token.pickle')
    if os.path.exists(token_file):
        with open(token_file, 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_file, 'wb') as token:
            pickle.dump(creds, token)
    return build('youtube', 'v3', credentials=creds)

def upload_video(youtube, video_file, title, description, tags, privacy_status='public'):
    body = dict(
        snippet=dict(
            title=title,
            description=description,
            tags=tags,
            categoryId='22'
        ),
        status=dict(
            privacyStatus=privacy_status,
            selfDeclaredMadeForKids=False
        )
    )
    media = MediaFileUpload(video_file, chunksize=-1, resumable=True)
    print(f'🚀 Subiendo "{os.path.basename(video_file)}"...')
    request = youtube.videos().insert(
        part=','.join(body.keys()),
        body=body,
        media_body=media
    )
    response = None
    while response is None:
        try:
            status, response = request.next_chunk()
            if status:
                print(f"  Subido {int(status.progress() * 100)}%")
        except HttpError as e:
            if e.resp.status == 403 and 'quotaExceeded' in str(e):
                print("❌ Límite de subidas diarias alcanzado. Deteniendo.")
                raise
            print(f"⚠️ Error: {e}")
            time.sleep(5)
            continue
    print(f'✅ Subido con éxito. URL: https://youtu.be/{response["id"]}')
    return response

if __name__ == '__main__':
    # Cargar registro de videos ya subidos
    subidos = cargar_registro()
    print(f"📋 Registro actual: {len(subidos)} videos subidos previamente.")

    youtube = get_authenticated_service()
    archivos = [f for f in os.listdir(VIDEOS_FOLDER) if f.endswith('.mp4')]
    if not archivos:
        print('❌ No hay videos en la carpeta.')
        sys.exit()

    # Ordenar por fecha de modificación (más reciente primero)
    archivos.sort(key=lambda f: os.path.getmtime(os.path.join(VIDEOS_FOLDER, f)), reverse=True)

    nuevos_subidos = 0
    for video in archivos:
        identificador = generar_identificador(video)
        if identificador in subidos:
            print(f"⏭️ Video ya subido anteriormente: {video}")
            continue

        ruta_video = os.path.join(VIDEOS_FOLDER, video)
        nombre_base = os.path.splitext(video)[0].replace('_', ' ')
        titulo = f"🍎 Frutinovela: El Secreto del Huerto - {nombre_base}"
        descripcion = "Ana la Manzana y Mando la Mandarina siguen su aventura. #Frutinovela #Shorts"
        etiquetas = ['Frutinovela', 'Shorts', 'Animacion', 'IA']

        try:
            upload_video(youtube, ruta_video, titulo, descripcion, etiquetas, privacy_status='public')
            subidos.add(identificador)
            guardar_registro(subidos)
            nuevos_subidos += 1
            print("⏳ Esperando 30 segundos para no saturar la API...")
            time.sleep(30)
        except HttpError as e:
            if 'uploadLimitExceeded' in str(e):
                print("❌ Límite diario de YouTube alcanzado. Se detiene la subida.")
                break
            else:
                print(f"❌ Error subiendo {video}: {e}")
                # No lo marcamos como subido, para reintentar después.

    print(f"\n🎉 Subidos hoy: {nuevos_subidos} nuevos videos. Total en registro: {len(subidos)}.")
    print("📋 Los videos subidos se han guardado en 'videos_subidos.txt'.")