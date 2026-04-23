# cartera_ia.py - Monitoreo de cartera IA (5 activos)

import requests
import time

# ========== CONFIGURACIÓN ==========
CARTERA = {
    "NVDA": "NVIDIA",
    "AVGO": "Broadcom", 
    "MU": "Micron Technology",
    "ANET": "Arista Networks",
    "MRVL": "Marvell Technology"
}

print("=== 🚀 CARTERA IA - MONITOREO EN VIVO ===")
print(f"📅 {time.strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 50)

for ticker, nombre in CARTERA.items():
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
        headers = {"User-Agent": "Mozilla/5.0"}
        respuesta = requests.get(url, headers=headers, timeout=5)
        datos = respuesta.json()
        
        precio = datos['chart']['result'][0]['meta']['regularMarketPrice']
        
        # Calcular RSI simple
        precios = []
        for candle in datos['chart']['result'][0]['indicators']['quote'][0]['close']:
            if candle is not None:
                precios.append(candle)
        
        # RSI rápido (últimos 14 periodos)
        if len(precios) >= 15:
            ganancias = []
            perdidas = []
            for i in range(-14, 0):
                cambio = precios[i] - precios[i-1]
                if cambio >= 0:
                    ganancias.append(cambio)
                    perdidas.append(0)
                else:
                    ganancias.append(0)
                    perdidas.append(abs(cambio))
            
            avg_gain = sum(ganancias) / 14
            avg_loss = sum(perdidas) / 14
            
            if avg_loss == 0:
                rsi = 100
            else:
                rs = avg_gain / avg_loss
                rsi = 100 - (100 / (1 + rs))
        else:
            rsi = 50
        
        # Decisión
        if rsi < 30:
            decision = "🔴 COMPRAR"
        elif rsi > 70:
            decision = "🟢 VENDER"
        else:
            decision = "🟡 ESPERAR"
        
        print(f"{ticker} - {nombre}")
        print(f"  💰 Precio: ${precio:.2f}")
        print(f"  📊 RSI: {rsi:.1f} | {decision}")
        print("")
        
    except Exception as e:
        print(f"{ticker} - {nombre}: ❌ Error - {e}")
        print("")

print("=" * 50)
print("🚀 Bot ejecutado. Recuerda: COMPRAR solo si RSI < 30")