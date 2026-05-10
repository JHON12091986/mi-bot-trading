from dotenv import load_dotenv
import os

# Cargar .env con ruta explícita
load_dotenv(dotenv_path="C:\\Users\\jhons\\mi_primer_bot\\.env")

api_key = os.getenv("BINANCE_API_KEY")
secret_key = os.getenv("BINANCE_SECRET_KEY")

print(f"API Key: {api_key[:20]}..." if api_key else "❌ No encontrada")
print(f"Secret Key: {secret_key[:20]}..." if secret_key else "❌ No encontrada")