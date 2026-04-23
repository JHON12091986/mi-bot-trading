# bot_experto.py - Bot completo con historial, alertas y cálculo de posición

import requests
import time
import pandas as pd
import numpy as np
import json
import os
from datetime import datetime

print("=== 🧠 BOT EXPERTO DE TRADING ====")
print("Módulos: Historial | Alertas RSI | Tamaño de posición")
print("")

# ==================== CONFIGURACIÓN ====================
CAPITAL_DISPONIBLE = 50  # TUS $50 REALES
ACTIVO = "NVDA"
RSI_UMBRAL_COMPRA = 30
RSI_UMBRAL_VENTA = 70
ARCHIVO_HISTORIAL = "historial_nvda.json"

# ==================== FUNCIONES ====================

def calcular_rsi(precios, periodo=14):
    """Calcula el RSI a partir de una lista de precios"""
    if len(precios) < periodo + 1:
        return 50
    
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
    
    ganancia_promedio = np.mean(ganancias[-periodo:])
    perdida_promedio = np.mean(perdidas[-periodo:])
    
    if perdida_promedio == 0:
        return 100
    
    rs = ganancia_promedio / perdida_promedio
    rsi = 100 - (100 / (1 + rs))
    return rsi

def obtener_precio_y_rsi():
    """Obtiene precio actual y calcula RSI"""
    url = "https://query1.finance.yahoo.com/v8/finance/chart/NVDA"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    respuesta = requests.get(url, headers=headers, timeout=5)
    datos = respuesta.json()
    
    precio_actual = datos['chart']['result'][0]['meta']['regularMarketPrice']
    
    # Obtener precios históricos
    precios = []
    for candle in datos['chart']['result'][0]['indicators']['quote'][0]['close']:
        if candle is not None:
            precios.append(candle)
    
    rsi = calcular_rsi(precios, 14)
    
    return precio_actual, rsi, precios

def guardar_historial(precio, rsi, decision):
    """Guarda el historial en un archivo JSON"""
    historial = []
    if os.path.exists(ARCHIVO_HISTORIAL):
        with open(ARCHIVO_HISTORIAL, 'r') as f:
            historial = json.load(f)
    
    historial.append({
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "precio": round(precio, 2),
        "rsi": round(rsi, 2),
        "decision": decision
    })
    
    # Guardar solo últimos 100 registros
    historial = historial[-100:]
    
    with open(ARCHIVO_HISTORIAL, 'w') as f:
        json.dump(historial, f, indent=2)
    
    return historial

def calcular_tamano_posicion(precio_actual, rsi, capital=CAPITAL_DISPONIBLE):
    """Calcula cuántas unidades comprar según el RSI y capital disponible"""
    
    if rsi > 70:
        return 0, "VENTA", "RSI alto, momento de vender"
    
    if rsi < 30:
        # RSI bajo: más agresivo (hasta 80% del capital)
        porcentaje_invertir = 0.80
    elif rsi < 40:
        porcentaje_invertir = 0.50
    elif rsi < 50:
        porcentaje_invertir = 0.30
    elif rsi < 60:
        porcentaje_invertir = 0.15
    else:
        porcentaje_invertir = 0.05
    
    monto_invertir = capital * porcentaje_invertir
    unidades = monto_invertir / precio_actual
    
    return unidades, monto_invertir, porcentaje_invertir

def mostrar_historial(historial):
    """Muestra las últimas 5 lecturas del historial"""
    if not historial:
        print("📭 Aún no hay historial")
        return
    
    print("\n📜 HISTORIAL (últimas 5 lecturas):")
    print("-" * 60)
    for registro in historial[-5:]:
        print(f"  🕐 {registro['fecha']} | Precio: ${registro['precio']} | RSI: {registro['rsi']} | {registro['decision']}")
    print("-" * 60)

def verificar_alerta(historial, rsi):
    """Verifica si hay una alerta nueva (RSI cruzó umbral)"""
    if len(historial) < 2:
        return False, ""
    
    rsi_anterior = historial[-2]['rsi']
    
    if rsi_anterior > RSI_UMBRAL_COMPRA and rsi <= RSI_UMBRAL_COMPRA:
        return True, f"🔔 ALERTA: RSI BAJÓ DE {RSI_UMBRAL_COMPRA} ({rsi_anterior:.1f} → {rsi:.1f}) - ¡OPORTUNIDAD DE COMPRA!"
    
    if rsi_anterior < RSI_UMBRAL_VENTA and rsi >= RSI_UMBRAL_VENTA:
        return True, f"⚠️ ALERTA: RSI SUBIÓ DE {RSI_UMBRAL_VENTA} ({rsi_anterior:.1f} → {rsi:.1f}) - ¡CONSIDERA VENDER!"
    
    return False, ""

# ==================== EJECUCIÓN PRINCIPAL ====================

try:
    # Obtener datos
    precio, rsi, precios = obtener_precio_y_rsi()
    
    print(f"📊 {ACTIVO} - NVIDIA Corporation")
    print(f"💰 Precio actual: ${precio:.2f}")
    print(f"📈 RSI (14 periodos): {rsi:.2f}")
    print("")
    
    # Decisión del bot
    print("=== 🤖 DECISIÓN DEL BOT ===")
    
    if rsi < RSI_UMBRAL_COMPRA:
        decision = "COMPRAR"
        print(f"🔴 RSI indica SOBREVENTA ({rsi:.2f} < {RSI_UMBRAL_COMPRA})")
        print(f"✅ RECOMENDACIÓN: {decision}")
    elif rsi > RSI_UMBRAL_VENTA:
        decision = "VENDER"
        print(f"🟢 RSI indica SOBRECOMPRA ({rsi:.2f} > {RSI_UMBRAL_VENTA})")
        print(f"⚠️ RECOMENDACIÓN: {decision}")
    else:
        decision = "ESPERAR"
        print(f"🟡 RSI en zona NEUTRAL ({RSI_UMBRAL_COMPRA} < {rsi:.2f} < {RSI_UMBRAL_VENTA})")
        print(f"⏳ RECOMENDACIÓN: {decision}")
    
    print("")
    
    # Cálculo de tamaño de posición (para COMPRAR)
    if decision == "COMPRAR":
        unidades, monto, porcentaje = calcular_tamano_posicion(precio, rsi)
        print("=== 📐 TAMAÑO DE POSICIÓN RECOMENDADO ===")
        print(f"💰 Capital disponible: ${CAPITAL_DISPONIBLE}")
        print(f"📊 Porcentaje a invertir: {porcentaje * 100:.0f}%")
        print(f"💵 Monto a invertir: ${monto:.2f}")
        print(f"📈 Unidades a comprar: {unidades:.4f}")
        print(f"🎯 Precio límite: ${precio:.2f}")
        print("")
        print("👉 En eToro: Busca NVDA → Cantidad personalizada → Ingresa el monto en $")
    
    # Guardar historial
    historial = guardar_historial(precio, rsi, decision)
    
    # Mostrar historial
    mostrar_historial(historial)
    
    # Verificar alertas
    alerta, mensaje = verificar_alerta(historial, rsi)
    if alerta:
        print("")
        print("=" * 60)
        print(mensaje)
        print("=" * 60)
    
    print("")
    print("🚀 Bot ejecutado correctamente")
    print(f"💡 Sugerencia: Ejecuta este script varias veces al día para monitorear el RSI")
    
except Exception as e:
    print(f"❌ Error: {e}")
    print("Verifica tu conexión a internet")