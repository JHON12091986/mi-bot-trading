# conexion_etoro.py - Primer script para conectar con eToro

print("=== BOT DE CONEXIÓN CON ETORO ====")
print("Versión 1.0 - Probando librerías")

# Verificar que las librerías están instaladas
try:
    import requests
    print("✅ requests instalado")
except ImportError:
    print("❌ requests NO instalado")

try:
    import pandas as pd
    print("✅ pandas instalado")
except ImportError:
    print("❌ pandas NO instalado")

try:
    import numpy as np
    print("✅ numpy instalado")
except ImportError:
    print("❌ numpy NO instalado")

print("\n🚀 Verificación completada")