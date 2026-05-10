import requests
import time
import json
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# ========== CONFIGURACIÓN CONSERVADORA ==========
SIMBOLO = "WIFUSDT"
RSI_COMPRA = 25      # Más bajo = Más conservador (solo compra en sobreventa extrema)
RSI_VENTA = 75       # Más alto = Más conservador (solo vende en sobrecompra extrema)
INTERVALO_SEGUNDOS = 60
ARCHIVO_ESTADO = "bot_wif_simulado.json"

# ========== FUNCIONES ==========
def enviar_telegram(mensaje):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {"chat_id": TELEGRAM_CHAT_ID, "text": mensaje, "parse_mode": "HTML"}
        requests.post(url, json=payload, timeout=10)
        print(f"📱 Mensaje enviado")
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
        # Precio actual
        url_price = "https://api.binance.com/api/v3/ticker/price?symbol=WIFUSDT"
        precio = float(requests.get(url_price, timeout=10).json()["price"])
        
        # Datos históricos para RSI
        url_klines = f"https://api.binance.com/api/v3/klines?symbol=WIFUSDT&interval=1h&limit=50"
        datos = requests.get(url_klines, timeout=10).json()
        precios_hist = [float(candle[4]) for candle in datos]
        
        rsi = calcular_rsi(precios_hist)
        return precio, rsi
    except Exception as e:
        print(f"❌ Error: {e}")
        return None, None

def cargar_estado():
    if os.path.exists(ARCHIVO_ESTADO):
        with open(ARCHIVO_ESTADO, "r") as f:
            return json.load(f)
    return {"ultima_alerta": None, "ultimo_rsi": 50}

def guardar_estado(tipo_alerta, rsi):
    estado = {
        "ultima_alerta": tipo_alerta,
        "ultimo_rsi": rsi,
        "fecha": datetime.now().isoformat()
    }
    with open(ARCHIVO_ESTADO, "w") as f:
        json.dump(estado, f, indent=4)

# ========== BUCLE PRINCIPAL ==========
def ejecutar():
    print("=" * 60)
    print("🐕 BOT WIF - ESTRATEGIA CONSERVADORA (SIMULADO)")
    print(f"📅 Iniciado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🎯 Comprar manual cuando RSI ≤ {RSI_COMPRA}")
    print(f"🎯 Vender manual cuando RSI ≥ {RSI_VENTA}")
    print(f"⏱️  Revisando cada {INTERVALO_SEGUNDOS} segundos")
    print("=" * 60)
    
    enviar_telegram(f"🐕 BOT CONSERVADOR INICIADO\n📊 RSI compra ≤ {RSI_COMPRA}\n📊 RSI venta ≥ {RSI_VENTA}\n✅ Solo alertas - Tú operas manual")
    
    estado = cargar_estado()
    
    while True:
        try:
            precio, rsi = obtener_datos_wif()
            if precio is None:
                time.sleep(30)
                continue
            
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] WIF: ${precio:.4f} | RSI: {rsi:.1f}")
            
            # COMPRA
            if rsi <= RSI_COMPRA:
                if estado["ultima_alerta"] != "COMPRA":
                    mensaje = f"""🟢 <b>ALERTA DE COMPRA MANUAL</b>
🐕 WIF/USDT
💰 Precio: ${precio:.4f}
📊 RSI: {rsi:.1f}
🎯 <b>Estrategia: RSI ≤ {RSI_COMPRA}</b>

✅ Sugerencia: COMPRA AHORA
💡 Monto sugerido: $5 - $10 USDT
⏰ {datetime.now().strftime('%H:%M:%S')}"""
                    enviar_telegram(mensaje)
                    guardar_estado("COMPRA", rsi)
                    print("🔔 Alerta de COMPRA enviada")
            
            # VENTA
            elif rsi >= RSI_VENTA:
                if estado["ultima_alerta"] != "VENTA":
                    mensaje = f"""🔴 <b>ALERTA DE VENTA MANUAL</b>
🐕 WIF/USDT
💰 Precio: ${precio:.4f}
📊 RSI: {rsi:.1f}
🎯 <b>Estrategia: RSI ≥ {RSI_VENTA}</b>

✅ Sugerencia: VENDE AHORA
⏰ {datetime.now().strftime('%H:%M:%S')}"""
                    enviar_telegram(mensaje)
                    guardar_estado("VENTA", rsi)
                    print("🔔 Alerta de VENTA enviada")
            
            time.sleep(INTERVALO_SEGUNDOS)
            
        except KeyboardInterrupt:
            print("\n🛑 Bot detenido")
            enviar_telegram("🛑 BOT CONSERVADOR DETENIDO")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            time.sleep(60)

if __name__ == "__main__":
    ejecutar()