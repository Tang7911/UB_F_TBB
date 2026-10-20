import sqlite3
import os
import pandas as pd

db_path = "./Data/UserBehavior.db"

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    print("数据库存在, 已连接！")

    cursor = conn.cursor()
    cursor.execute("""
        SELECT COUNT(*) AS pv_nums FROM user_behavior
        WHERE behavior_type='pv'
    """)
    result1 = cursor.fetchone()

    cursor.execute("""
        SELECT COUNT(DISTINCT user_id) AS uv_nums FROM user_behavior
    """)
    result2 = cursor.fetchone()

    if result1 and result2:
        print(f"周期总访问量为：{result1[0]}")
        print(f"独立访客数为：{result2[0]}")
    else:
        print("未查询到数据！")

    cursor.close()
    conn.close()
else:
    print("数据库不存在！")
