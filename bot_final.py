# bot_final.py - Bot de trading con 10 activos y alertas por correo

import requests
import time
import json
import os
import smtplib
from email.mime.text import MIMEText
from datetime import datetime

# ==================== CONFIGURACIÓN ====================
CARTERA = ["NVDA", "AVGO", "MU", "ANET", "MRVL", "MSFT", "AMZN", "LLY", "V", "META"]
INTERVALO_MINUTOS = 15
RSI_COMPRA = 30
RSI_VENTA = 70
ARCHIVO_HISTORIAL = "historial_automatico.json"

# ==================== CONFIGURACIÓN DE CORREO ====================
# 🔴 CAMBIA ESTAS 3 LÍNEAS CON TUS DATOS 🔴
CORREO_ORIGEN = "jhon.larosa.30@gmail.com"
CORREO_DESTINO = "jhon.larosa.30@gmail.com"
CONTRASENA_CORREO = "ymeg etnb wzzu udzy"  # ← PON LA CONTRASEÑA DE 16 LETRAS

# ==================== FUNCIONES ====================

def calcular_rsi(precios, periodo=14):
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

def guardar_historial(ticker, precio, rsi, decision):
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
        "decision": decision
    })
    historial[ticker] = historial[ticker][-100:]
    with open(ARCHIVO_HISTORIAL, 'w') as f:
        json.dump(historial, f, indent=2)

def enviar_alerta(ticker, precio, rsi, decision):
    try:
        msg = MIMEText(f"""
⚠️ ALERTA DE TRADING ⚠️

Activo: {ticker}
Precio: ${precio:.2f}
RSI: {rsi:.1f}
Decisión: {decision}

Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

👉 Ve a eToro y ejecuta la orden manualmente.
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
        print(f"  ❌ Error email: {e}")
        return False

# ==================== BUCLE PRINCIPAL ====================

print("=== 🤖 BOT FINAL - 10 ACTIVOS ===")
print(f"📋 Monitoreando: {', '.join(CARTERA)}")
print(f"⏱️  Intervalo: cada {INTERVALO_MINUTOS} minutos")
print(f"📧 Alertas a: {CORREO_DESTINO}")
print("=" * 60)
print("🟢 Bot iniciado. Presiona Ctrl+C para detener.")
print("")

contador = 0
alertas_enviadas = {}

try:
    while True:
        contador += 1
        print(f"\n📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🔄 Ciclo #{contador}")
        print("-" * 60)
        
        oportunidades = []
        
        for ticker in CARTERA:
            try:
                precio, rsi = obtener_precio_rsi(ticker)
                
                if rsi < RSI_COMPRA:
                    decision = "🔴 COMPRAR"
                    oportunidades.append(f"{ticker} (RSI: {rsi:.1f})")
                    if alertas_enviadas.get(ticker) != "COMPRAR":
                        enviar_alerta(ticker, precio, rsi, "COMPRAR")
                        alertas_enviadas[ticker] = "COMPRAR"
                elif rsi > RSI_VENTA:
                    decision = "🟢 VENDER"
                    oportunidades.append(f"{ticker} (RSI: {rsi:.1f})")
                    if alertas_enviadas.get(ticker) != "VENDER":
                        enviar_alerta(ticker, precio, rsi, "VENDER")
                        alertas_enviadas[ticker] = "VENDER"
                else:
                    decision = "🟡 ESPERAR"
                    if ticker in alertas_enviadas:
                        del alertas_enviadas[ticker]
                
                guardar_historial(ticker, precio, rsi, decision)
                print(f"{decision} {ticker}: ${precio:.2f} | RSI: {rsi:.1f}")
                
            except Exception as e:
                print(f"❌ {ticker}: Error - {e}")
        
        print("-" * 60)
        if oportunidades:
            print(f"🎯 OPORTUNIDADES: {', '.join(oportunidades)}")
        else:
            print("⏳ No hay oportunidades")
        
        print(f"💤 Próxima revisión en {INTERVALO_MINUTOS} minutos...")
        time.sleep(INTERVALO_MINUTOS * 60)
        
except KeyboardInterrupt:
    print("\n🛑 Bot detenido por el usuario")
    print(f"📁 Historial guardado en {ARCHIVO_HISTORIAL}")