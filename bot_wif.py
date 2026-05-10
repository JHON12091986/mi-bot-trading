#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BOT WIF - FORZAR COMPRA/VENTA EN TOPES
COMPRA AUTOMÁTICA: RSI < 45
VENTA AUTOMÁTICA: RSI > 68
STOP LOSS: -15% desde precio medio
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
    'MONTO_OPERACION': 20,
    'COOLDOWN_MINUTES': 10,
    'SCAN_INTERVAL': 60,
    'MONITOR_INTERVAL': 300,
    'MAX_RETRIES': 3,
    'SIMBOLO': "WIFUSDT",
    'NOMBRE': "🐕 Dogwifhat",
    'COMPRA_RSI': 45,
    'VENTA_RSI': 68,
    'STOP_LOSS_PCT': 15,
}

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
logger = logging.getLogger(__name__)

client = Client(API_KEY, SECRET_KEY, testnet=False)
logger.info("🚀 BOT WIF (FORZAR COMPRA/VENTA EN TOPES) conectado a Binance REAL")

STATE_FILE = "cartera_wif.json"

def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r') as f:
                data = json.load(f)
                return data.get('cash', 20.0), data.get('position', {})
        except:
            pass
    return 20.0, {}

def save_state(cash, position):
    with open(STATE_FILE, 'w') as f:
        json.dump({'cash': cash, 'position': position}, f, indent=2)

cash, position = load_state()
logger.info(f"💰 Capital: ${cash:.2f} USDT")

def send_telegram(msg):
    if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
        try:
            requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                         json={'chat_id': TELEGRAM_CHAT_ID, 'text': msg}, timeout=5)
        except:
            pass

