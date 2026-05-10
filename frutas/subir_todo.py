import os
from upload_post import UploadPostClient

API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6Impob24ubGFyb3NhLjMwQGdtYWlsLmNvbSIsImV4cCI6NDkzMDYwNTI3MCwianRpIjoiNzMxYmUwYWEtZjUyZC00YWJjLTkwN2MtY2M3Mjg2NzI2ZTNlIn0.3BY6IYAcERphCswfI4mKL1WNRJiiDfH5pjCJ0zYCiYQ"
PERFIL = "agente_digital"

client = UploadPostClient(api_key=API_KEY)

def publicar_video(video_path, titulo, descripcion=""):
    """Publica un video en YouTube automáticamente"""
    print(f"📤 Subiendo {video_path}...")
    try:
        response = client.upload_video(
            video_path=video_path,
            title=titulo,
            user=PERFIL,
            platforms=["youtube"],
            youtube_title=titulo,
            youtube_description=descripcion or "🍎 Frutinovela - El secreto del huerto #Shorts",
            youtube_tags="frutinovela,shorts,historias",
            youtube_visibility="public",
            youtube_shorts=True
        )
        if response.get("results") and response["results"].get("youtube"):
            print(f"✅ Publicado: {response['results']['youtube']['url']}")
        else:
            print(f"✅ Publicado (sin enlace)")
        return True
    except Exception as e:
        print(f"⚠️ Error al publicar: {e}")
        return False

if __name__ == "__main__":
    # Modo manual: sube el último video de la carpeta principal
    carpeta = r"C:\Users\jhons\mi_primer_bot"
    archivos = [f for f in os.listdir(carpeta) if f.endswith(".mp4")]
    if archivos:
        archivos.sort(key=lambda f: os.path.getmtime(os.path.join(carpeta, f)), reverse=True)
        ultimo = archivos[0]
        ruta = os.path.join(carpeta, ultimo)
        titulo = ultimo.replace(".mp4", "").replace("_", " ").replace("-", " ")
        publicar_video(ruta, titulo)
    else:
        print("No hay videos en la carpeta")