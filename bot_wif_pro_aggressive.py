import requests
import time
import os
from datetime import datetime
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def enviar_telegram(mensaje):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": mensaje}, timeout=5)
        print(f"📱 Mensaje enviado a Telegram")
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
    rsi = 100 - (100 / (1 + rs))
    return round(rsi, 1)

def obtener_precio_rsi_wif():
    """Obtiene precio actual y RSI de WIF/USDT desde Binance"""
    try:
        # Precio actual
        url = "https://api.binance.com/api/v3/ticker/price?symbol=WIFUSDT"
        resp = requests.get(url, timeout=10)
        precio = float(resp.json()["price"])
        
        # Datos históricos para RSI (velas de 1 hora)
        url_klines = "https://api.binance.com/api/v3/klines?symbol=WIFUSDT&interval=1h&limit=50"
        resp_klines = requests.get(url_klines, timeout=10)
        candles = resp_klines.json()
        precios_historicos = [float(c[4]) for c in candles]
        
        rsi = calcular_rsi(precios_historicos)
        return precio, rsi
    except Exception as e:
        print(f"❌ Error obteniendo datos: {e}")
        return None, None

def obtener_saldo_usdt():
    """Obtiene saldo de USDT desde Binance (requiere API key configurada)"""
    try:
        from binance.client import Client
        API_KEY = os.getenv("BINANCE_API_KEY")
        SECRET_KEY = os.getenv("BINANCE_SECRET_KEY")
        
        if not API_KEY or not SECRET_KEY:
            return None
        
        client = Client(API_KEY, SECRET_KEY)
        cuenta = client.get_account()
        for asset in cuenta["balances"]:
            if asset["asset"] == "USDT":
                return float(asset["free"])
        return 0.0
    except Exception as e:
        print(f"⚠️ No se pudo obtener saldo: {e}")
        return None

def enviar_alerta(precio, rsi, saldo_usdt):
    timestamp = datetime.now().strftime("%H:%M:%S")
    
    # Determinar señal (agresiva: compra en 40, vende en 70)
    if rsi <= 40:
        emoji = "🟢"
        senal = "COMPRA MANUAL"
        estrategia = "RSI en zona de sobreventa (≤ 40). Potencial rebote."
        color = "COMPRA"
    elif rsi >= 70:
        emoji = "🔴"
        senal = "VENTA MANUAL"
        estrategia = "RSI en zona de sobrecompra (≥ 70). Tomar ganancias."
        color = "VENTA"
    else:
        emoji = "🟡"
        senal = "ESPERAR"
        estrategia = "RSI en zona neutral. Esperar señal."
        color = "ESPERAR"
    
    saldo_texto = f"${saldo_usdt:.2f}" if saldo_usdt is not None else "No disponible (sin API)"
    
    mensaje = f"""{emoji} **WIF USDT** - {timestamp}

💰 Precio: ${precio:.4f}
📊 RSI: {rsi:.1f}

🎯 **SEÑAL: {senal}**
📌 **Estrategia:** {estrategia}

💵 **Saldo USDT:** {saldo_texto}

⏱️ _Actualizado cada 5 minutos_"""
    
    enviar_telegram(mensaje)
    print(f"{timestamp} | ${precio:.4f} | RSI: {rsi:.1f} | {senal}")

def main():
    print("=" * 50)
    print("🐕 BOT WIF AGRESIVO (COMPRA 40 | VENTA 70)")
    print(f"📅 Iniciado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🔄 Enviando alertas cada 5 minutos...")
    print("Presiona Ctrl+C para detener")
    print("=" * 50)
    
    enviar_telegram("🐕 Bot WIF Agresivo INICIADO\n📊 Comprar en RSI ≤ 40 | Vender en RSI ≥ 70\n⏱️ Alertas cada 5 minutos")
    
    while True:
        try:
            precio, rsi = obtener_precio_rsi_wif()
            
            if precio is not None and rsi is not None:
                saldo = obtener_saldo_usdt()
                enviar_alerta(precio, rsi, saldo)
            else:
                print("❌ Error obteniendo datos, reintentando en 60 segundos...")
                time.sleep(60)
                continue
            
            # Esperar 5 minutos (300 segundos)
            for i in range(300, 0, -1):
                print(f"\r⏳ Próxima actualización en {i} segundos...", end="")
                time.sleep(1)
            print("\r" + " " * 50 + "\r", end="")
            
        except KeyboardInterrupt:
            print("\n\n🛑 Bot detenido por el usuario")
            enviar_telegram("🛑 Bot WIF Agresivo detenido manualmente")
            break
        except Exception as e:
            print(f"\n❌ Error inesperado: {e}")
            enviar_telegram(f"⚠️ Error en bot: {str(e)[:100]}")
            time.sleep(60)

if __name__ == "__main__":
    main()