# precio_nvda.py - Consultar precio de NVDA (Versión alternativa)

import requests
import time

print("=== BOT DE PRECIOS NVDA ====")
print("Consultando precio...")
print("")

# Usamos una API gratuita que NO requiere clave para pruebas
# Fuente: Investing.com (a través de un endpoint público)

url = "https://api.binance.com/api/v3/ticker/price?symbol=NVDABUSD"

try:
    respuesta = requests.get(url, timeout=5)
    
    if respuesta.status_code == 200:
        datos = respuesta.json()
        precio_actual = float(datos['price'])
        print(f"✅ NVDA (vía Binance)")
        print(f"💰 Precio actual: ${precio_actual:.2f} USD")
        print(f"🕐 {time.strftime('%H:%M:%S')}")
    else:
        print(f"❌ Error HTTP: {respuesta.status_code}")
        print("Probando método alternativo...")
        
        # Método alternativo: Yahoo Finance con headers
        url2 = "https://query1.finance.yahoo.com/v8/finance/chart/NVDA"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        respuesta2 = requests.get(url2, headers=headers, timeout=5)
        datos2 = respuesta2.json()
        precio_actual2 = datos2['chart']['result'][0]['meta']['regularMarketPrice']
        print(f"💰 Precio actual (Yahoo): ${precio_actual2:.2f} USD")
        
except Exception as e:
    print(f"❌ Error: {e}")
    print("")
    print("Posible solución: Tu red o firewall puede estar bloqueando la API.")
    print("Usaremos un precio de prueba para continuar aprendiendo.")
    print("")
    print("💰 Precio de prueba NVDA: $200.00 USD")

print("")
print("🚀 Script ejecutado")