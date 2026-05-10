# tiktok_bot.py
from playwright.sync_api import sync_playwright
import time
import random

class TikTokBot:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.playwright = None
        self.browser = None
        self.page = None
    
    def iniciar(self):
        """Inicia el navegador y abre TikTok"""
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=False)  # False para ver lo que hace
        self.page = self.browser.new_page()
        self.page.goto("https://www.tiktok.com/login")
        print("🔹 Navegador abierto. Inicia sesión MANUALMENTE esta primera vez.")
        input("Presiona Enter después de iniciar sesión...")
    
    def dar_likes_a_hashtag(self, hashtag, cantidad=10):
        """Da likes a los primeros 'cantidad' videos de un hashtag"""
        self.page.goto(f"https://www.tiktok.com/tag/{hashtag}")
        time.sleep(3)
        
        likes_dados = 0
        for i in range(cantidad):
            # Buscar el botón de like (svg con data-e2e="like-icon")
            try:
                like_btn = self.page.locator('button[data-e2e="like-icon"]').nth(i)
                if like_btn:
                    like_btn.click()
                    likes_dados += 1
                    print(f"✅ Like #{likes_dados} a video de #{hashtag}")
                    time.sleep(random.uniform(5, 10))  # Pausa humana entre 5 y 10 segundos
            except Exception as e:
                print(f"❌ Error en like {i}: {e}")
        
        print(f"🎯 Total likes dados: {likes_dados}")
    
    def seguir_cuentas_de_hashtag(self, hashtag, cantidad=10):
        """Sigue a los creadores de los primeros videos de un hashtag"""
        self.page.goto(f"https://www.tiktok.com/tag/{hashtag}")
        time.sleep(3)
        
        seguidos = 0
        for i in range(cantidad):
            try:
                # Buscar botón de seguir en el video
                follow_btn = self.page.locator('button[data-e2e="follow-button"]').nth(i)
                if follow_btn:
                    follow_btn.click()
                    seguidos += 1
                    print(f"✅ Seguido #{seguidos} desde #{hashtag}")
                    time.sleep(random.uniform(8, 15))  # Pausa más larga para no ser detectado
            except:
                pass
        
        print(f"🎯 Total seguidos: {seguidos}")
    
    def cerrar(self):
        """Cierra el navegador"""
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()

# ========== EJECUCIÓN ==========
if __name__ == "__main__":
    # Pon tu usuario y contraseña de TikTok (opcional, puedes iniciar sesión manual)
    bot = TikTokBot("", "")
    
    bot.iniciar()
    
    print("\n📌 ELIGE UNA ACCIÓN:")
    print("1 - Dar likes a videos de #fyp")
    print("2 - Dar likes a videos de #parati")
    print("3 - Seguir cuentas de #tecnologia")
    
    opcion = input("\n👉 Opción (1/2/3): ")
    
    if opcion == "1":
        bot.dar_likes_a_hashtag("fyp", cantidad=15)
    elif opcion == "2":
        bot.dar_likes_a_hashtag("parati", cantidad=15)
    elif opcion == "3":
        bot.seguir_cuentas_de_hashtag("tecnologia", cantidad=10)
    else:
        print("❌ Opción no válida")
    
    bot.cerrar()