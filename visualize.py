import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import sqlite3

db_path = "./Data/UserBehavior.db"
conn = sqlite3.connect(db_path)

# ----------24 小时用户活跃趋势----------
hour_data = pd.read_sql_query("SELECT * FROM behavior_hourly", con=conn)
# print(hour_data)
plt.figure(figsize=(12, 6))
# sns.lineplot绘制折线 marker='o'设置点，linewidth设置折线粗细，label设置折线名字
sns.lineplot(data=hour_data, x='hour', y='pv_hour', marker='o', linewidth=2.5, color='#1f77b4', label='PV')
sns.lineplot(data=hour_data, x='hour', y='buy_hour', marker='o', linewidth=2.5, color='#d62728', label='Buy')

# fontsize设置文字大小，fontweight='bold'文字加粗，pad设置文字与图的距离
plt.title('Taobao users 24-hour activity and buying trends', fontsize=16, fontweight='bold', pad=15)
plt.xlabel('Time(hour)', fontsize=12)
plt.ylabel('Number of actions', fontsize=12)
# 设置x轴刻度
plt.xticks(range(0, 24))
# 让折线名字显示出来，同时设置文字大小
plt.legend(fontsize=11)

plt.savefig('./Data/24_Hour_Activity_Trend.png', dpi=300, bbox_inches='tight')

# ----------一周七天用户活跃趋势----------
week_data = pd.read_sql_query("SELECT * FROM behavior_weekly", con=conn)
plt.figure(figsize=(12, 6))
sns.lineplot(data=week_data, x='week', y='pv_week', marker='o', linewidth=2.5, color='#1f77b4', label='PV')
sns.lineplot(data=week_data, x='week', y='buy_week', marker='o', linewidth=2.5, color='#d62728', label='Buy')

plt.title('Taobao users 7-week activity and buying trends', fontsize=16, fontweight='bold', pad=15)
plt.xlabel('Week(day)', fontsize=12)
plt.ylabel('Number of actions', fontsize=12)
plt.xticks(range(0, 7))
plt.legend(fontsize=11)

plt.savefig('./Data/7_week_Activity_Trend.png', dpi=300, bbox_inches='tight')


conn.close()
