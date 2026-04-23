# reporte_progreso.py - Genera un reporte de tu progreso en trading

import json
from datetime import datetime

ARCHIVO_HISTORIAL = "historial_automatico.json"

print("=== 📊 REPORTE DE PROGRESO DE TRADING ===\n")

try:
    with open(ARCHIVO_HISTORIAL, 'r') as f:
        datos = json.load(f)
    
    print(f"📁 Analizando historial desde: {ARCHIVO_HISTORIAL}\n")
    
    for activo, registros in datos.items():
        print(f"🔹 {activo}")
        print(f"   Total de revisiones: {len(registros)}")
        
        # Contar señales
        compras = sum(1 for r in registros if "COMPRAR" in r['decision'])
        ventas = sum(1 for r in registros if "VENDER" in r['decision'])
        esperas = sum(1 for r in registros if "ESPERAR" in r['decision'])
        
        print(f"   🔴 Señales de COMPRAR: {compras}")
        print(f"   🟢 Señales de VENDER: {ventas}")
        print(f"   🟡 Señales de ESPERAR: {esperas}")
        
        # RSI mínimo y máximo detectado
        rsis = [r['rsi'] for r in registros]
        print(f"   📊 RSI mínimo: {min(rsis):.1f} | RSI máximo: {max(rsis):.1f}")
        print("")
    
    print("✅ Reporte generado correctamente")
    print("💡 Sugerencia: Copia estos datos a tu hoja de cálculo")
    
except FileNotFoundError:
    print("❌ No se encontró el archivo de historial.")
    print("   Asegúrate de que el bot ya haya corrido al menos una vez.")
except Exception as e:
    print(f"❌ Error: {e}")