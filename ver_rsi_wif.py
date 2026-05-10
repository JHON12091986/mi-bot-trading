# ver_rsi_wif.py
import requests
import time

def calcular_rsi(precios, periodo=14):
    """Calcula RSI a partir de una lista de precios"""
    if len(precios) < periodo + 1:
        return 50
    
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
        return 100
    rs = ganancia_prom / perdida_prom
    rsi = 100 - (100 / (1 + rs))
    return round(rsi, 1)

def obtener_rsi_wif(intervalo="1h"):
    """
    Obtiene el RSI de WIF/USDT desde Binance.
    intervalos válidos: 1m, 5m, 15m, 30m, 1h, 2h, 4h, 1d
    """
    try:
        # Obtener datos históricos de Binance
        url = f"https://api.binance.com/api/v3/klines?symbol=WIFUSDT&interval={intervalo}&limit=50"
        resp = requests.get(url, timeout=10)
        datos = resp.json()
        
        # Extraer precios de cierre
        precios = [float(candle[4]) for candle in datos]
        precio_actual = precios[-1]
        rsi = calcular_rsi(precios)
        
        return precio_actual, rsi
    except Exception as e:
        print(f"Error: {e}")
        return None, None

# ========== EJECUCIÓN ==========
if __name__ == "__main__":
    print("🐕 WIF/USDT - RSI en tiempo real")
    print("Presiona Ctrl+C para salir\n")
    
    while True:
        precio, rsi = obtener_rsi_wif("1h")
        
        if precio and rsi:
            # Determinar señal
            if rsi <= 30:
                emoji = "🟢"
                senal = "COMPRA (sobreventa)"
            elif rsi >= 70:
                emoji = "🔴"
                senal = "VENTA (sobrecompra)"
            else:
                emoji = "🟡"
                senal = "ESPERAR"
            
            print(f"[{time.strftime('%H:%M:%S')}] WIF: ${precio:.4f} | RSI: {rsi:.1f} | {emoji} {senal}")
            
        time.sleep(60)  # Actualiza cada 60 segundos