def get_rsi(symbol):
    try:
        klines = client.get_klines(symbol=symbol, interval=Client.KLINE_INTERVAL_15MINUTE, limit=20)
        closes = [float(v[4]) for v in klines]
        df = pd.DataFrame({'close': closes})
        delta = df['close'].diff()
        gain = delta.clip(lower=0).rolling(14).mean()
        loss = (-delta.clip(upper=0)).rolling(14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return round(rsi.iloc[-1], 2)
    except Exception as e:
        logger.error(f"Error RSI: {e}")
        return 50.0

def get_price(symbol):
    try:
        return float(client.get_symbol_ticker(symbol=symbol)['price'])
    except Exception as e:
        logger.error(f"Error precio: {e}")
        return None

def check_stop_loss(precio_actual, precio_compra):
    if precio_compra == 0:
        return False
    perdida_pct = (precio_compra - precio_actual) / precio_compra * 100
    return perdida_pct >= CONFIG['STOP_LOSS_PCT']

def comprar():
    global cash, position
    if cash < CONFIG['MONTO_OPERACION']:
        logger.warning(f"Saldo insuficiente: ${cash:.2f} (necesitas ${CONFIG['MONTO_OPERACION']})")
        return False
    
    price = get_price(CONFIG['SIMBOLO'])
    if not price:
        return False
    
    try:
        order = client.order_market_buy(symbol=CONFIG['SIMBOLO'], quoteOrderQty=CONFIG['MONTO_OPERACION'])
        qty = float(order['executedQty'])
        if qty > 0:
            if position:
                old_qty = position['qty']
                old_avg = position['avg_price']
                new_qty = old_qty + qty
                new_avg = (old_qty * old_avg + qty * price) / new_qty
                position = {'qty': new_qty, 'avg_price': new_avg}
            else:
                position = {'qty': qty, 'avg_price': price}
            cash -= CONFIG['MONTO_OPERACION']
            save_state(cash, position)
            msg = f"🔴 COMPRA AUTOMÁTICA {CONFIG['NOMBRE']}\n💰 Precio: ${price:.4f}\n📦 Cantidad: {qty:.6f}\n💵 Efectivo restante: ${cash:.2f}"
            logger.info(msg)
            send_telegram(msg)
            return True
    except Exception as e:
        logger.error(f"Error en compra: {e}")
        send_telegram(f"❌ ERROR COMPRA AUTOMÁTICA\n{e}")
    return False

def vender():
    global cash, position
    if not position or position.get('qty', 0) <= 0:
        logger.warning("No hay posición para vender")
        return False
    
    price = get_price(CONFIG['SIMBOLO'])
    if not price:
        return False
    
    try:
        qty_str = f"{position['qty']:.8f}".rstrip('0').rstrip('.')
        order = client.order_market_sell(symbol=CONFIG['SIMBOLO'], quantity=qty_str)
        qty = float(order['executedQty'])
        if qty > 0:
            revenue = qty * price
            cash += revenue
            gain = revenue - CONFIG['MONTO_OPERACION']
            position = {}
            save_state(cash, position)
            msg = f"🟢 VENTA AUTOMÁTICA {CONFIG['NOMBRE']}\n💰 Precio: ${price:.4f}\n📦 Cantidad: {qty:.6f}\n💵 Ganancia: ${gain:.2f}\n💰 Efectivo: ${cash:.2f}"
            logger.info(msg)
            send_telegram(msg)
            return True
    except Exception as e:
        logger.error(f"Error en venta: {e}")
        send_telegram(f"❌ ERROR VENTA AUTOMÁTICA\n{e}")
    return False

def main():
    logger.info("🚀 BOT WIF (FORZAR COMPRA/VENTA) ACTIVADO")
    send_telegram("✅ BOT WIF FORZAR COMPRA/VENTA ACTIVADO\nCOMPRA AUTOMÁTICA: RSI < 45\nVENTA AUTOMÁTICA: RSI > 68")
    
    last_buy_time = 0
    last_monitor_time = 0
    
    while True:
        try:
            price = get_price(CONFIG['SIMBOLO'])
            if not price:
                time.sleep(10)
                continue
            
            rsi = get_rsi(CONFIG['SIMBOLO'])
            in_position = position and position.get('qty', 0) > 0
            total = cash + (position.get('qty', 0) * price if position else 0)
            tiempo_actual = time.time()
            
            # Log en consola (cada 1 minuto)
            logger.info(f"📊 {CONFIG['NOMBRE']} | ${price:.4f} | RSI {rsi:.1f} | Pos: {position.get('qty', 0):.6f} | Total: ${total:.2f}")
            
            # Enviar monitor a Telegram CADA 5 MINUTOS
            if tiempo_actual - last_monitor_time >= CONFIG['MONITOR_INTERVAL']:
                profit_loss = ""
                if in_position and position.get('avg_price', 0) > 0:
                    pnl_pct = (price - position['avg_price']) / position['avg_price'] * 100
                    profit_loss = f"\n📈 PnL: {pnl_pct:+.2f}%"
                
                monitor_msg = (f"📊 *MONITOR WIF (45/68)*\n"
                              f"💰 Precio: ${price:.4f}\n"
                              f"📈 RSI: {rsi:.1f}\n"
                              f"{'🔴 EN POSICIÓN' if in_position else '🟢 SIN POSICIÓN'}{profit_loss}\n"
                              f"💵 Efectivo: ${cash:.2f}\n"
                              f"💼 TOTAL: ${total:.2f}")
                send_telegram(monitor_msg)
                last_monitor_time = tiempo_actual
            
            # STOP LOSS (si hay posición y pérdida > 15%)
            if in_position and check_stop_loss(price, position.get('avg_price', 0)):
                logger.warning(f"⚠️ STOP LOSS ACTIVADO! Pérdida > {CONFIG['STOP_LOSS_PCT']}%")
                vender()
                continue
            
            # 🔴 COMPRA AUTOMÁTICA (RSI < 45 y sin posición)
            if rsi < CONFIG['COMPRA_RSI'] and not in_position and cash >= CONFIG['MONTO_OPERACION']:
                if tiempo_actual - last_buy_time > CONFIG['COOLDOWN_MINUTES'] * 60:
                    logger.info(f"🔴 SEÑAL COMPRA RSI {rsi:.1f} < {CONFIG['COMPRA_RSI']} → EJECUTANDO COMPRA")
                    if comprar():
                        last_buy_time = tiempo_actual
            
            # 🟢 VENTA AUTOMÁTICA (RSI > 68 y con posición)
            elif rsi > CONFIG['VENTA_RSI'] and in_position:
                logger.info(f"🟢 SEÑAL VENTA RSI {rsi:.1f} > {CONFIG['VENTA_RSI']} → EJECUTANDO VENTA")
                vender()
            
            time.sleep(CONFIG['SCAN_INTERVAL'])
            
        except KeyboardInterrupt:
            logger.info("Bot detenido manualmente")
            send_telegram("Bot WIF detenido manualmente")
            break
        except Exception as e:
            logger.error(f"Error general: {e}")
            send_telegram(f"❌ ERROR EN BOT\n{str(e)[:200]}")
            time.sleep(60)

if __name__ == "__main__":
    main()