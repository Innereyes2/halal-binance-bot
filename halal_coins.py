# halal_coins.py

def get_halal_symbols(binance_client, base_pair="USDT"):
    static_halal_assets = [
        "BTC", "ETH", "BNB", "SOL", "AVAX", "ADA", "MATIC", "DOT", "ATOM", "NEAR",
        "XLM", "LINK", "FIL", "ICP", "OP", "ARB", "ALGO", "VET", "GRT", "RNDR"
    ]
    try:
        exchange_info = binance_client.get_exchange_info()
        symbols = [
            s['symbol'] for s in exchange_info['symbols']
            if s['symbol'].endswith(base_pair)
            and s['status'] == "TRADING"
            and s['baseAsset'] in static_halal_assets
        ]
        return symbols
    except Exception as e:
        print("⚠️ Could not fetch halal symbols:", e)
        return []
