# cartera_ia_ampliada.py - Monitoreo con simulación, resumen y recomendaciones

import requests
import json
import os
from datetime import datetime

# ========== CONFIGURACIÓN TELEGRAM ==========
TELEGRAM_TOKEN = "8418325481:AAFnfV87o167nAMltPr1n1MvWblw4YofaZ8"
TELEGRAM_CHAT_ID = "5326893982"

def enviar_telegram(mensaje):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": mensaje}, timeout=5)
    except Exception as e:
        print(f"⚠️ Error Telegram: {e}")

# ========== CONFIGURACIÓN DE AUTOMATIZACIÓN ==========
AUTO_COMPRAR = True   # True = compra solo, False = solo alerta
AUTO_VENDER = True    # True = vende solo, False = solo alerta

REGLAS_AUTO = {
    "META": {
        "compra_rsi_min": 25,
        "venta_rsi_max": 75,
        "cantidad_max_compra": 5000,
        "cantidad_min_venta": 0.5
    },
    "BTC": {
        "compra_rsi_min": 30,
        "venta_rsi_max": 70,
        "cantidad_max_compra": 10000,
        "cantidad_min_venta": 0.3
    }
}

# ========== TU PORTAFOLIO REAL (se actualiza automáticamente) ==========
PORTAFOLIO_REAL = {
    "BTC": {
        "cantidad": 0.263796,
        "precio_entrada": 75815.99,
        "valor": 20488.85
    },
    "META": {
        "cantidad": 14.94192,
        "precio_entrada": 669.04702,
        "valor": 9936.83
    }
}

EFECTIVO_DISPONIBLE = 59911.00

# ========== CONFIGURACIÓN CARTERA ==========
CARTERA = {
    "NVDA": "NVIDIA",
    "AVGO": "Broadcom",
    "MU": "Micron Technology",
    "ANET": "Arista Networks",
    "MRVL": "Marvell Technology",
    "MSFT": "Microsoft",
    "AMZN": "Amazon",
    "LLY": "Eli Lilly",
    "V": "Visa",
    "META": "Meta Platforms"
}

# ========== FUNCIONES ==========
def calcular_rsi(precios, periodo=14):
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
    ganancia_promedio = sum(ganancias[-periodo:]) / periodo
    perdida_promedio = sum(perdidas[-periodo:]) / periodo
    if perdida_promedio == 0:
        return 100
    rs = ganancia_promedio / perdida_promedio
    return 100 - (100 / (1 + rs))

def obtener_precio_rsi(ticker):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
    headers = {"User-Agent": "Mozilla/5.0"}
    respuesta = requests.get(url, headers=headers, timeout=10)
    datos = respuesta.json()
    precio = datos['chart']['result'][0]['meta']['regularMarketPrice']
    precios = []
    for candle in datos['chart']['result'][0]['indicators']['quote'][0]['close']:
        if candle is not None:
            precios.append(candle)
    return precio, calcular_rsi(precios, 14)

def guardar_simulacion(activo, accion, precio, rsi):
    archivo = "historial_simulado.json"
    datos = []
    if os.path.exists(archivo):
        with open(archivo, "r") as f:
            datos = json.load(f)
    datos.append({
        "fecha": datetime.now().isoformat(),
        "activo": activo,
        "accion": accion,
        "precio": precio,
        "rsi": rsi
    })
    with open(archivo, "w") as f:
        json.dump(datos, f, indent=4)

def guardar_orden_simulada(activo, accion, precio, rsi, recomendacion=""):
    archivo = "ordenes_simuladas.json"
    datos = []
    if os.path.exists(archivo):
        with open(archivo, "r") as f:
            datos = json.load(f)
    nueva_orden = {
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "activo": activo,
        "accion": accion,
        "precio": precio,
        "rsi": rsi,
        "recomendacion": recomendacion
    }
    datos.append(nueva_orden)
    with open(archivo, "w") as f:
        json.dump(datos, f, indent=4)
    print(f"   📝 Orden simulada guardada: {accion} {activo} a ${precio:.2f}")

def guardar_en_excel(activo, accion, precio, rsi, cantidad, total):
    archivo = "mis_operaciones.csv"
    archivo_existe = os.path.exists(archivo)
    with open(archivo, "a", newline='', encoding='utf-8') as f:
        if not archivo_existe:
            f.write("Fecha,Activo,Acción,Precio,RSI,Cantidad,Total,Saldo Efectivo\n")
        f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')},{activo},{accion},{precio},{rsi},{cantidad},{total},{EFECTIVO_DISPONIBLE}\n")
    print(f"   📊 Operación guardada en mis_operaciones.csv")

