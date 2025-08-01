import pandas as pd

# parameters
leverage = 2.0
starting_year = 2018

# read data and make necessary adjustments
df = pd.read_csv("01_btc_historical_data.csv")
df["data"] = pd.to_datetime(df["data"], format="%Y-%m-%d")
df.set_index("data", inplace=True)

# drop NaN indexed lines
df = df[~df.index.isna()]

# filter data for the specified year
df = df[df.index.year >= starting_year]

# makes sure prices are float (not str)
df["close"] = df["close"].astype(float)

# set initial backtest conditions
initial_price = df["close"].iloc[0]
cripto_return = 1.0
future_return = 1.0

for index, row in df.iterrows():
    cripto_return = row["close"] / initial_price - 1
    future_return = leverage * cripto_return
    total_return = cripto_return + future_return
    print(f"return for {index} = {cripto_return} | future return = {future_return} | total return = {total_return}")
