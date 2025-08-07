import pandas as pd
import statistics as stats

"""

    Regras para o sinal

    neutro   -> comprado, quando  (sma_5 > sma_30 > sma_60)
    neutro   -> vendido,  quando  (sma_5 < sma_30 < sma_60)
    comprado -> neutro,   quando !(sma_5 > sma_30 > sma_60)
    vendido  -> neutro,   quando !(sma_5 < sma_30 < sma_60)

"""

# parameters
list_of_assets = ["01_btc", "02_eth", "03_sol", "04_xrp"]
leverage_list = [0.0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0]
starting_year = 2014
allow_short_futures = False

# output dataframe
df_pnl = pd.DataFrame(leverage_list, columns=["leverage"])
df_price = pd.DataFrame()
df_return = pd.DataFrame()

def calc_pnl(leverage, df):

    initial_price = df["close"].iloc[0]
    liquidated = False
    future_position = "neutral"

    for index, row in df.iterrows():

        if liquidated:
            break

        spot_return = row["close"] / initial_price - 1
        if future_position != "neutral":
            future_return = leverage * spot_return
        else:
            future_return = 0.0
        total_return = spot_return + future_return

        if total_return < -1:
            liquidated = True
            total_return = -1.0

        pnl_spot = 1 + total_return

        buy_signal = row["sma_5"] > row["sma_30"] and row["sma_30"] > row["sma_60"]
        sell_signal = row["sma_5"] < row["sma_30"] and row["sma_30"] < row["sma_60"]
        if not allow_short_futures:
            sell_signal = False

        match future_position:
                case "neutral":
                    if buy_signal:
                        future_position = "long"
                        leverage = abs(leverage)
                    if sell_signal:
                        future_position = "short"
                        leverage = -abs(leverage)
                case _:
                    if not buy_signal and not sell_signal:
                        future_position = "neutral"

    return pnl_spot

print("---------- reading data ----------")
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
    df_price[asset] = df["close"]
    df_return[asset] = df["close"] / df["close"].shift(1) -1

    # add moving averages and remove NAs
    df["sma_5"] = df["close"].rolling(window=5).mean()
    df["sma_30"] = df["close"].rolling(window=30).mean()
    df["sma_60"] = df["close"].rolling(window=60).mean()
    df = df[~df["sma_5"].isna()]
    df = df[~df["sma_30"].isna()]
    df = df[~df["sma_60"].isna()]

    # filter data for the specified year
    df = df[df.index.year >= starting_year]

    # backtest loop
    print(f"calculating pnl for {asset}...")

    simulated_pnl = []

    out_dict = {}
    for leverage in leverage_list:
        print(f"asset = {asset} | leverage = {leverage}")
        pnl_list = []
        for i in range(0, len(df) - 365):
            df_tmp = df[i:i+365]
            pnl_spot = calc_pnl(leverage = leverage, df = df_tmp)
            # print(pnl_spot)
            pnl_list.append(pnl_spot)
        out_dict[asset+"_"+str(leverage)] = pnl_list
        print (f"simulation results...")
        print (f"{stats.mean(pnl_list):.2f}")
        print (f"{stats.stdev(pnl_list):.2f}")

    df_out = pd.DataFrame(out_dict)
    df_out.to_csv("simulation_result.csv", index=False)
