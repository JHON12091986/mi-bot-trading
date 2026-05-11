from datetime import datetime, timedelta
from coinpaprika.client import Client

def calcular_rsi(precios, periodo=14):
    """Calcula RSI a partir de lista de precios"""
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
    
    ganancia_prom = sum(ganancias[-periodo:]) / periodo
    perdida_prom = sum(perdidas[-periodo:]) / periodo
    
    if perdida_prom == 0:
        return 100.0
    
    rs = ganancia_prom / perdida_prom
    return round(100 - (100 / (1 + rs)), 1)

def obtener_rsi_wif():
    """Obtiene RSI de WIF usando CoinPaprika SDK oficial"""
    try:
        # Inicializar el cliente (plan gratuito, sin API key)
        client = Client()
        print("✅ Cliente CoinPaprika inicializado")
        
        # El ID correcto de WIF
        coin_id = "wif-dogwifhat"
        
        # Obtener OHLCV histórico (según documentación oficial)[citation:6]
        # Nota: Según la documentación, para datos históricos se recomienda usar API key[citation:6]
        # Pero probamos primero sin key
        historical_data = client.candle(coin_id)
        
        if not historical_data:
            print("❌ No se recibieron datos")
            return None, None
        
        # Extraer precios de cierre
        precios = [float(candle['close']) for candle in historical_data]
        
        # Calcular RSI
        rsi = calcular_rsi(precios)
        
        # Obtener precio actual (Binance)
        import requests
        url_price = "https://api.binance.com/api/v3/ticker/price?symbol=WIFUSDT"
        precio_actual = float(requests.get(url_price, timeout=10).json()['price'])
        
        return rsi, precio_actual
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None, None

if __name__ == "__main__":
    print("🔄 Obteniendo RSI de WIF...")
    rsi, precio = obtener_rsi_wif()
    
    if rsi:
        print(f"\n✅ ¡ÉXITO!")
        print(f"💰 Precio: ${precio:.4f}")
        print(f"📊 RSI: {rsi:.1f}")
        
        if rsi <= 30:
            print("🟢 RECOMENDACIÓN: ¡COMPRA!")
        elif rsi >= 70:
            print("🔴 RECOMENDACIÓN: ¡VENDE!")
        else:
            print("⚪ NEUTRAL: Esperar")
    else:
        print("\n❌ No se pudo obtener el RSI")