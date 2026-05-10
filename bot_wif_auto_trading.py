import os
import time
import hmac
import hashlib
import requests
import json
from datetime import datetime
from dotenv import load_dotenv

# ========== CONFIGURACIÓN ==========
load_dotenv()
API_KEY = os.getenv("iFUsjEoWVYg43fRHpmZDd5Qgwb8jTdSIGOZvWXqxsstB4LAZiaXsOiXQKZSjWTAA")
SECRET_KEY = os.getenv("7pcSCbgPz4G8rwOI6UTDDopmeMRbBzlSSpPFiwZHyOSdbMbK1CfUsVocZdHhdeLQ")
TELEGRAM_TOKEN = os.getenv("8418325481:AAFnfV87o167nAMltPr1n1MvWblw4YofaZ8")
TELEGRAM_CHAT_ID = os.getenv("5326893982")

# PARÁMETROS DE TRADING
SIMBOLO = "WIFUSDT"
RSI_COMPRA = 35      # Comprar cuando RSI baja a 35 o menos
RSI_VENTA = 70       # Vender cuando RSI sube a 70 o más
MONTO_COMPRA_USDT = 5.0  # Monto fijo en USDT por cada compra
INTERVALO_SEGUNDOS = 60   # Revisar cada 60 segundos

# Archivo para evitar comprar/vender repetidamente
ARCHIVO_ESTADO = "bot_wif_estado.json"

# ========== FUNCIONES TELEGRAM ==========
def enviar_telegram(mensaje):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {"chat_id": TELEGRAM_CHAT_ID, "text": mensaje, "parse_mode": "HTML"}
        requests.post(url, json=payload, timeout=10)
        print(f"📱 Mensaje enviado: {mensaje[:50]}...")
    except Exception as e:
        print(f"⚠️ Error Telegram: {e}")

