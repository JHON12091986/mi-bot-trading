import os
from upload_post import UploadPostClient

API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6Impob24ubGFyb3NhLjMwQGdtYWlsLmNvbSIsImV4cCI6NDkzMDYwNTI3MCwianRpIjoiNzMxYmUwYWEtZjUyZC00YWJjLTkwN2MtY2M3Mjg2NzI2ZTNlIn0.3BY6IYAcERphCswfI4mKL1WNRJiiDfH5pjCJ0zYCiYQ"
PERFIL = "agente_digital"
CARPETA_VIDEOS = r"C:\Users\jhons\mi_primer_bot"

client = UploadPostClient(api_key=API_KEY)

def publicar_video():
    video_path = os.path.join(CARPETA_VIDEOS, "video_short.mp4")
    titulo = "Señal de Venta MU - RSI 87.8 | Alerta de Trading"
    
    print(f"📤 Subiendo {video_path}...")
    try:
        response = client.upload_video(
            video_path=video_path,
            title=titulo,
            user=PERFIL,
            platforms=["youtube"],
            youtube_title=titulo,
            youtube_description="📊 Señal automática de trading",
            youtube_tags=["TradingBot", "RSI"]
        )
        print(f"✅ Publicado. Respuesta completa: {response}")
        if response.get("results") and response["results"].get("youtube"):
            print(f"🔗 Enlace: {response['results']['youtube']['url']}")
    except Exception as e:
        print(f"⚠️ Error: {e}")

if __name__ == "__main__":
    publicar_video()