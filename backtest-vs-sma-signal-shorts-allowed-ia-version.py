import pandas as pd
import os

# Parameters
list_of_assets = ["01_btc", "02_eth", "03_sol", "04_xrp"]
leverage_list = [0.0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0]
starting_year = 2014

# Output DataFrames
df_pnl = pd.DataFrame(leverage_list, columns=["leverage"])
df_price = pd.DataFrame()
df_return = pd.DataFrame()

print("---------- reading data ----------")

# Read and process data
for asset in list_of_assets:
    print(f"reading data for {asset}...")
    file_name = f"{asset}_historical_data.csv"
    
    if not os.path.isfile(file_name):
        print(f"File {file_name} not found.")
        continue

    df = pd.read_csv(file_name)
    df["data"] = pd.to_datetime(df["data"], format="%Y-%m-%d")
    df.set_index("data", inplace=True)
    df = df[~df.index.isna()]
    df["close"] = df["close"].astype(float)
    df_price[asset] = df["close"]
    df_return[asset] = df["close"].pct_change()

    # Calculate moving averages
    df["sma_5"] = df["close"].rolling(window=5).mean()
    df["sma_30"] = df["close"].rolling(window=30).mean()
    df["sma_60"] = df["close"].rolling(window=60).mean()
    df.dropna(inplace=True)
    df = df[df.index.year >= starting_year]

    print(f"calculating pnl for {asset}...")

    simulated_pnl = []

    for leverage in leverage_list:
        # Start with initial capital of 1.0
        total_return = 0.0
        future_position = "neutral"
        signed_leverage = 0.0
        liquidated = False

        for i in range(1, len(df)):
            if liquidated:
                break

            row = df.iloc[i]
            row_prev = df.iloc[i - 1]

            # Signal based on yesterday's moving averages
            buy_signal = row_prev["sma_5"] > row_prev["sma_30"] > row_prev["sma_60"]
            sell_signal = row_prev["sma_5"] < row_prev["sma_30"] < row_prev["sma_60"]

            # Update future position based on signal
            if future_position == "neutral":
                if buy_signal:
                    future_position = "long"
                    signed_leverage = leverage
                elif sell_signal:
                    future_position = "short"
                    signed_leverage = -leverage
            else:
                if not buy_signal and not sell_signal:
                    future_position = "neutral"
                    signed_leverage = 0.0

            # Compute spot return
            spot_return = row["close"] / df["close"].iloc[0] - 1.0

            # Apply leverage only when in long or short position
            future_return = signed_leverage * spot_return

            # Total return is spot + futures (long or short)
            total_return = 1 + spot_return + future_return

            if total_return <= -1:
                total_return = 0.0
                liquidated = True

        simulated_pnl.append(total_return)

    df_pnl[asset] = simulated_pnl

# Final outputs
print("---------- simulation results ----------")
print(f"starting at {starting_year}")
print("----------   pnl simulation   ----------")
df_pnl.set_index("leverage", inplace=True)
print(df_pnl)

print("----------  pnl correlation  ----------")
print(df_pnl.corr())
print("---------- price correlation ----------")
print(df_price.corr())
print("---------- return correlation ---------")
print(df_return.corr())
