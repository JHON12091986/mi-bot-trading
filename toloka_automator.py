# toloka_automator.py
# Bot para automatizar la búsqueda de proyectos en Toloka
# Versión: Asistente de Tiburónzin 🦈

import webbrowser
import time
import pyperclip
from datetime import datetime

class TolokaBot:
    def __init__(self):
        self.url_base = "https://toloka.ai"
        self.proyectos_interes = [
            "First-Person Video AI Trainer",
            "Spanish Audio Transcription",
            "Image Tagging Spanish",
            "Data Collection Spanish"
        ]
        self.perfil = {
            "idiomas": ["Español nativo (Perú)", "Inglés básico/intermedio"],
            "equipo": "Laptop Windows 11 + Celular Android",
            "internet": "4G estable (compartido del celular)",
            "disponibilidad": "20-30 horas/semana"
        }
    
    def abrir_toloka(self):
        """Abre Toloka en el navegador"""
        print("🌐 Abriendo Toloka...")
        webbrowser.open(self.url_base)
        time.sleep(2)
        print("✅ Página abierta. Regístrate con Google o email.")
    
    def mostrar_proyectos(self):
        """Muestra los proyectos que debes buscar manualmente"""
        print("\n" + "="*60)
        print("📋 PROYECTOS A BUSCAR EN TOLOKA")
        print("="*60)
        for i, proyecto in enumerate(self.proyectos_interes, 1):
            print(f"{i}. 🔍 Buscar: {proyecto}")
        print("\n💡 Tip: Usa el buscador interno de Toloka con estos nombres")
    
    def generar_texto_postulacion(self):
        """Genera el texto para tu perfil/postulación"""
        texto = f"""🎯 Perfil Profesional - Toloka

📅 Fecha: {datetime.now().strftime('%d/%m/%Y')}

👤 Sobre mí:
Soy hablante nativo de español (Perú) con nivel práctico de inglés para leer instrucciones. Tengo experiencia en etiquetado de datos y transcripción de audio.

💻 Equipo disponible:
- Laptop con Windows 11 (internet 4G compartido del celular)
- Celular Android con cámara 1080p

🕐 Disponibilidad:
20-30 horas semanales, horario flexible.

📌 Habilidades:
- Atención al detalle
- Cumplimiento de instrucciones
- Experiencia con plataformas de microtareas
- Automatización básica con Python (para optimizar tareas)

✅ Busco proyectos de:
- Transcripción de audio en español
- Etiquetado de imágenes
- Grabación de video (First-Person tasks)

¡Listo para empezar!
"""
        return texto
    
    def copiar_texto_perfil(self):
        """Copia el texto del perfil al portapapeles"""
        texto = self.generar_texto_postulacion()
        pyperclip.copy(texto)
        print("\n📋 Texto del perfil copiado al portapapeles ✅")
        print("👉 Ahora pégalo (Ctrl+V) en tu perfil de Toloka")
    
    def guia_rapida(self):
        """Guía paso a paso"""
        print("\n" + "="*60)
        print("🚀 GUÍA RÁPIDA TOLOKA - TIBURÓNZIN")
        print("="*60)
        print("""
1️⃣ REGISTRO:
   - Ve a toloka.ai
   - Regístrate con Google (usa tu cuenta jslrch...)
   - Confirma tu correo

2️⃣ COMPLETA PERFIL:
   - Ve a "Profile" o "Mi perfil"
   - Pega el texto que generé (Ctrl+V)
   - Añade tu país: Perú

3️⃣ BUSCA PROYECTOS:
   - Ve a "Projects" o "Tareas"
   - Busca estos nombres:
     • First-Person Video AI Trainer
     • Spanish Audio Transcription
     • Image Tagging Spanish

4️⃣ EMPIEZA:
   - Haz proyectos pequeños primero
   - Acumula reputación
   - En 2-3 días tendrás más tareas

⚠️ IMPORTANTE:
- No uses VPN (te pueden banear)
- Lee bien las instrucciones
- Toloka paga por PayPal
- Mínimo de retiro: $10-$20 USD
""")
    
    def ejecutar(self):
        """Ejecuta la automatización"""
        print("="*60)
        print("🦈 TOLOKA AUTOMATOR - TIBURÓNZIN")
        print("="*60)
        print("🤖 Iniciando asistente...")
        
        self.guia_rapida()
        self.mostrar_proyectos()
        self.copiar_texto_perfil()
        
        print("\n" + "="*60)
        print("✅ ¿Listo para empezar?")
        print("📌 Acciones siguientes:")
        print("1. Abre el enlace: toloka.ai")
        print("2. Regístrate con Google")
        print("3. Pega el texto en tu perfil")
        print("4. Busca los proyectos indicados")
        print("5. Empieza a ganar 💰")
        print("="*60)
        
        # Preguntar si abre el navegador
        respuesta = input("\n🌐 ¿Abro Toloka en tu navegador ahora? (s/n): ")
        if respuesta.lower() == 's':
            self.abrir_toloka()

# Ejecutar el bot
if __name__ == "__main__":
    bot = TolokaBot()
    bot.ejecutar()