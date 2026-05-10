import os
from dotenv import load_dotenv
from binance.client import Client

# Cargar las claves desde el archivo .env
load_dotenv()

API_KEY = os.getenv("BINANCE_API_KEY")
SECRET_KEY = os.getenv("BINANCE_SECRET_KEY")

# Verificar que las claves se cargaron bien
if not API_KEY or not SECRET_KEY:
    print("❌ Error: No se encontraron las claves en el archivo .env")
    print("   Asegúrate de que el archivo .env contiene:")
    print("   BINANCE_API_KEY=tu_clave_api")
    print("   BINANCE_SECRET_KEY=tu_clave_secreta")
    exit()

# Conectar al simulador de Binance (Demo Trading)
client = Client(API_KEY, SECRET_KEY, demo=True)

# Probar la conexión obteniendo la información de la cuenta demo
try:
    cuenta = client.get_account()
    print("✅ Conexión exitosa al Demo Trading de Binance")
    print(f"   Saldo de USDT (virtual):")
    for balance in cuenta['balances']:
        if float(balance['free']) > 0 or float(balance['locked']) > 0:
            print(f"   - {balance['asset']}: free={balance['free']}, locked={balance['locked']}")
except Exception as e:
    print(f"❌ Error al conectar: {e}")
    print("   Verifica que las claves sean correctas y que estés en la Demo.")