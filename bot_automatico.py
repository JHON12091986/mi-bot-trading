# bot_automatico.py - Bot que se ejecuta solo y te avisa por email

import requests
import time
import smtplib
import json
import os
from email.mime.text import MimeText
from datetime import datetime

# ==================== CONFIGURACIÓN ====================
CARTERA = ["NVDA", "AVGO", "MU", "ANET", "MRVL"]
INTERVALO_MINUTOS = 60  # Cada 60 minutos revisa
RSI_COMPRA = 30
RSI_VENTA = 70

# CONFIGURACIÓN DE CORREO (cámbialo por el tuyo)
CORREO_ORIGEN = "tu_correo@gmail.com"
CORREO_DESTINO = "tu_correo@gmail.com"
CONTRASENA_CORREO = "tu_contraseña_de_aplicacion"  # Ver nota abajo

ARCHIVO_HISTORIAL = "historial_automatico.json"

# ==================== FUNCIONES ====================

def calcular_rsi(precios, periodo=14):
    """Calcula el RSI"""
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
    
    ganancia_promedio = sum(ganancias[-periodo:]) / periodo
    perdida_promedio = sum(perdidas[-periodo:]) / periodo
    
    if perdida_promedio == 0:
        return 100
    
    rs = ganancia_promedio / perdida_promedio
    rsi = 100 - (100 / (1 + rs))
    return rsi

def obtener_precio_rsi(ticker):
    """Obtiene precio y RSI para un ticker"""
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    respuesta = requests.get(url, headers=headers, timeout=10)
    datos = respuesta.json()
    
    precio = datos['chart']['result'][0]['meta']['regularMarketPrice']
    
    precios = []
    for candle in datos['chart']['result'][0]['indicators']['quote'][0]['close']:
        if candle is not None:
            precios.append(candle)
    
    rsi = calcular_rsi(precios, 14)
    
    return precio, rsi

def enviar_alerta(ticker, precio, rsi, decision):
    """Envía un correo de alerta"""
    try:
        msg = MimeText(f"""
        ⚠️ ALERTA DE TRADING ⚠️
        
        Activo: {ticker}
        Precio: ${precio:.2f}
        RSI: {rsi:.1f}
        Decisión: {decision}
        
        Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        
        Ve a eToro y ejecuta la orden manualmente.
        """)
        
        msg['Subject'] = f"🔔 ALERTA BOT: {ticker} - {decision}"
        msg['From'] = CORREO_ORIGEN
        msg['To'] = CORREO_DESTINO
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(CORREO_ORIGEN, CONTRASENA_CORREO)
        server.send_message(msg)
        server.quit()
        
        print(f"  📧 Alerta enviada a {CORREO_DESTINO}")
        return True
    except Exception as e:
        print(f"  ❌ Error al enviar email: {e}")
        return False

def guardar_historial(ticker, precio, rsi, decision, alerta_enviada):
    """Guarda el historial en JSON"""
    historial = {}
    if os.path.exists(ARCHIVO_HISTORIAL):
        with open(ARCHIVO_HISTORIAL, 'r') as f:
            historial = json.load(f)
    
    if ticker not in historial:
        historial[ticker] = []
    
    historial[ticker].append({
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "precio": round(precio, 2),
        "rsi": round(rsi, 1),
        "decision": decision,
        "alerta_enviada": alerta_enviada
    })
    
    historial[ticker] = historial[ticker][-50:]  # Guardar últimos 50
    
    with open(ARCHIVO_HISTORIAL, 'w') as f:
        json.dump(historial, f, indent=2)

def cargar_ultima_alerta(ticker):
    """Carga si ya se envió alerta para evitar spam"""
    if not os.path.exists(ARCHIVO_HISTORIAL):
        return False
    
    with open(ARCHIVO_HISTORIAL, 'r') as f:
        historial = json.load(f)
    
    if ticker not in historial or len(historial[ticker]) == 0:
        return False
    
    ultimo = historial[ticker][-1]
    return ultimo.get("alerta_enviada", False)

# ==================== BUCLE PRINCIPAL ====================

print("=== 🤖 BOT AUTOMÁTICO DE TRADING ===")
print(f"📋 Monitoreando: {', '.join(CARTERA)}")
print(f"⏱️  Intervalo: cada {INTERVALO_MINUTOS} minutos")
print(f"📧 Alertas a: {CORREO_DESTINO}")
print("=" * 50)
print("🟢 Bot iniciado. Presiona Ctrl+C para detener.")
print("")

try:
    while True:
        print(f"\n📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("-" * 40)
        
        for ticker in CARTERA:
            try:
                precio, rsi = obtener_precio_rsi(ticker)
                
                # Decisión
                if rsi < RSI_COMPRA:
                    decision = "COMPRAR"
                elif rsi > RSI_VENTA:
                    decision = "VENDER"
                else:
                    decision = "ESPERAR"
                
                # Verificar si ya se envió alerta
                alerta_ya_enviada = cargar_ultima_alerta(ticker)
                
                # Enviar alerta solo si es COMPRA o VENTA y no se envió antes
                alerta_enviada = False
                if decision in ["COMPRAR", "VENDER"] and not alerta_ya_enviada:
                    alerta_enviada = enviar_alerta(ticker, precio, rsi, decision)
                
                # Guardar historial
                guardar_historial(ticker, precio, rsi, decision, alerta_enviada)
                
                # Mostrar en pantalla
                if decision == "COMPRAR":
                    print(f"🔴 {ticker}: ${precio:.2f} | RSI: {rsi:.1f} | {decision}")
                elif decision == "VENDER":
                    print(f"🟢 {ticker}: ${precio:.2f} | RSI: {rsi:.1f} | {decision}")
                else:
                    print(f"🟡 {ticker}: ${precio:.2f} | RSI: {rsi:.1f} | {decision}")
                
            except Exception as e:
                print(f"❌ {ticker}: Error - {e}")
        
        print("-" * 40)
        print(f"💤 Próxima revisión en {INTERVALO_MINUTOS} minutos...")
        time.sleep(INTERVALO_MINUTOS * 60)
        
except KeyboardInterrupt:
    print("\n🛑 Bot detenido por el usuario")