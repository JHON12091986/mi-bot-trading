import os
from upload_post import UploadPostClient

# ========== CONFIGURACIÓN CON NUEVA CLAVE ==========
API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6ImpzbHJjaC4xMi4wOS44NkBnbWFpbC5jb20iLCJleHAiOjQ5MzE0NzA5MDksImp0aSI6IjEyZDdiOTk2LTY1NTktNDgyZi1hOTRiLWJjNjYzYWZhM2QwZCJ9.qnO6sOtGMNdGrEl64hPvlzgiYAHmWf5PMs9bh07dOLE"
PERFIL = "agente_digital"

# ========== RUTA DEL VIDEO LARGO ==========
VIDEO_PATH = r"C:\Users\jhons\mi_primer_bot\frutinovela_larga_10min_20260503_000838.mp4"

# ========== INICIALIZAR CLIENTE ==========
client = UploadPostClient(api_key=API_KEY)

def publicar_video_largo():
    """Publica un video largo (10-15 min) en YouTube como contenido normal"""
    
    print(f"🎬 Subiendo video largo a YouTube...")
    
    try:
        response = client.upload_video(
            video_path=VIDEO_PATH,
            title="🍎 Frutinovela: El Secreto del Huerto - COMPILADO 10 MINUTOS",
            user=PERFIL,
            platforms=["youtube"],
            youtube_description="""Disfruta de las aventuras de Ana la Manzana y Mando la Mandarina en este compilado especial.

💰 ¿Quieres aprender a invertir en bolsa y vencer al mercado?
👉 Curso recomendado: https://go.hotmart.com/Q105757633F

#Frutinovela #CuentosInfantiles #Compilado #Inversiones""",
            youtube_tags="frutinovela,cuentos,infantiles,compilado,aventuras",
            youtube_visibility="public"
        )
        
        print(f"✅ ¡PUBLICADO EN YOUTUBE!")
        
        if response.get("results") and response["results"].get("youtube"):
            print(f"🔗 Enlace: {response['results']['youtube']['url']}")
        
        return True
        
    except Exception as e:
        print(f"⚠️ Error al publicar: {e}")
        return False

if __name__ == "__main__":
    publicar_video_largo()