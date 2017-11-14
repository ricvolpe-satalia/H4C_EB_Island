import pandas as pd
import numpy as np

#get the time and price dataframe
df_prices = pd.read_csv('Prices_2017.csv')
df1_prices = df_prices.set_index("Timestamp")
size_prices = df1_prices.shape

#toggle on off, report power at the instant (rules for the smart meter)
#get the time and power dataframe from devices in one file
total_devices = 2
dfs = []
for num in range(total_devices):
    df = pd.read_csv("Power_2017_"+str(num+1)+".csv")
    df = df.ix[:,1:2]
    df.columns = ["Device_"+str(num+1)]
    dfs.append(df)
merged = pd.concat(dfs,axis=1)
merged['timestamp'] = df_prices.iloc[:,0]
merged['prices'] = df_prices.iloc[:,1]
merged.to_csv("Power_2017.csv", encoding='utf-8', index=False)

# get the price and the battery status for all the devices
Power = pd.read_csv("Power_2017.csv")
Power['Prices_1']=Power.Device_1 * Power.prices/1000
Power['Prices_2']=Power.Device_2 * Power.prices/1000
Power['Battery_status_1']=np.random.randint(1,100,Power.shape[0])
Power['Battery_status_2']=np.random.randint(1,100,Power.shape[0])
Power.to_csv("Power_2017.csv", encoding='utf-8', index=False)

#set limit for prices and store energy
price_limit = Power["prices"].mean()

#trade between all the devices
time_per_charge_10_percent = 1 #1 time interval i.e. takes 15 minutes to charge 10%
Trading_energy=[0]*len(Power)
for i in range(size_prices[0]):
    price = Power.get_value(i, "prices")
    #Scenario 1: if the price is less than the price limit
    if price < price_limit:
        # check the one with higher consumption need
        if Power.get_value(i,"Device_1") < Power.get_value(i,"Device_2"):
            # if the higher consumption device has has no storage energy, then charge it
            if Power.get_value(i,"Battery_status_1")<70:
                Power.ix[i,"Battery_status_1"] = 70
            # if the higher consumption device has storage energy, then trade to the other device
            else:
                Trading_energy[i] = 70 - Power.ix[i,"Battery_status_2"]
                Power.ix[i,"Battery_status_2"] = 70
            # if the lower consumption device has storage energy, then end-do nothing
Power['Traded_energy']=Trading_energy
Power.to_csv("Power_2017.csv", encoding='utf-8', index=False)