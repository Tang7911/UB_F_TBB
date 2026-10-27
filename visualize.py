import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import sqlite3

db_path = "./Data/UserBehavior.db"
conn = sqlite3.connect(db_path)

hour_data = pd.read_sql_query("SELECT * FROM behavior_hourly", con=conn)
# print(hour_data)
plt.figure(figsize=(12, 6))
sns.lineplot(data=hour_data, x='hour', y='pv_hour', marker='o', linewidth=2.5, color='#1f77b4', label='PV')
sns.lineplot(data=hour_data, x='hour', y='buy_hour', marker='o', linewidth=2.5, color='#d62728', label='Buy')

plt.title('Taobao users 24-hour activity and buying trends', fontsize=16, fontweight='bold', pad=15)
plt.xlabel('Time(hour)', fontsize=12)
plt.ylabel('Number of actions', fontsize=12)
plt.xticks(range(0, 24))
plt.legend(fontsize=11)

plt.savefig('./Data/24_Hour_Activity_Trend.png', dpi=300, bbox_inches='tight')
# plt.show()

conn.close()
