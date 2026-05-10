It will run once, send alerts, and generate logs. To run periodically, set up a cron job (Linux/Mac) or Task Scheduler (Windows).

## Customization
- Edit `WATCHLIST` dictionary to change assets.
- Modify `RULES` to adjust RSI thresholds and trade sizes.
- Set `AUTO_BUY` / `AUTO_SELL` to `False` if you only want alerts.

## Output Files
- `historial_simulado.json` – all buy/sell signals
- `ordenes_simuladas.json` – simulated orders
- `mis_operaciones.csv` – trade log for Excel
- `guiones_youtube.txt` – ready-to-use video scripts
- `resumen_dia.txt` – daily summary

## Disclaimer
This bot is for **educational purposes only**. It simulates trades – never invest real money without proper risk management.

## Author
Agente Digital – Python Automation Specialist