def guardar_saldo_actual(activo, precio_actual, rsi):
    archivo = "saldo_portafolio.json"
    datos = {}
    if os.path.exists(archivo):
        with open(archivo, "r") as f:
            datos = json.load(f)
    datos["fecha_actualizacion"] = datetime.now().isoformat()
    datos["efectivo"] = EFECTIVO_DISPONIBLE
    datos["portafolio"] = PORTAFOLIO_REAL.copy()
    if activo == "BTC-USD" and "BTC" in PORTAFOLIO_REAL:
        datos["portafolio"]["BTC"]["valor_actual"] = precio_actual * PORTAFOLIO_REAL["BTC"]["cantidad"]
        datos["portafolio"]["BTC"]["rsi_actual"] = rsi
    elif activo == "META" and "META" in PORTAFOLIO_REAL:
        datos["portafolio"]["META"]["valor_actual"] = precio_actual * PORTAFOLIO_REAL["META"]["cantidad"]
        datos["portafolio"]["META"]["rsi_actual"] = rsi
    with open(archivo, "w") as f:
        json.dump(datos, f, indent=4)
    print(f"   💾 Saldo guardado en saldo_portafolio.json")

def ejecutar_orden_automatica(activo, accion, precio, rsi, cantidad):
    global EFECTIVO_DISPONIBLE, PORTAFOLIO_REAL
    archivo_ordenes = "ordenes_automaticas.json"
    datos = []
    if os.path.exists(archivo_ordenes):
        with open(archivo_ordenes, "r") as f:
            datos = json.load(f)
    orden = {
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "activo": activo,
        "accion": accion,
        "precio": precio,
        "rsi": rsi,
        "cantidad": cantidad,
        "total": precio * cantidad
    }
    if accion == "COMPRA":
        EFECTIVO_DISPONIBLE -= precio * cantidad
        if activo in PORTAFOLIO_REAL:
            PORTAFOLIO_REAL[activo]["cantidad"] += cantidad
            PORTAFOLIO_REAL[activo]["valor"] += precio * cantidad
    elif accion == "VENTA":
        EFECTIVO_DISPONIBLE += precio * cantidad
        if activo in PORTAFOLIO_REAL:
            PORTAFOLIO_REAL[activo]["cantidad"] -= cantidad
            PORTAFOLIO_REAL[activo]["valor"] -= precio * cantidad
    datos.append(orden)
    with open(archivo_ordenes, "w") as f:
        json.dump(datos, f, indent=4)
    print(f"   🤖 ORDEN AUTOMÁTICA: {accion} {cantidad:.2f} {activo} a ${precio:.2f}")
    print(f"   💰 Nuevo efectivo: ${EFECTIVO_DISPONIBLE:.2f}")
    enviar_telegram(f"🤖 ORDEN AUTOMÁTICA\n{accion} {cantidad:.2f} {activo}\nPrecio: ${precio:.2f}\nRSI: {rsi:.1f}\nEfectivo: ${EFECTIVO_DISPONIBLE:.2f}")

def generar_resumen(oportunidades, recomendaciones):
    hoy = datetime.now().strftime("%Y-%m-%d")
    resumen = f"""
========================================
📅 RESUMEN DEL DÍA {hoy}
========================================
🔔 Señales detectadas: {len(oportunidades)}
🎯 Recomendaciones: {len(recomendaciones)}
💰 Efectivo disponible: ${EFECTIVO_DISPONIBLE:.2f}
========================================
"""
    for rec in recomendaciones:
        resumen += f"\n{rec}"
    with open("resumen_dia.txt", "w", encoding="utf-8") as f:
        f.write(resumen)
    print("✅ Resumen guardado en resumen_dia.txt")

# ========== MENSAJE DE INICIO ==========
enviar_telegram("🐞 Bot reiniciado con AUTOMATIZACIÓN - Socio Jhon")

print("=== 🚀 CARTERA IA AMPLIADA (MODO AUTOMÁTICO) ===")
print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 60)

oportunidades = []
recomendaciones = []

