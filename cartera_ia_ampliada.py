# cartera_ia_ampliada.py - Simulador avanzado con 10 activos (RSI) y Telegram
# Modo: SOLO SIMULACIÓN. No afecta dinero real.
# VERSIÓN MEJORADA - MÁS POTENTE Y PRECISA

import os
import json
import requests
import random
import time
from datetime import datetime
from dotenv import load_dotenv

# ========== MENSAJES DE ÁNIMO ==========
MENSAJES_ANIMO = [
    "¡Vamos, mi Tiburón! 🦈 A seguir dominando el mercado.",
    "Con esta jugada, un pasito más cerca de la libertad financiera. 🚀",
    "El bot trabaja, tú relájate. El mercado nunca duerme. 🌙",
    "¡Excelente compra! El RSI bajo es nuestra oportunidad. 📈",
    "Recuerda: paciencia y disciplina. El bot sigue tu plan. 🧘",
    "Esto es solo el comienzo. Prepárate para surfear la ola. 🌊",
    "Un movimiento más en nuestra bitácora. ¡Vamos por más! 💪",
    "El bot está más afilado que nunca. ¡Acierto seguro! 🎯",
    "Mercado en movimiento, nosotros en control. 😎",
    "Sigue así, mi rey. Estamos construyendo un imperio. 👑"
]

def obtener_mensaje_animo():
    return random.choice(MENSAJES_ANIMO)

# ========== CONFIGURACIÓN TELEGRAM ==========
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

# ========== CONFIGURACIÓN DE LA CARTERA ==========
CARTERA = {
    "NVDA": {"nombre": "NVIDIA", "max_compra_usd": 2500, "compra_rsi_min": 30, "venta_rsi_max": 70, "venta_fraccion": 1.0},
    "AVGO": {"nombre": "Broadcom", "max_compra_usd": 2000, "compra_rsi_min": 30, "venta_rsi_max": 70, "venta_fraccion": 1.0},
    "MU":   {"nombre": "Micron", "max_compra_usd": 1500, "compra_rsi_min": 30, "venta_rsi_max": 70, "venta_fraccion": 1.0},
    "ANET": {"nombre": "Arista Networks", "max_compra_usd": 1500, "compra_rsi_min": 30, "venta_rsi_max": 70, "venta_fraccion": 1.0},
    "MRVL": {"nombre": "Marvell", "max_compra_usd": 1500, "compra_rsi_min": 30, "venta_rsi_max": 70, "venta_fraccion": 1.0},
    "MSFT": {"nombre": "Microsoft", "max_compra_usd": 2500, "compra_rsi_min": 30, "venta_rsi_max": 70, "venta_fraccion": 1.0},
    "AMZN": {"nombre": "Amazon", "max_compra_usd": 2500, "compra_rsi_min": 30, "venta_rsi_max": 70, "venta_fraccion": 1.0},
    "LLY":  {"nombre": "Eli Lilly", "max_compra_usd": 2500, "compra_rsi_min": 25, "venta_rsi_max": 75, "venta_fraccion": 1.0},
    "V":    {"nombre": "Visa", "max_compra_usd": 2000, "compra_rsi_min": 25, "venta_rsi_max": 75, "venta_fraccion": 1.0},
    "META": {"nombre": "Meta", "max_compra_usd": 3000, "compra_rsi_min": 22, "venta_rsi_max": 78, "venta_fraccion": 1.0},
    "BTC":  {"nombre": "Bitcoin", "max_compra_usd": 5000, "compra_rsi_min": 25, "venta_rsi_max": 75, "venta_fraccion": 1.0},
}

# Capital inicial
EFECTIVO = 59911.00
POSICIONES = {ticker: 0.0 for ticker in CARTERA}
ARCHIVO_ESTADO = "simulacion_estado.json"

# Cargar estado guardado
if os.path.exists(ARCHIVO_ESTADO):
    with open(ARCHIVO_ESTADO, "r") as f:
        data = json.load(f)
        EFECTIVO = data.get("efectivo", EFECTIVO)
        POSICIONES.update(data.get("posiciones", {}))

# ========== FUNCIONES PRINCIPALES ==========
def calcular_rsi(precios, periodo=14):
    """Calcula RSI más preciso con manejo de errores"""
    if len(precios) < periodo + 1:
        return 50.0
    
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
    
    # Promedios con manejo de casos extremos
    ganancia_prom = sum(ganancias[-periodo:]) / periodo
    perdida_prom = sum(perdidas[-periodo:]) / periodo
    
    if perdida_prom == 0:
        return 100.0 if ganancia_prom > 0 else 50.0
    
    rs = ganancia_prom / perdida_prom
    rsi = 100 - (100 / (1 + rs))
    return round(rsi, 1)

