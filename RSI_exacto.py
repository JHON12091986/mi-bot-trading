import requests
import numpy as np
import time
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv('.env_real')

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# ===== CONFIGURACIÓN =====
INTERVALO_MINUTOS = 45   # Cambia aquí: 30, 45 o 60 minutos

def send_telegram(msg):
    if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
        try:
            requests.post(
                f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                json={'chat_id': TELEGRAM_CHAT_ID, 'text': msg, 'parse_mode': 'HTML'},
                timeout=10
            )
        except Exception as e:
            print(f"Error Telegram: {e}")

def get_rsi():
    url = "https://api.binance.com/api/v3/klines?symbol=WIFUSDT&interval=15m&limit=30"
    data = requests.get(url).json()
    closes = np.array([float(c[4]) for c in data])

    deltas = np.diff(closes)
    gains = np.where(deltas > 0, deltas, 0)
    losses = np.where(deltas < 0, -deltas, 0)

    period = 14
    avg_gain = np.mean(gains[:period])
    avg_loss = np.mean(losses[:period])

    for i in range(period, len(gains)):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period

    rs = avg_gain / avg_loss if avg_loss != 0 else 100
    rsi = 100 - (100 / (1 + rs))
    return round(rsi, 2)

def get_price():
    url = "https://api.binance.com/api/v3/ticker/price?symbol=WIFUSDT"
    data = requests.get(url).json()
    return float(data['price'])

def get_24h_change():
    url = "https://api.binance.com/api/v3/ticker/24hr?symbol=WIFUSDT"
    data = requests.get(url).json()
    return float(data['priceChangePercent'])

def enviar_estado():
    try:
        rsi = get_rsi()
        price = get_price()
        change = get_24h_change()

        if rsi <= 35:
            señal = "🔴 Zona SOBREVENDIDA - Posible COMPRA"
        elif rsi >= 70:
            señal = "🟢 Zona SOBRECOMPRADA - Posible VENTA"
        else:
            señal = "⚪ Zona NEUTRAL - Esperar"

        hora = datetime.now().strftime("%H:%M:%S")
        mensaje = (
            f"<b>🐕 WIF (dogwifhat) - ESTADO ACTUAL</b>\n"
            f"🕐 {hora}\n\n"
            f"💰 Precio: <b>${price:.6f}</b>\n"
            f"📊 RSI (14 períodos 15min): <b>{rsi}</b>\n"
            f"📉 Cambio 24h: <b>{change:+.2f}%</b>\n"
            f"🎯 Señal: {señal}\n\n"
            f"<i>Bot configurado: COMPRA RSI≤35 | VENTA RSI≥70</i>"
        )
        print(mensaje)
        send_telegram(mensaje)
    except Exception as e:
        error_msg = f"❌ Error: {str(e)}"
        print(error_msg)
        send_telegram(error_msg)

# ===== MAIN =====
print(f"🟢 RSI_exacto.py en modo automático")
print(f"📊 Enviando estado a Telegram cada {INTERVALO_MINUTOS} minutos")
send_telegram(f"✅ Monitor RSI WIF iniciado - Enviaré estado cada {INTERVALO_MINUTOS} minutos")

ultimo_envio = time.time()

while True:
    try:
        if time.time() - ultimo_envio >= INTERVALO_MINUTOS * 60:
            enviar_estado()
            ultimo_envio = time.time()
        time.sleep(60)  # Revisa cada 1 minuto
    except KeyboardInterrupt:
        print("\n🛑 Monitor detenido")
        send_telegram("🛑 Monitor RSI WIF detenido")
        break
    except Exception as e:
        print(f"Error: {e}")
        time.sleep(60)