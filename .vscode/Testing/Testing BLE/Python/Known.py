from bleak import BleakClient
import asyncio
from datetime import datetime


ADDRESS    = "28:cd:c1:0b:73:64"
#GYRO_UUID  = "ed01c340-ff5f-41e2-8779-70fa0a22f891"
ACCEL_UUID = "ed01c340-ff5f-41e2-8779-70fa0a22f892"
GYRO_UUID = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"

# Create a handler for gyroscope notifications.
global gyro_byte_buffer; gyro_byte_buffer = []
def gyro_handler(characteristic, data):
    current_timestamp_entry = datetime.now()
    list_entry = (data) #str(current_timestamp_entry) + "; " + data.hex())
    gyro_byte_buffer.append(list_entry)
       
# Create a handler for accelerometer notifications.
global accel_byte_buffer; accel_byte_buffer = []
def accel_handler(characteristic, data):
    current_timestamp_entry = datetime.now()
    list_entry = (data) # (str(current_timestamp_entry) + "; " + data.hex())
    accel_byte_buffer.append(list_entry)
    
# Connect to the Arduino and start reading data.
async def collect_data(address, gyro_uuid, accel_uuid):
    async with BleakClient(address) as client:
        print(f"Connected: {client.is_connected}")
        await client.start_notify(gyro_uuid, gyro_handler)
        #await client.start_notify(accel_uuid, accel_handler)
        print("Notifications enabled... Reading data")
        await asyncio.sleep(1.0)
        await client.stop_notify(gyro_uuid)
        #await client.stop_notify(accel_uuid)
        print("Reading complete")

# Collect data over BLE.
asyncio.run(collect_data(ADDRESS, GYRO_UUID, ACCEL_UUID))

print(gyro_byte_buffer)

'''
import struct
import pandas as pd
import time

# Convert gyro data to a dataframe.
timestamp_list = []
x_list, y_list, z_list = [], [], []
for entry in gyro_byte_buffer:
    [timestamp_entry, gyro_entry] = entry.split("; ")
    timestamp_entry = datetime.strptime(timestamp_entry, "%Y-%m-%d %H:%M:%S.%f")
    timestamp_entry = timestamp_entry.strftime("%H:%M:%S.%f")
    timestamp_list.append(timestamp_entry)
    
    gyro_entry = bytes.fromhex(gyro_entry)
    [x, y, z] = struct.unpack('fff', gyro_entry)
    x_list.append(x)
    y_list.append(y)
    z_list.append(z)  
df_gyro = pd.DataFrame()
df_gyro["Timestamp"] = timestamp_list
df_gyro["X-axis (deg/s)"] = x_list
df_gyro["Y-axis (deg/s)"] = y_list
df_gyro["Z-axis (deg/s)"] = z_list

# Convert accelerometer data to a dataframe.
timestamp_list = []
x_list, y_list, z_list = [], [], []
for entry in accel_byte_buffer:
    [timestamp_entry, accel_data] = entry.split("; ")
    timestamp_entry = datetime.strptime(timestamp_entry, "%Y-%m-%d %H:%M:%S.%f")
    timestamp_entry = timestamp_entry.strftime("%H:%M:%S.%f")
    timestamp_list.append(timestamp_entry)
    
    accel_data = bytes.fromhex(accel_data)
    [x, y, z] = struct.unpack('fff', accel_data)
    x_list.append(x)
    y_list.append(y)
    z_list.append(z)  
df_accel = pd.DataFrame()
df_accel["Timestamp"] = timestamp_list
df_accel["X-axis (g)"] = x_list
df_accel["Y-axis (g)"] = y_list
df_accel["Z-axis (g)"] = z_list

# Merge gyro datafram and accelerometer dataframe into a single dataframe.
df_merge = pd.merge(df_gyro, df_accel,  how="inner", on=["Timestamp", "Timestamp"], sort=True)  
df_merge.index.name = 'Sample'

# Create a column for "time delta".
df_merge["Timestamp"] = pd.to_datetime(df_merge["Timestamp"])
init_time = df_merge["Timestamp"].iloc[0]
time_deltas = df_merge["Timestamp"] - init_time + pd.Timestamp(0)
df_merge["Timedelta"] = time_deltas

# Reorganzie columns.
df_merge = df_merge[[
    "Timestamp",
    "Timedelta",
    "X-axis (deg/s)",
    "Y-axis (deg/s)",
    "Z-axis (deg/s)",
    "X-axis (g)",
    "Y-axis (g)",
    "Z-axis (g)"]].copy()

# Write to Excel
writer = pd.ExcelWriter("output.xlsx", datetime_format='hh:mm:ss.000')
df_merge.to_excel(writer, sheet_name="Data")
writer.sheets['Data'].set_column(0, 0, 8)
writer.sheets['Data'].set_column(1, len(df_merge.columns)+1, 12)
writer.close()
print("Output to Excel complete")'''