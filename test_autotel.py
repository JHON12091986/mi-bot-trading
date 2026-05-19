from playwright.sync_api import sync_playwright

def main():
    with sync_playwright() as p:
        # Abre el navegador (modo visible)
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        # 1. Ve a la página de prueba
        page.goto("https://www.saucedemo.com/")
        print("✅ Página cargada")
        
        # 2. Escribe usuario
        page.fill("#user-name", "standard_user")
        print("✅ Usuario ingresado")
        
        # 3. Escribe contraseña
        page.fill("#password", "secret_sauce")
        print("✅ Contraseña ingresada")
        
        # 4. Haz clic en Login
        page.click("#login-button")
        print("✅ Login clickeado")
        
        # 5. Espera un momento para ver el resultado
        page.wait_for_timeout(3000)
        
        # 6. Verifica que el login fue exitoso
        if page.is_visible(".inventory_list"):
            print("🎉 LOGIN EXITOSO! Has entrado al catálogo de productos.")
        else:
            print("❌ Algo salió mal con el login")
        
        # Cierra el navegador
        browser.close()

if __name__ == "__main__":
    main()