# ========== MONITOREO DE ACTIVOS ==========
for ticker, nombre in CARTERA.items():
    try:
        precio, rsi = obtener_precio_rsi(ticker)
        if rsi < 30:
            decision = "🔴 COMPRAR"
            mensaje = f"🔴 COMPRA {ticker} - {nombre}\n💰 ${precio:.2f} | RSI: {rsi:.1f}"
            enviar_telegram(mensaje)
            guardar_simulacion(ticker, "COMPRA", precio, rsi)
            oportunidades.append(f"{ticker} (COMPRA RSI:{rsi:.0f})")
            if AUTO_COMPRAR and ticker in REGLAS_AUTO and rsi <= REGLAS_AUTO[ticker]["compra_rsi_min"]:
                cantidad = REGLAS_AUTO[ticker]["cantidad_max_compra"] / precio
                ejecutar_orden_automatica(ticker, "COMPRA", precio, rsi, cantidad)
        elif rsi > 70:
            decision = "🟢 VENDER"
            mensaje = f"🟢 VENTA {ticker} - {nombre}\n💰 ${precio:.2f} | RSI: {rsi:.1f}"
            enviar_telegram(mensaje)
            guardar_simulacion(ticker, "VENTA", precio, rsi)
            oportunidades.append(f"{ticker} (VENTA RSI:{rsi:.0f})")
            if AUTO_VENDER and ticker in REGLAS_AUTO and rsi >= REGLAS_AUTO[ticker]["venta_rsi_max"] and ticker in PORTAFOLIO_REAL:
                cantidad = PORTAFOLIO_REAL[ticker]["cantidad"] * REGLAS_AUTO[ticker]["cantidad_min_venta"]
                if cantidad > 0:
                    ejecutar_orden_automatica(ticker, "VENTA", precio, rsi, cantidad)
        else:
            decision = "🟡 ESPERAR"
        print(f"{decision} {ticker} - {nombre}")
        print(f"     💰 ${precio:.2f} | RSI: {rsi:.1f}")
        if ticker == "META" and ticker in PORTAFOLIO_REAL:
            guardar_saldo_actual(ticker, precio, rsi)
        print("")
    except Exception as e:
        print(f"❌ {ticker}: Error - {e}\n")

# ========== MONITOREO BTC ==========
try:
    precio_btc, rsi_btc = obtener_precio_rsi("BTC-USD")
    if rsi_btc > 70:
        recomendacion_btc = f"⚠️ BTC RSI {rsi_btc:.1f} > 70"
        recomendaciones.append(recomendacion_btc)
        enviar_telegram(f"🟢 VENTA BTC\n💰 ${precio_btc:.2f} | RSI: {rsi_btc:.1f}")
        guardar_simulacion("BTC", "VENTA", precio_btc, rsi_btc)
        if AUTO_VENDER and "BTC" in REGLAS_AUTO and rsi_btc >= REGLAS_AUTO["BTC"]["venta_rsi_max"] and "BTC" in PORTAFOLIO_REAL:
            cantidad = PORTAFOLIO_REAL["BTC"]["cantidad"] * REGLAS_AUTO["BTC"]["cantidad_min_venta"]
            if cantidad > 0:
                ejecutar_orden_automatica("BTC", "VENTA", precio_btc, rsi_btc, cantidad)
    elif rsi_btc < 30:
        if AUTO_COMPRAR and "BTC" in REGLAS_AUTO and rsi_btc <= REGLAS_AUTO["BTC"]["compra_rsi_min"]:
            cantidad = REGLAS_AUTO["BTC"]["cantidad_max_compra"] / precio_btc
            ejecutar_orden_automatica("BTC", "COMPRA", precio_btc, rsi_btc, cantidad)
    print(f"🟡 BTC - Bitcoin")
    print(f"     💰 ${precio_btc:.2f} | RSI: {rsi_btc:.1f}")
    guardar_saldo_actual("BTC-USD", precio_btc, rsi_btc)
    print("")
except Exception as e:
    print(f"❌ BTC: Error - {e}\n")

# ========== RESULTADO FINAL ==========
print("=" * 60)
if oportunidades:
    print(f"🎯 OPORTUNIDADES: {', '.join(oportunidades)}")
else:
    print("⏳ Sin oportunidades")
generar_resumen(oportunidades, recomendaciones)
print(f"📊 Total activos: {len(CARTERA)} + BTC")