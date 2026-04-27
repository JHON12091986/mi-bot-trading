import os
import json
import time
import requests
from datetime import datetime
from dotenv import load_dotenv
from binance.client import Client
import pandas as pd

load_dotenv()

# Credenciales
API_KEY = os.getenv("BINANCE_API_KEY")
SECRET_KEY = os.getenv("BINANCE_SECRET_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# *** CAMBIO CLAVE: testnet=True en lugar de demo=True ***
client = Client(API_KEY, SECRET_KEY, testnet=True)
print("✅ Conectado a Binance Testnet (entorno de pruebas)")

# 10 activos con umbrales y montos
ACTIVOS = {
    "BTCUSDT": {"nombre": "Bitcoin", "compra_rsi": 30, "venta_rsi": 70, "monto": 500},
    "ETHUSDT": {"nombre": "Ethereum", "compra_rsi": 30, "venta_rsi": 70, "monto": 500},
    "BNBUSDT": {"nombre": "Binance Coin", "compra_rsi": 30, "venta_rsi": 70, "monto": 500},
    "SOLUSDT": {"nombre": "Solana", "compra_rsi": 30, "venta_rsi": 70, "monto": 500},
    "ADAUSDT": {"nombre": "Cardano", "compra_rsi": 30, "venta_rsi": 70, "monto": 300},
    "DOTUSDT": {"nombre": "Polkadot", "compra_rsi": 30, "venta_rsi": 70, "monto": 300},
    "LINKUSDT": {"nombre": "Chainlink", "compra_rsi": 30, "venta_rsi": 70, "monto": 300},
    "MATICUSDT": {"nombre": "Polygon", "compra_rsi": 30, "venta_rsi": 70, "monto": 300},
    "ATOMUSDT": {"nombre": "Cosmos", "compra_rsi": 30, "venta_rsi": 70, "monto": 300},
    "UNIUSDT": {"nombre": "Uniswap", "compra_rsi": 30, "venta_rsi": 70, "monto": 300},
}

# Estado persistente
ESTADO_FILE = "cartera_binance.json"
if os.path.exists(ESTADO_FILE):
    with open(ESTADO_FILE) as f:
        data = json.load(f)
        EFECTIVO = data.get("efectivo", 10000.0)
        POSICIONES = data.get("posiciones", {s: {"cantidad": 0.0, "precio_medio": 0.0} for s in ACTIVOS})
else:
    EFECTIVO = 10000.0
    POSICIONES = {s: {"cantidad": 0.0, "precio_medio": 0.0} for s in ACTIVOS}

def guardar_estado():
    with open(ESTADO_FILE, "w") as f:
        json.dump({"efectivo": EFECTIVO, "posiciones": POSICIONES}, f, indent=4)

def rsi(simbolo):
    try:
        velas = client.get_klines(symbol=simbolo, interval=Client.KLINE_INTERVAL_1HOUR, limit=15)
        closes = [float(v[4]) for v in velas]
        df = pd.DataFrame({"close": closes})
        delta = df["close"].diff()
        ganancia = delta.clip(lower=0).rolling(14).mean()
        perdida = (-delta.clip(upper=0)).rolling(14).mean()
        rs = ganancia / perdida
        return 100 - (100 / (1 + rs)).iloc[-1]
    except:
        return 50.0

def precio(simbolo):
    try:
        return float(client.get_symbol_ticker(symbol=simbolo)["price"])
    except:
        return None

def enviar_telegram(msg):
    if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
        try:
            requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                          json={"chat_id": TELEGRAM_CHAT_ID, "text": msg}, timeout=5)
        except:
            pass

def comprar(simbolo, monto):
    global EFECTIVO
    if EFECTIVO < monto:
        return
    p = precio(simbolo)
    if not p:
        return
    orden = client.order_market_buy(symbol=simbolo, quoteOrderQty=monto)
    cant = float(orden["executedQty"])
    if cant > 0:
        vieja_cant = POSICIONES[simbolo]["cantidad"]
        viejo_pm = POSICIONES[simbolo]["precio_medio"]
        if vieja_cant == 0:
            nuevo_pm = p
        else:
            nuevo_pm = (vieja_cant * viejo_pm + cant * p) / (vieja_cant + cant)
        POSICIONES[simbolo]["cantidad"] += cant
        POSICIONES[simbolo]["precio_medio"] = nuevo_pm
        EFECTIVO -= monto
        guardar_estado()
        msg = f"🔴 COMPRA {ACTIVOS[simbolo]['nombre']}\nPrecio: ${p:.2f}\nCantidad: {cant:.6f}\nInvertido: ${monto:.2f}\nEfectivo: ${EFECTIVO:.2f}"
        print(msg)
        enviar_telegram(msg)

def vender(simbolo):
    global EFECTIVO
    cant = POSICIONES[simbolo]["cantidad"]
    if cant <= 0:
        return
    p = precio(simbolo)
    if not p:
        return
    orden = client.order_market_sell(symbol=simbolo, quantity=cant)
    vendido = float(orden["executedQty"])
    if vendido > 0:
        ingreso = vendido * p
        EFECTIVO += ingreso
        POSICIONES[simbolo]["cantidad"] = 0
        POSICIONES[simbolo]["precio_medio"] = 0
        guardar_estado()
        msg = f"🟢 VENTA {ACTIVOS[simbolo]['nombre']}\nPrecio: ${p:.2f}\nCantidad: {vendido:.6f}\nIngreso: ${ingreso:.2f}\nEfectivo: ${EFECTIVO:.2f}"
        print(msg)
        enviar_telegram(msg)

def mostrar_resumen():
    total_valor = 0
    total_invertido = 0
    for sym, pos in POSICIONES.items():
        if pos["cantidad"] > 0:
            p = precio(sym)
            if p:
                valor = pos["cantidad"] * p
                costo = pos["cantidad"] * pos["precio_medio"]
                total_valor += valor
                total_invertido += costo
    gp = total_valor - total_invertido
    enviar_telegram(f"📊 Resumen | Efectivo: ${EFECTIVO:.2f} | Total: ${EFECTIVO + total_valor:.2f} | G/P: ${gp:.2f}")

# Bucle principal
print("🚀 Bot 10 activos Binance Testnet iniciado")
enviar_telegram("🤖 Bot activo en modo Testnet (dinero virtual)")
while True:
    try:
        for simbolo, cfg in ACTIVOS.items():
            p = precio(simbolo)
            if not p:
                continue
            r = rsi(simbolo)
            print(f"{simbolo} ${p:.2f} | RSI {r:.1f} | pos: {POSICIONES[simbolo]['cantidad']:.6f}")
            
            if r < cfg["compra_rsi"] and EFECTIVO >= cfg["monto"]:
                comprar(simbolo, cfg["monto"])
            elif r > cfg["venta_rsi"] and POSICIONES[simbolo]["cantidad"] > 0:
                vender(simbolo)
        
        mostrar_resumen()
        time.sleep(300)  # 5 minutos
        
    except KeyboardInterrupt:
        print("\n🛑 Bot detenido")
        enviar_telegram("🛑 Bot detenido manualmente")
        break
    except Exception as e:
        print(f"Error: {e}")
        time.sleep(60)