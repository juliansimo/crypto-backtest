import pandas as pd

# parameters
list_of_assets = ["01_btc", "02_eth", "03_sol", "04_xrp"]
leverage_list = [0.0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0]
starting_year = 2020

# output dataframe
df_ans = pd.DataFrame(leverage_list, columns=["leverage"])

# read data
for asset in list_of_assets:

    # read the CSV file for each asset
    print(f"reading data for {asset}...")
    df = pd.read_csv(f"{asset}_historical_data.csv")

    # convert 'data' column to datetime and set it as index
    df["data"] = pd.to_datetime(df["data"], format="%Y-%m-%d")
    df.set_index("data", inplace=True)

    # drop NaN indexed lines and ensure 'close' is float
    df = df[~df.index.isna()] 
    df["close"] = df["close"].astype(float)

    # filter data for the specified year
    df = df[df.index.year >= starting_year]

    # backtest loop
    simulated_pnl = []
    for leverage in leverage_list:
        initial_price = df["close"].iloc[0]
        cripto_return = 0.0
        future_return = 0.0
        total_return = 0.0
        pnl = 0.0
        liquidated = False
        for index, row in df.iterrows():
            if not liquidated:
                cripto_return = row["close"] / initial_price - 1
                future_return = leverage * cripto_return
                total_return = cripto_return + future_return
                if total_return < -1:
                    liquidated = True
                    total_return = -1.0
                pnl = 1 + total_return
        simulated_pnl.append(float(pnl))
        # print(f"{index:%Y-%m-%d}: leverage = {leverage:.2f} | PnL = {pnl:.2f}")
    df_ans[asset] = simulated_pnl

df_ans.set_index("leverage", inplace=True)
print(df_ans)
