import os
import time
from dotenv import load_dotenv
from binance.client import Client
from supabase import create_client
from utils.whatsapp import send_whatsapp
from halal_coins import get_halal_symbols
from strategies.ema_rsi import fetch_ohlcv, generate_signal

load_dotenv()

supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
client = Client(os.getenv("BINANCE_API_KEY"), os.getenv("BINANCE_API_SECRET"), testnet=False)

CAPITAL_FILE = "capital_tracker.txt"
BUY_LOG_FILE = "last_buy_prices.txt"
DEFAULT_CAPITAL = 100.00
MAX_TRADES = 5

def get_dashboard_status():
    try:
        status = supabase.table("status").select("*").eq("id", 1).execute()
        return status.data[0]["running"]
    except:
        return False

def load_capital():
    try:
        with open(CAPITAL_FILE, "r") as f:
            return float(f.read().strip())
    except:
        return DEFAULT_CAPITAL

def save_capital(amount):
    with open(CAPITAL_FILE, "w") as f:
        f.write(f"{amount:.2f}")

def load_buy_log():
    data = {}
    if os.path.exists(BUY_LOG_FILE):
        with open(BUY_LOG_FILE, "r") as f:
            for line in f:
                symbol, price = line.strip().split(",")
                data[symbol] = float(price)
    return data

def save_buy_log(buy_log):
    with open(BUY_LOG_FILE, "w") as f:
        for symbol, price in buy_log.items():
            f.write(f"{symbol},{price}\n")

def run_trading_cycle():
    capital = load_capital()
    buy_log = load_buy_log()
    symbols_to_trade = get_halal_symbols(client)
    scanned, trades_made = 0, 0
    trade_candidates = []

    for symbol in symbols_to_trade:
        scanned += 1
        try:
            df = fetch_ohlcv(client, symbol)
            signal = generate_signal(df)
            price = df['close'].iloc[-1]
            tp = price * 1.003  # +0.3%
            sl = price * 0.997  # -0.3%

            if signal == "BUY" and symbol not in buy_log:
                trade_candidates.append({
                    "symbol": symbol,
                    "price": price,
                    "tp": tp,
                    "sl": sl
                })
        except Exception as e:
            print(f"⚠️ Error processing {symbol}: {e}")
            continue

    top_trades = trade_candidates[:MAX_TRADES]
    total_weight = len(top_trades)
    for trade in top_trades:
        allocated = capital / total_weight
        qty = round(allocated / trade['price'], 6)
        buy_log[trade['symbol']] = trade['price']
        save_buy_log(buy_log)

        msg = f"📥 BUY {trade['symbol']}\nPrice: {trade['price']}\nQty: {qty}\nTP: {trade['tp']:.4f}\nSL: {trade['sl']:.4f}"
        supabase.table("trades").insert({
            "symbol": trade['symbol'],
            "side": "BUY",
            "price": trade['price'],
            "quantity": qty,
            "profit": None
        }).execute()
        send_whatsapp(msg)
        print("✅ Buy executed:", msg)
        trades_made += 1

    for symbol in list(buy_log.keys()):
        try:
            df = fetch_ohlcv(client, symbol)
            current = df['close'].iloc[-1]
            old = buy_log[symbol]
            qty = round(capital / old, 6)
            tp = old * 1.003
            sl = old * 0.997
            signal = generate_signal(df)

            if current >= tp or current <= sl or signal == "SELL":
                profit = round((current - old) * qty, 4)
                capital += profit
                save_capital(capital)
                del buy_log[symbol]
                save_buy_log(buy_log)

                status = "🎯 TP HIT" if current >= tp else ("🛑 SL HIT" if current <= sl else "📉 SELL SIGNAL")
                msg = f"📤 {status} {symbol}\nExit: {current}\nQty: {qty}\n💰 Profit: {profit} USDT\n📈 Capital: {capital:.2f}"
                supabase.table("trades").insert({
                    "symbol": symbol,
                    "side": "SELL",
                    "price": current,
                    "quantity": qty,
                    "profit": profit
                }).execute()
                send_whatsapp(msg)
                print("✅ Sell executed:", msg)
                trades_made += 1
        except Exception as e:
            print(f"⚠️ Error selling {symbol}: {e}")
            continue

    if trades_made == 0:
        print(f"🔍 Scanned {scanned} coins. No trade signal at {time.strftime('%Y-%m-%d %H:%M:%S')}. HOLD.")

def run_with_dashboard_check():
    print("🤖 Bot waiting for dashboard signal... (every 1 min)")
    while True:
        if get_dashboard_status():
            print("▶️ Dashboard says RUN — starting trading cycle...")
            run_trading_cycle()
        else:
            print("⏸ Dashboard says STOP — skipping trading cycle.")
        time.sleep(60)

if __name__ == "__main__":
    run_with_dashboard_check()
