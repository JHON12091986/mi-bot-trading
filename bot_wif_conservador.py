import requests
import time
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# ========== CONFIGURACIÓN ==========
SIMBOLO = "WIFUSDT"
RSI_COMPRA = 30
RSI_VENTA = 70
INTERVALO_SEGUNDOS = 60

# === BINANCE REAL ===
API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")

# === TELEGRAM ===
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Conectar a Binance
from binance.client import Client
from binance.exceptions import BinanceAPIException

client = Client(API_KEY, API_SECRET)
print("✅ Conectado a Binance REAL - Modo AUTOMÁTICO activado")

# ========== FUNCIONES ==========

def enviar_telegram(mensaje):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        return
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {"chat_id": TELEGRAM_CHAT_ID, "text": mensaje}
        requests.post(url, json=payload, timeout=5)
        print("📱 Mensaje enviado a Telegram")
    except Exception as e:
        print(f"⚠️ Error Telegram: {e}")

def calcular_rsi(precios, periodo=14):
    """Calcula RSI a partir de lista de precios"""
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
    """Obtiene precio y RSI de WIF"""
    try:
        # Precio desde Binance
        url_price = f"https://api.binance.com/api/v3/ticker/price?symbol={SIMBOLO}"
        precio = float(requests.get(url_price, timeout=5).json()["price"])
        
        # RSI desde Binance (más estable que CoinPaprika)
        url_klines = f"https://api.binance.com/api/v3/klines?symbol={SIMBOLO}&interval=1h&limit=30"
        datos = requests.get(url_klines, timeout=10).json()
        precios_hist = [float(candle[4]) for candle in datos]
        rsi = calcular_rsi(precios_hist)
        
        return precio, rsi
    except Exception as e:
        print(f"❌ Error obtener datos: {e}")
        return None, None

def obtener_saldos():
    try:
        account = client.get_account()
        usdt = 0
        wif = 0
        for asset in account['balances']:
            if asset['asset'] == 'USDT':
                usdt = float(asset['free'])
            elif asset['asset'] == 'WIF':
                wif = float(asset['free'])
        return usdt, wif
    except Exception as e:
        print(f"❌ Error obtener saldos: {e}")
        return 0, 0

def comprar_wif(precio, rsi, usdt_disponible):
    if usdt_disponible < 5:
        enviar_telegram(f"⚠️ SALDO INSUFICIENTE: ${usdt_disponible:.2f} USDT")
        return False
    try:
        monto_usdt = round(usdt_disponible * 0.90, 2)
        orden = client.order_market_buy(
            symbol=SIMBOLO,
            quoteOrderQty=monto_usdt
        )
        mensaje = f"🟢 COMPRA AUTOMÁTICA\n💰 ${precio:.4f}\n📊 RSI: {rsi:.1f}\n💵 ${monto_usdt} USDT"
        enviar_telegram(mensaje)
        print(f"✅ COMPRA: {monto_usdt} USDT")
        return True
    except Exception as e:
        enviar_telegram(f"❌ Error compra: {e}")
        return False

def vender_wif(precio, rsi, wif_disponible):
    if wif_disponible < 0.1:
        return False
    try:
        cantidad = round(wif_disponible, 2)
        orden = client.order_market_sell(
            symbol=SIMBOLO,
            quantity=cantidad
        )
        mensaje = f"🔴 VENTA AUTOMÁTICA\n💰 ${precio:.4f}\n📊 RSI: {rsi:.1f}\n📦 {cantidad} WIF"
        enviar_telegram(mensaje)
        print(f"✅ VENTA: {cantidad} WIF")
        return True
    except Exception as e:
        enviar_telegram(f"❌ Error venta: {e}")
        return False

# ========== BUCLE PRINCIPAL ==========

def ejecutar():
    print("=" * 50)
    print("🤖 BOT WIF - ENVÍA RSI CADA MINUTO")
    print(f"🎯 COMPRA cuando RSI ≤ {RSI_COMPRA}")
    print(f"🎯 VENTA cuando RSI ≥ {RSI_VENTA}")
    print("=" * 50)
    
    enviar_telegram(f"🤖 BOT WIF ACTIVADO\n✅ Te enviaré el RSI cada 1 minuto\n✅ COMPRA si RSI ≤ {RSI_COMPRA}\n✅ VENTA si RSI ≥ {RSI_VENTA}")
    
    ya_compro = False
    ya_vendio = False
    
    while True:
        try:
            precio, rsi = obtener_datos_wif()
            if precio is None:
                time.sleep(30)
                continue
            
            usdt, wif = obtener_saldos()
            timestamp = datetime.now().strftime("%H:%M:%S")
            
            # Mostrar en consola
            print(f"[{timestamp}] WIF: ${precio:.4f} | RSI: {rsi:.1f} | USDT: ${usdt:.2f} | WIF: {wif:.2f}")
            
            # ===== ENVIAR RSI A TELEGRAM CADA MINUTO =====
            mensaje_rsi = f"⏱️ {timestamp}\n🐕 WIF: ${precio:.4f}\n📊 RSI: {rsi:.1f}"
            
            # Agregar recomendación según RSI
            if rsi <= RSI_COMPRA:
                mensaje_rsi += f"\n🟢 ¡COMPRA! (RSI ≤ {RSI_COMPRA})"
            elif rsi >= RSI_VENTA:
                mensaje_rsi += f"\n🔴 ¡VENTA! (RSI ≥ {RSI_VENTA})"
            else:
                mensaje_rsi += f"\n⚪ NEUTRAL (Rango {RSI_COMPRA}-{RSI_VENTA})"
            
            enviar_telegram(mensaje_rsi)
            # ============================================
            
            # COMPRA AUTOMÁTICA
            if rsi <= RSI_COMPRA and not ya_compro and usdt > 5:
                print(f"🔔 CONDICIÓN COMPRA (RSI {rsi:.1f})")
                comprar_wif(precio, rsi, usdt)
                ya_compro = True
                ya_vendio = False
                time.sleep(30)
            
            # VENTA AUTOMÁTICA
            elif rsi >= RSI_VENTA and not ya_vendio and wif > 0:
                print(f"🔔 CONDICIÓN VENTA (RSI {rsi:.1f})")
                vender_wif(precio, rsi, wif)
                ya_vendio = True
                ya_compro = False
                time.sleep(30)
            
            # Resetear flags
            if rsi > RSI_COMPRA:
                ya_compro = False
            if rsi < RSI_VENTA:
                ya_vendio = False
            
            time.sleep(INTERVALO_SEGUNDOS)
            
        except KeyboardInterrupt:
            print("\n🛑 Bot detenido")
            enviar_telegram("🛑 BOT WIF DETENIDO")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            enviar_telegram(f"⚠️ Error: {str(e)[:100]}")
            time.sleep(60)

if __name__ == "__main__":
    ejecutar()