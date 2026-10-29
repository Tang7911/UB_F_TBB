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

# RF 用户价值分层散点图
rf_data = pd.read_sql_query("SELECT user_id, R, F, score FROM user_rf_top", con=conn)

plt.figure(figsize=(10, 7))
scatter = sns.scatterplot(
    data = rf_data,
    x='R', y='F',
    size='score', sizes=(50, 500),
    hue='score', palette='Reds',
    legend='full'
)

plt.title('High-Value User Segmentation (Top 20) Based on RF Model', fontsize=16, fontweight='bold', pad=15)
plt.xlabel('R', fontsize=12)
plt.ylabel('F', fontsize=12)

for i in range(min(3, len(rf_data))):
    plt.annotate(rf_data.iloc[i]['user_id'],
                (rf_data.iloc[i]['R'], rf_data.iloc[i]['F']),
                textcoords="offset points", xytext=(5,5), ha='left', fontsize=9, color='blue'
    )

plt.savefig('./Data/RFM_User_Value_Segmentation.png', dpi=300, bbox_inches='tight')

# Top10爆款商品
item_data = pd.read_sql_query("SELECT item_id, buy_item FROM top_items", con=conn)
plt.figure(figsize=(12, 6))
sns.barplot(data=item_data, x='item_id', y='buy_item')
plt.title("Top 10 Best-Selling Products Bar Chart", fontsize=16, fontweight='bold', pad=15)
plt.xlabel("item_id", fontsize=12)
plt.ylabel("buy_item", fontsize=12)
plt.savefig('./Data/Best_Selling_Products_Bar_Chart.png', dpi=300, bbox_inches='tight')

# Top10热门类目
category_data = pd.read_sql_query("SELECT category_id, buy_category FROM top_categories", con=conn)
plt.figure(figsize=(12, 6))
sns.barplot(data=category_data, x='category_id', y='buy_category')
plt.title("Top 10 Popular Category Bar Chart", fontsize=16, fontweight='bold', pad=15)
plt.xlabel("category_id", fontsize=12)
plt.ylabel("buy_category", fontsize=12)
plt.savefig('./Data/Popular_Category_Bar_Chart.png', dpi=300, bbox_inches='tight')

conn.close()