def obtener_precio_rsi(ticker):
    """Obtiene precio y RSI con reintentos y manejo de errores"""
    max_intentos = 3
    for intento in range(max_intentos):
        try:
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
            headers = {"User-Agent": "Mozilla/5.0"}
            resp = requests.get(url, headers=headers, timeout=15)
            resp.raise_for_status()
            
            datos = resp.json()
            precio = datos['chart']['result'][0]['meta']['regularMarketPrice']
            
            # Extraer precios históricos (manejo de None)
            precios_historicos = []
            for candle in datos['chart']['result'][0]['indicators']['quote'][0]['close']:
                if candle is not None:
                    precios_historicos.append(candle)
            
            if len(precios_historicos) < 15:
                # Si no hay suficientes datos, usar precio actual
                precios_historicos = [precio] * 15
            
            rsi = calcular_rsi(precios_historicos)
            return precio, rsi
            
        except Exception as e:
            print(f"⚠️ Intento {intento+1} fallido para {ticker}: {e}")
            if intento < max_intentos - 1:
                time.sleep(2)
            else:
                print(f"❌ {ticker}: No se pudo obtener datos después de {max_intentos} intentos")
                raise
    
    return None, None

def registrar_orden(ticker, accion, precio, cantidad, rsi, total, efectivo_restante):
    """Registra orden en archivo JSON con más detalles"""
    orden = {
        "fecha": datetime.now().isoformat(),
        "ticker": ticker,
        "accion": accion,
        "precio": precio,
        "cantidad": cantidad,
        "total": total,
        "rsi": rsi,
        "efectivo_restante": efectivo_restante,
        "timestamp_unix": time.time()
    }
    archivo = "ordenes_simuladas.json"
    historial = []
    if os.path.exists(archivo):
        with open(archivo, "r") as f:
            historial = json.load(f)
    historial.append(orden)
    with open(archivo, "w") as f:
        json.dump(historial, f, indent=4)
    print(f"   📝 Orden registrada: {accion} {ticker} - ${total:.2f}")

def guardar_estado():
    """Guarda estado actual de la simulación"""
    with open(ARCHIVO_ESTADO, "w") as f:
        json.dump({
            "efectivo": EFECTIVO, 
            "posiciones": POSICIONES,
            "ultima_actualizacion": datetime.now().isoformat()
        }, f, indent=4)

def generar_guion_youtube(ticker, accion, precio, rsi):
    """Genera guion optimizado para YouTube Shorts"""
    timestamp = datetime.now().strftime("%d/%m/%Y %H:%M")
    if accion == "COMPRA":
        guion = f"""🔥 SEÑAL DE COMPRA - {timestamp}

{ticker} está en zona de sobreventa extrema.
RSI: {rsi:.1f}
Precio actual: ${precio:.2f}

🚀 Estrategia: RSI < {CARTERA[ticker]['compra_rsi_min']}
📈 Potencial rebote técnico.

#TradingBot #Compra #RSI #{ticker}"""
    else:
        guion = f"""⚠️ SEÑAL DE VENTA - {timestamp}

{ticker} alcanzó sobrecompra.
RSI: {rsi:.1f}
Precio actual: ${precio:.2f}

💼 Estrategia: RSI > {CARTERA[ticker]['venta_rsi_max']}
💰 Toma de ganancias.

#TradingBot #Venta #TakeProfit #{ticker}"""
    
    with open("guiones_youtube.txt", "a", encoding="utf-8") as f:
        f.write(f"\n{'='*60}\n{guion}\n{'='*60}\n")
    print(f"   📢 Guion YouTube generado")

def calcular_valor_total():
    """Calcula el valor total actual de la cartera"""
    valor_posiciones = 0
    detalles = []
    for ticker, cant in POSICIONES.items():
        if cant > 0:
            try:
                precio, _ = obtener_precio_rsi(ticker)
                valor = precio * cant
                valor_posiciones += valor
                detalles.append(f"{ticker}: {cant:.4f}u = ${valor:.2f}")
            except:
                detalles.append(f"{ticker}: {cant:.4f}u (precio no disponible)")
    return EFECTIVO + valor_posiciones, valor_posiciones, detalles

# ========== EJECUCIÓN PRINCIPAL ==========
print("="*60)
print("=== 🚀 CARTERA IA MEJORADA (SIMULACIÓN) ===")
print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"💰 Efectivo inicial: ${EFECTIVO:.2f}")
print("="*60)

# Enviar inicio
enviar_telegram(f"🐞 Bot de 10 activos INICIADO\n💰 Efectivo: ${EFECTIVO:.2f}\n{obtener_mensaje_animo()}")

# Procesar cada activo
operaciones_realizadas = []