# ========== FUNCIONES BINANCE ==========
def binance_request(endpoint, params=None, method="GET"):
    """Firma y ejecuta request a Binance API"""
    timestamp = int(time.time() * 1000)
    if params is None:
        params = {}
    params["timestamp"] = timestamp
    params["recvWindow"] = 5000
    
    query_string = "&".join([f"{k}={v}" for k, v in params.items()])
    signature = hmac.new(SECRET_KEY.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()
    
    url = f"https://api.binance.com/api/v3/{endpoint}?{query_string}&signature={signature}"
    headers = {"X-MBX-APIKEY": API_KEY}
    
    if method == "GET":
        response = requests.get(url, headers=headers, timeout=10)
    else:
        response = requests.post(url, headers=headers, timeout=10)
    
    return response.json()

def obtener_precio_actual():
    """Obtiene precio actual de WIF/USDT"""
    try:
        url = "https://api.binance.com/api/v3/ticker/price?symbol=WIFUSDT"
        resp = requests.get(url, timeout=10)
        return float(resp.json()["price"])
    except Exception as e:
        print(f"❌ Error obteniendo precio: {e}")
        return None

def obtener_klines(intervalo="1h", limite=50):
    """Obtiene velas históricas para calcular RSI"""
    try:
        url = f"https://api.binance.com/api/v3/klines?symbol=WIFUSDT&interval={intervalo}&limit={limite}"
        resp = requests.get(url, timeout=10)
        data = resp.json()
        return [float(candle[4]) for candle in data]  # Precios de cierre
    except Exception as e:
        print(f"❌ Error obteniendo klines: {e}")
        return None

def calcular_rsi(precios, periodo=14):
    """Calcula RSI (Relative Strength Index)"""
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
    rsi = 100 - (100 / (1 + rs))
    return round(rsi, 1)

def obtener_saldo_usdt():
    """Obtiene saldo disponible de USDT"""
    try:
        account = binance_request("account")
        for asset in account["balances"]:
            if asset["asset"] == "USDT":
                return float(asset["free"])
        return 0.0
    except Exception as e:
        print(f"❌ Error obteniendo saldo: {e}")
        return None

def obtener_posicion_wif():
    """Obtiene cantidad de WIF en cartera"""
    try:
        account = binance_request("account")
        for asset in account["balances"]:
            if asset["asset"] == "WIF":
                return float(asset["free"])
        return 0.0
    except Exception as e:
        print(f"❌ Error obteniendo posición: {e}")
        return None

def orden_compra_market(cantidad_wif):
    """Ejecuta orden de compra a mercado"""
    try:
        params = {
            "symbol": SIMBOLO,
            "side": "BUY",
            "type": "MARKET",
            "quantity": round(cantidad_wif, 6)
        }
        result = binance_request("order", params, method="POST")
        if "orderId" in result:
            return True, result
        return False, result
    except Exception as e:
        return False, str(e)

def orden_compra_usdt(monto_usdt):
    """Compra usando monto en USDT (más preciso)"""
    try:
        params = {
            "symbol": SIMBOLO,
            "side": "BUY",
            "type": "MARKET",
            "quoteOrderQty": round(monto_usdt, 2)
        }
        result = binance_request("order", params, method="POST")
        if "orderId" in result:
            return True, result
        return False, result
    except Exception as e:
        return False, str(e)

def orden_venta_market(cantidad_wif):
    """Ejecuta orden de venta a mercado"""
    try:
        params = {
            "symbol": SIMBOLO,
            "side": "SELL",
            "type": "MARKET",
            "quantity": round(cantidad_wif, 6)
        }
        result = binance_request("order", params, method="POST")
        if "orderId" in result:
            return True, result
        return False, result
    except Exception as e:
        return False, str(e)

def cargar_estado():
    """Carga el estado de la última operación para evitar repeticiones"""
    if os.path.exists(ARCHIVO_ESTADO):
        with open(ARCHIVO_ESTADO, "r") as f:
            return json.load(f)
    return {"ultima_accion": None, "ultimo_rsi": 50, "ultimo_precio": 0}

def guardar_estado(accion, rsi, precio):
    """Guarda el estado de la última operación"""
    estado = {
        "ultima_accion": accion,
        "ultimo_rsi": rsi,
        "ultimo_precio": precio,
        "fecha": datetime.now().isoformat()
    }
    with open(ARCHIVO_ESTADO, "w") as f:
        json.dump(estado, f, indent=4)

# ========== LÓGICA PRINCIPAL ==========
def ejecutar_bot():
    print("=" * 60)
    print("🐕 BOT WIF - TRADING AUTOMÁTICO REAL")
    print(f"📅 Iniciado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🎯 Estrategia: Comprar RSI ≤ {RSI_COMPRA} | Vender RSI ≥ {RSI_VENTA}")
    print(f"💰 Monto por compra: ${MONTO_COMPRA_USDT} USDT")
    print(f"⏱️  Revisando cada {INTERVALO_SEGUNDOS} segundos")
    print("=" * 60)
    
    enviar_telegram(f"🐕 BOT WIF INICIADO\n🎯 Comprar RSI ≤ {RSI_COMPRA} | Vender RSI ≥ {RSI_VENTA}\n💰 Monto: ${MONTO_COMPRA_USDT}")
    
    estado = cargar_estado()
    
    while True:
        try:
            # 1. Obtener datos del mercado
            precio = obtener_precio_actual()
            if precio is None:
                time.sleep(30)
                continue
            
            klines = obtener_klines(intervalo="1h", limite=50)
            if klines is None:
                time.sleep(30)
                continue
            
            rsi = calcular_rsi(klines)
            
            # 2. Obtener saldos
            saldo_usdt = obtener_saldo_usdt()
            posicion_wif = obtener_posicion_wif()
            
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] WIF: ${precio:.4f} | RSI: {rsi:.1f} | USDT: ${saldo_usdt:.2f} | WIF: {posicion_wif:.4f}")
            
            # 3. LÓGICA DE COMPRA (RSI bajo)
            if rsi <= RSI_COMPRA and saldo_usdt >= MONTO_COMPRA_USDT:
                print(f"🔴 SEÑAL DE COMPRA DETECTADA - RSI: {rsi:.1f} ≤ {RSI_COMPRA}")
                
                exito, resultado = orden_compra_usdt(MONTO_COMPRA_USDT)
                
                if exito:
                    precio_compra = float(resultado.get("fills", [{}])[0].get("price", precio))
                    cantidad_comprada = float(resultado.get("executedQty", 0))
                    mensaje = f"""🟢 <b>COMPRA EJECUTADA</b>
🐕 WIF/USDT
💰 Precio: ${precio_compra:.4f}
📊 RSI: {rsi:.1f}
📦 Cantidad: {cantidad_comprada:.4f} WIF
💵 Total: ${MONTO_COMPRA_USDT} USDT
⏰ {datetime.now().strftime('%H:%M:%S')}"""
                    enviar_telegram(mensaje)
                    guardar_estado("COMPRA", rsi, precio_compra)
                else:
                    enviar_telegram(f"❌ <b>ERROR EN COMPRA</b>\n{resultado}")
                    print(f"❌ Error compra: {resultado}")
            
            # 4. LÓGICA DE VENTA (RSI alto)
            elif rsi >= RSI_VENTA and posicion_wif > 0:
                print(f"🟢 SEÑAL DE VENTA DETECTADA - RSI: {rsi:.1f} ≥ {RSI_VENTA}")
                
                exito, resultado = orden_venta_market(posicion_wif)
                
                if exito:
                    precio_venta = float(resultado.get("fills", [{}])[0].get("price", precio))
                    cantidad_vendida = float(resultado.get("executedQty", 0))
                    total_usdt = cantidad_vendida * precio_venta
                    mensaje = f"""🔴 <b>VENTA EJECUTADA</b>
🐕 WIF/USDT
💰 Precio: ${precio_venta:.4f}
📊 RSI: {rsi:.1f}
📦 Cantidad: {cantidad_vendida:.4f} WIF
💵 Total: ${total_usdt:.2f} USDT
⏰ {datetime.now().strftime('%H:%M:%S')}"""
                    enviar_telegram(mensaje)
                    guardar_estado("VENTA", rsi, precio_venta)
                else:
                    enviar_telegram(f"❌ <b>ERROR EN VENTA</b>\n{resultado}")
                    print(f"❌ Error venta: {resultado}")
            
            # 5. Esperar antes de la siguiente iteración
            time.sleep(INTERVALO_SEGUNDOS)
            
        except KeyboardInterrupt:
            print("\n🛑 Bot detenido por el usuario")
            enviar_telegram("🛑 BOT WIF DETENIDO MANUALMENTE")
            break
        except Exception as e:
            print(f"❌ Error inesperado: {e}")
            enviar_telegram(f"⚠️ ERROR EN BOT WIF:\n{str(e)[:100]}")
            time.sleep(60)

# ========== EJECUCIÓN ==========
if __name__ == "__main__":
    ejecutar_bot()