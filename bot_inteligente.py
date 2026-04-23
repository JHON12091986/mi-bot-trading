# bot_inteligente.py - Bot con RSI y lógica de decisión

import requests
import time
import pandas as pd
import numpy as np

print("=== 🤖 BOT INTELIGENTE DE TRADING ====")
print("Estrategia: RSI (Sobreventa < 30 → COMPRAR)")
print("")

def calcular_rsi(precios, periodo=14):
    """Calcula el RSI a partir de una lista de precios"""
    ganancias = []
    perdidas = []
    
    for i in range(1, len(precios)):
        cambio = precios[i] - precios[i-1]
        if cambio >= 0:
            ganancias.append(cambio)
            perdidas.append(0)
        else:
            ganancias.append(0)
            perdidas.append(abs(cambio))
    
    # Si no hay suficientes datos, devolver 50 (neutral)
    if len(ganancias) < periodo:
        return 50
    
    ganancia_promedio = np.mean(ganancias[-periodo:])
    perdida_promedio = np.mean(perdidas[-periodo:])
    
    if perdida_promedio == 0:
        return 100
    
    rs = ganancia_promedio / perdida_promedio
    rsi = 100 - (100 / (1 + rs))
    return rsi

# Obtener precio actual de NVDA
url = "https://query1.finance.yahoo.com/v8/finance/chart/NVDA"
headers = {"User-Agent": "Mozilla/5.0"}

try:
    respuesta = requests.get(url, headers=headers, timeout=5)
    datos = respuesta.json()
    
    # Precio actual
    precio_actual = datos['chart']['result'][0]['meta']['regularMarketPrice']
    
    # Obtener precios históricos (para calcular RSI)
    precios_historicos = []
    for candle in datos['chart']['result'][0]['indicators']['quote'][0]['close']:
        if candle is not None:
            precios_historicos.append(candle)
    
    # Calcular RSI
    rsi = calcular_rsi(precios_historicos, 14)
    
    print(f"📊 NVDA - NVIDIA Corporation")
    print(f"💰 Precio actual: ${precio_actual:.2f}")
    print(f"📈 RSI (14 periodos): {rsi:.2f}")
    print("")
    
    # Lógica de decisión
    print("=== DECISIÓN DEL BOT ===")
    if rsi < 30:
        print("🔴 RSI indica SOBREVENTA")
        print("✅ RECOMENDACIÓN: COMPRAR")
        print(f"💰 Sugerencia: Invertir hasta $500 en NVDA")
    elif rsi > 70:
        print("🟢 RSI indica SOBRECOMPRA")
        print("⚠️ RECOMENDACIÓN: VENDER o ESPERAR")
        print(f"💵 Sugerencia: Considerar tomar ganancias")
    else:
        print("🟡 RSI en zona NEUTRAL")
        print("⏳ RECOMENDACIÓN: ESPERAR")
        print(f"👀 Sugerencia: Monitorear hasta que RSI baje de 30 o suba de 70")
    
    print("")
    print(f"💡 Tu efectivo disponible: $59,273")
    print("🚀 Bot ejecutado correctamente")
    
except Exception as e:
    print(f"❌ Error: {e}")
    print("Verifica tu conexión a internet")