import yfinance as yf
import pandas as pd

# Ativos e seus tickers no Yahoo Finance
assets = {
    'btc': 'BTC-USD',
    'eth': 'ETH-USD',
    'sol': 'SOL-USD',
    'xrp': 'XRP-USD'
}

# Período
start_date = '2014-01-01'
end_date = None  # até hoje

for symbol, ticker in assets.items():
    print(f"⬇️ Baixando dados de {ticker}...")

    df = yf.download(ticker, start=start_date, end=end_date)
    df.dropna(inplace=True)

    # Renomeia e seleciona colunas
    df = df.rename(columns={
        'Close': 'close',
        'High': 'high',
        'Low': 'low',
        'Open': 'open',
        'Volume': 'volume'
    })

    df['data'] = df.index.date  # extrai apenas a data (não o datetime completo)
    
    # Reorganiza colunas
    df = df[['data', 'close', 'high', 'low', 'open', 'volume']]

    # Garante os tipos corretos
    df['data'] = df['data'].astype(str)  # 'yyyy-mm-dd' como string
    df[['close', 'high', 'low', 'open', 'volume']] = df[['close', 'high', 'low', 'open', 'volume']].astype(float)

    # Salva em CSV
    filename = f"{symbol}_historical_data.csv"
    df.to_csv(filename, index=False)
    print(f"✅ Dados salvos em: {filename}")
