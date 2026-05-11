import requests
import time
import json
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# ========== CONFIGURACIÓN EXACTA ==========
SIMBOLO = "WIFUSDT"
RSI_COMPRA = 25      
RSI_VENTA = 75       
INTERVALO_SEGUNDOS = 60

def enviar_telegram(mensaje):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("⚠️ No hay Telegram configurado")
        return
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {"chat_id": TELEGRAM_CHAT_ID, "text": mensaje}
        requests.post(url, json=payload, timeout=5)
        print("📱 Mensaje enviado")
    except Exception as e:
        print(f"⚠️ Error Telegram: {e}")

def calcular_rsi(precios, periodo=14):
    if len(precios) < periodo + 1:
        return 50.0
    ganancias, perdidas = [], []
    for i in range(1, len(precios)):
        cambio = precios[i] - precios[i-1]
        if cambio >= 0:
            ganancias.append(cambio)
            perdidas.append(0)
        else:
            ganancias.append(0)
            perdidas.append(abs(cambio))
    ganancia_prom = sum(ganancias[-periodo:]) / periodo
    perdida_prom = sum(perdidas[-periodo:]) / periodo
    if perdida_prom == 0:
        return 100.0
    rs = ganancia_prom / perdida_prom
    return round(100 - (100 / (1 + rs)), 1)

def obtener_datos_wif():
    try:
        url_price = "https://api.binance.com/api/v3/ticker/price?symbol=WIFUSDT"
        precio = float(requests.get(url_price, timeout=10).json()["price"])
        
        url_klines = "https://api.binance.com/api/v3/klines?symbol=WIFUSDT&interval=1h&limit=50"
        datos = requests.get(url_klines, timeout=10).json()
        precios_hist = [float(candle[4]) for candle in datos]
        
        rsi = calcular_rsi(precios_hist)
        return precio, rsi
    except Exception as e:
        print(f"❌ Error: {e}")
        return None, None

def ejecutar():
    print("🐕 BOT WIF - RSI EXACTO")
    print(f"🎯 COMPRA cuando RSI ≤ {RSI_COMPRA}")
    print(f"🎯 VENTA cuando RSI ≥ {RSI_VENTA}")
    
    enviar_telegram(f"🐕 BOT WIF ACTIVADO\n✅ Comprar RSI ≤ {RSI_COMPRA}\n✅ Vender RSI ≥ {RSI_VENTA}")
    
    ultima_alerta = None
    
    while True:
        try:
            precio, rsi = obtener_datos_wif()
            if precio is None:
                time.sleep(30)
                continue
            
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] WIF: ${precio:.4f} | RSI: {rsi:.1f}")
            
            if rsi <= RSI_COMPRA and ultima_alerta != "COMPRA":
                mensaje = f"🟢 COMPRA WIF\nPrecio: ${precio:.4f}\nRSI: {rsi:.1f} (≤{RSI_COMPRA})"
                enviar_telegram(mensaje)
                ultima_alerta = "COMPRA"
                print("🔔 Alerta COMPRA enviada")
                
            elif rsi >= RSI_VENTA and ultima_alerta != "VENTA":
                mensaje = f"🔴 VENTA WIF\nPrecio: ${precio:.4f}\nRSI: {rsi:.1f} (≥{RSI_VENTA})"
                enviar_telegram(mensaje)
                ultima_alerta = "VENTA"
                print("🔔 Alerta VENTA enviada")
            
            time.sleep(60)
            
        except KeyboardInterrupt:
            print("\n🛑 Bot detenido")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            time.sleep(60)

if __name__ == "__main__":
    ejecutar()