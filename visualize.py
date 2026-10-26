import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import sqlite3

db_path = "./Data/UserBehavior.db"
conn = sqlite3.connect(db_path)

hour_data = pd.read_sql_query("SELECT * FROM behavior_hourly", con=conn)
# print(hour_data)

conn.close()
