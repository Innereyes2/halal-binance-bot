import pandas as pd
import ta

def fetch_ohlcv(client, symbol, interval='1h', limit=100):
    klines = client.get_klines(symbol=symbol, interval=interval, limit=limit)
    df = pd.DataFrame(klines, columns=[
        'timestamp', 'open', 'high', 'low', 'close', 'volume',
        'close_time', 'quote_asset_volume', 'num_trades',
        'taker_buy_base_vol', 'taker_buy_quote_vol', 'ignore'
    ])
    df['close'] = df['close'].astype(float)
    df['open'] = df['open'].astype(float)
    df['high'] = df['high'].astype(float)
    df['low'] = df['low'].astype(float)
    df['volume'] = df['volume'].astype(float)
    return df

def generate_signal(df):
    try:
        df['ema_12'] = ta.trend.ema_indicator(df['close'], window=12)
        df['ema_26'] = ta.trend.ema_indicator(df['close'], window=26)
        df['rsi'] = ta.momentum.rsi(df['close'], window=14)

        macd_indicator = ta.trend.MACD(df['close'])
        df['macd'] = macd_indicator.macd()
        df['macd_signal'] = macd_indicator.macd_signal()

        bb = ta.volatility.BollingerBands(df['close'], window=20, window_dev=2)
        df['bb_upper'] = bb.bollinger_hband()
        df['bb_lower'] = bb.bollinger_lband()

        stoch_rsi = ta.momentum.StochRSIIndicator(df['close'])
        df['stoch_k'] = stoch_rsi.stochrsi_k()
        df['stoch_d'] = stoch_rsi.stochrsi_d()

        df['adx'] = ta.trend.adx(df['high'], df['low'], df['close'], window=14)
        df['vol_ma'] = df['volume'].rolling(window=20).mean()

        latest = df.iloc[-1]

        # ✅ RELAXED BUY SIGNAL
        buy = (
            latest['ema_12'] > latest['ema_26'] and
            latest['rsi'] < 60 and
            latest['macd'] > latest['macd_signal'] and
            latest['stoch_k'] < 50 and
            latest['adx'] > 20 and
            latest['volume'] > 0
        )

        # ✅ RELAXED SELL SIGNAL
        sell = (
            latest['ema_12'] < latest['ema_26'] and
            latest['rsi'] > 40 and
            latest['macd'] < latest['macd_signal'] and
            latest['stoch_k'] > 50 and
            latest['adx'] > 20 and
            latest['volume'] > 0
        )

        if buy:
            return "BUY"
        elif sell:
            return "SELL"
        else:
            return "HOLD"

    except Exception as e:
        print(f"⚠️ Indicator error: {e}")
        return "HOLD"