for ticker, cfg in CARTERA.items():
    try:
        precio, rsi = obtener_precio_rsi(ticker)
        
        if precio is None:
            print(f"❌ {ticker}: No se pudo obtener datos, saltando...")
            continue
        
        accion = None
        cantidad = 0
        total = 0
        
        # Señal de COMPRA
        if rsi < cfg["compra_rsi_min"]:
            if EFECTIVO >= cfg["max_compra_usd"]:
                cantidad = cfg["max_compra_usd"] / precio
                total = cfg["max_compra_usd"]
                EFECTIVO -= total
                POSICIONES[ticker] += cantidad
                
                registrar_orden(ticker, "COMPRA", precio, cantidad, rsi, total, EFECTIVO)
                accion = "COMPRA"
                operaciones_realizadas.append(ticker)
                
                mensaje_animo = obtener_mensaje_animo()
                mensaje = f"""🔴 COMPRA SIMULADA: {ticker}

💰 Precio: ${precio:.2f}
📊 RSI: {rsi:.1f}
🔢 Cantidad: {cantidad:.6f}
💵 Efectivo restante: ${EFECTIVO:.2f}

{mensaje_animo}"""
                
                print(f"\n🔴 COMPRA: {ticker} a ${precio:.2f} (RSI {rsi:.1f})")
                print(f"   Cantidad: {cantidad:.6f} | Efectivo restante: ${EFECTIVO:.2f}")
                enviar_telegram(mensaje)
                generar_guion_youtube(ticker, "COMPRA", precio, rsi)
            else:
                print(f"⚠️ {ticker}: Señal COMPRA pero fondos insuficientes (falta ${cfg['max_compra_usd'] - EFECTIVO:.2f})")
        
        # Señal de VENTA
        elif rsi > cfg["venta_rsi_max"] and POSICIONES.get(ticker, 0) > 0:
            cantidad = POSICIONES[ticker]
            total = precio * cantidad
            EFECTIVO += total
            POSICIONES[ticker] = 0
            
            registrar_orden(ticker, "VENTA", precio, cantidad, rsi, total, EFECTIVO)
            accion = "VENTA"
            operaciones_realizadas.append(ticker)
            
            ganancia_perdida = total - (cantidad * cfg.get("precio_compra_promedio", precio))
            mensaje_animo = obtener_mensaje_animo()
            mensaje = f"""🟢 VENTA SIMULADA: {ticker}

💰 Precio: ${precio:.2f}
📊 RSI: {rsi:.1f}
🔢 Cantidad: {cantidad:.6f}
💵 Efectivo actual: ${EFECTIVO:.2f}

{mensaje_animo}"""
            
            print(f"\n🟢 VENTA: {ticker} a ${precio:.2f} (RSI {rsi:.1f})")
            print(f"   Cantidad: {cantidad:.6f} | Nuevo efectivo: ${EFECTIVO:.2f}")
            enviar_telegram(mensaje)
            generar_guion_youtube(ticker, "VENTA", precio, rsi)
        
        # Mostrar estado actual
        estado_icono = "🟢 VENDER" if accion == "VENTA" else ("🔴 COMPRAR" if accion == "COMPRA" else "🟡 ESPERAR")
        posicion_str = f" | 📦 {POSICIONES[ticker]:.4f}u" if POSICIONES[ticker] > 0 else ""
        print(f"{estado_icono} {ticker} - {cfg['nombre']}: ${precio:.2f} | RSI: {rsi:.1f}{posicion_str}")
        
        # Pequeña pausa para no saturar la API
        time.sleep(0.5)
        
    except Exception as e:
        print(f"❌ {ticker}: Error crítico - {e}")
        enviar_telegram(f"⚠️ Error con {ticker}: {str(e)[:100]}")

# Guardar estado final
guardar_estado()

# ========== RESUMEN FINAL ==========
print("\n" + "="*60)
print("📊 RESUMEN DE CARTERA")
print("="*60)

# Calcular valor total
valor_total, valor_posiciones, detalles_posiciones = calcular_valor_total()

print(f"💰 Efectivo disponible: ${EFECTIVO:.2f}")
print(f"💼 Valor en posiciones: ${valor_posiciones:.2f}")
print(f"💎 VALOR TOTAL ESTIMADO: ${valor_total:.2f}")

if detalles_posiciones:
    print("\n📦 Posiciones abiertas:")
    for detalle in detalles_posiciones:
        print(f"   {detalle}")
else:
    print("\n📦 No hay posiciones abiertas (efectivo 100%)")

# Enviar resumen por Telegram
resumen_telegram = f"""📈 RESUMEN DE CARTERA

💰 Efectivo: ${EFECTIVO:.2f}
💼 Posiciones: ${valor_posiciones:.2f}
💎 TOTAL: ${valor_total:.2f}

Operaciones hoy: {len(operaciones_realizadas)}
{obtener_mensaje_animo()}"""

enviar_telegram(resumen_telegram)

print("\n" + "="*60)
print("✅ Simulación completada")
print(f"📊 Operaciones realizadas: {len(operaciones_realizadas)}")
print("="*60)