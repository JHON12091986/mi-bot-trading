#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BOT DOGE y WIF - RSI 35/70 CON MONITOREO EN TELEGRAM
"""

import os
import json
import time
import logging
import requests
from dotenv import load_dotenv
from binance.client import Client
import pandas as pd

load_dotenv('.env_real')

API_KEY = os.getenv("BINANCE_API_KEY")
SECRET_KEY = os.getenv("BINANCE_SECRET_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

CONFIG = {
    'MONTO_OPERACION': 10,
    'COOLDOWN_MINUTES': 15,
    'SCAN_INTERVAL': 300,   # 5 minutos
    'MAX_RETRIES': 3,
    'ACTIVOS': {
        "DOGEUSDT": {"nombre": "🐕 Dogecoin", "compra_rsi": 35, "venta_rsi": 70},
        "WIFUSDT": {"nombre": "🧢 Dogwifhat", "compra_rsi": 35, "venta_rsi": 70}
    }
}

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
logger = logging.getLogger(__name__)

client = Client(API_KEY, SECRET_KEY, testnet=False)
logger.info("🚀 BOT DOGE/WIF RSI 35/70 conectado")

STATE_FILE = "cartera_doge_wif.json"

def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r') as f:
                data = json.load(f)
                return data.get('cash', 10.0), data.get('positions', {})
        except:
            pass
    return 10.0, {}

def save_state(cash, positions):
    with open(STATE_FILE, 'w') as f:
        json.dump({'cash': cash, 'positions': positions}, f, indent=2)

cash, positions = load_state()
logger.info(f"💰 Capital: {cash:.2f} USDT")

def send_telegram(msg):
    if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
        try:
            requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                         json={'chat_id': TELEGRAM_CHAT_ID, 'text': msg}, timeout=3)
            logger.info("Mensaje enviado a Telegram")
        except Exception as e:
            logger.error(f"Error enviando a Telegram: {e}")

def get_rsi(symbol):
    try:
        klines = client.get_klines(symbol=symbol, interval=Client.KLINE_INTERVAL_15MINUTE, limit=15)
        closes = [float(v[4]) for v in klines]
        df = pd.DataFrame({'close': closes})
        delta = df['close'].diff()
        gain = delta.clip(lower=0).rolling(14).mean()
        loss = (-delta.clip(upper=0)).rolling(14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return round(rsi.iloc[-1], 2)
    except Exception as e:
        logger.error(f"Error calculando RSI: {e}")
        return 50.0

def get_price(symbol):
    try:
        return float(client.get_symbol_ticker(symbol=symbol)['price'])
    except:
        return None

def get_total_balance():
    """Obtiene el saldo total de la cuenta en USDT (efectivo + valor de posiciones)"""
    try:
        # Saldo USDT
        account = client.get_account()
        usdt_balance = 0
        for balance in account['balances']:
            if balance['asset'] == 'USDT':
                usdt_balance = float(balance['free']) + float(balance['locked'])
                break
        
        # Valor de las posiciones
        pos_value = 0
        for symbol, pos in positions.items():
            price = get_price(symbol)
            if price:
                pos_value += pos['qty'] * price
        
        total = usdt_balance + pos_value
        return usdt_balance, pos_value, total
    except Exception as e:
        logger.error(f"Error obteniendo balance: {e}")
        return 0, 0, 0

def comprar(symbol, cfg):
    global cash
    if cash < CONFIG['MONTO_OPERACION']:
        return False
    price = get_price(symbol)
    if not price:
        return False
    try:
        order = client.order_market_buy(symbol=symbol, quoteOrderQty=CONFIG['MONTO_OPERACION'])
        qty = float(order['executedQty'])
        if qty > 0:
            if symbol in positions:
                old = positions[symbol]
                new_qty = old['qty'] + qty
                new_avg = (old['qty'] * old['avg_price'] + qty * price) / new_qty
                positions[symbol] = {'qty': new_qty, 'avg_price': new_avg}
            else:
                positions[symbol] = {'qty': qty, 'avg_price': price}
            cash -= CONFIG['MONTO_OPERACION']
            save_state(cash, positions)
            usdt, pos_val, total = get_total_balance()
            msg = (f"🔴 **COMPRA {cfg['nombre']}**\n"
                   f"📊 RSI: {cfg['compra_rsi']}\n"
                   f"💰 Precio: ${price:.6f}\n"
                   f"📦 Cantidad: {qty:.4f}\n"
                   f"💵 Efectivo bot: ${cash:.2f}\n"
                   f"💰 **SALDO TOTAL BINANCE: ${total:.2f} USDT**")
            logger.info(msg)
            send_telegram(msg)
            return True
    except Exception as e:
        logger.error(f"Error compra: {e}")
    return False

def vender(symbol, cfg):
    global cash
    pos = positions.get(symbol)
    if not pos or pos['qty'] <= 0:
        return False
    price = get_price(symbol)
    if not price:
        return False
    try:
        qty_str = f"{pos['qty']:.8f}".rstrip('0').rstrip('.')
        order = client.order_market_sell(symbol=symbol, quantity=qty_str)
        qty = float(order['executedQty'])
        if qty > 0:
            revenue = qty * price
            cash += revenue
            del positions[symbol]
            save_state(cash, positions)
            usdt, pos_val, total = get_total_balance()
            msg = (f"🟢 **VENTA {cfg['nombre']}**\n"
                   f"📊 RSI: {cfg['venta_rsi']}\n"
                   f"💰 Precio: ${price:.6f}\n"
                   f"📦 Cantidad: {qty:.4f}\n"
                   f"💵 Ingreso: ${revenue:.2f}\n"
                   f"💰 **SALDO TOTAL BINANCE: ${total:.2f} USDT**")
            logger.info(msg)
            send_telegram(msg)
            return True
    except Exception as e:
        logger.error(f"Error venta: {e}")
    return False

def main():
    logger.info("🚀 BOT DOGE/WIF ACTIVADO - RSI COMPRA 35 | VENTA 70")
    send_telegram("🤖 **BOT DOGE/WIF ACTIVADO**\nRSI Compra: 35 | RSI Venta: 70")
    ultima_compra = {s: 0 for s in CONFIG['ACTIVOS']}
    
    while True:
        try:
            # Variables para el mensaje de monitoreo
            monitor_msg = "📊 **MONITOREO BOT DOGE/WIF**\n\n"
            total_cash = cash
            
            for simbolo, cfg in CONFIG['ACTIVOS'].items():
                precio = get_price(simbolo)
                if not precio:
                    continue
                rsi = get_rsi(simbolo)
                en_posicion = simbolo in positions
                
                # Actualizar total
                if simbolo in positions:
                    total_cash += positions[simbolo]['qty'] * precio
                
                # Estado de señal
                if rsi <= cfg['compra_rsi']:
                    senal = "🔴 **SEÑAL COMPRA** (RSI BAJO)"
                elif rsi >= cfg['venta_rsi']:
                    senal = "🟢 **SEÑAL VENTA** (RSI ALTO)"
                else:
                    senal = "🟡 NEUTRAL (ESPERAR)"
                
                monitor_msg += (f"{cfg['nombre']}\n"
                               f"💰 Precio: ${precio:.6f}\n"
                               f"📈 RSI: {rsi:.1f}\n"
                               f"🎯 Señal: {senal}\n"
                               f"📦 Posición: {positions.get(simbolo, {}).get('qty', 0):.6f}\n\n")
                
                # Log en consola
                logger.info(f"📊 {cfg['nombre']} | ${precio:.8f} | RSI: {rsi:.1f} | Posición: {positions.get(simbolo, {}).get('qty', 0):.6f}")
                
                # Lógica de trading
                if rsi <= cfg['compra_rsi'] and cash >= CONFIG['MONTO_OPERACION']:
                    if time.time() - ultima_compra.get(simbolo, 0) > CONFIG['COOLDOWN_MINUTES'] * 60:
                        if comprar(simbolo, cfg):
                            ultima_compra[simbolo] = time.time()
                elif rsi >= cfg['venta_rsi'] and en_posicion:
                    vender(simbolo, cfg)
            
            # Obtener saldo real de Binance
            usdt_real, pos_val_real, total_real = get_total_balance()
            
            monitor_msg += (f"💰 **SALDO EN BINANCE**\n"
                           f"💵 USDT disponible: ${usdt_real:.2f}\n"
                           f"📦 Valor en posiciones: ${pos_val_real:.2f}\n"
                           f"💎 **TOTAL: ${total_real:.2f} USDT**")
            
            # Enviar monitoreo a Telegram
            send_telegram(monitor_msg)
            
            # Resumen en consola
            logger.info(f"💰 EFECTIVO BOT: ${cash:.2f} | TOTAL BINANCE: ${total_real:.2f} | POSICIONES: {len(positions)}")
            
            time.sleep(CONFIG['SCAN_INTERVAL'])
            
        except KeyboardInterrupt:
            logger.info("Bot detenido manualmente")
            send_telegram("🛑 Bot DOGE/WIF detenido manualmente")
            break
        except Exception as e:
            logger.error(f"Error general: {e}")
            time.sleep(60)

if __name__ == "__main__":
    main()