import sqlite3
import os
import pandas as pd

db_path = "./Data/UserBehavior.db"

# 数据库存在，对数据进行分析
if os.path.exists(db_path):
    # 连接数据库
    conn = sqlite3.connect(db_path)
    print("数据库存在, 已连接！")

    # 创建游标
    cursor = conn.cursor()
    # 分析周期总访问量
    cursor.execute("""
        SELECT COUNT(*) AS pv_nums FROM user_behavior
        WHERE behavior_type='pv'
    """)
    # 接收结果
    result1 = cursor.fetchone()

    # 分析独立访客数
    cursor.execute("""
        SELECT COUNT(DISTINCT user_id) AS uv_nums FROM user_behavior
    """)
    result2 = cursor.fetchone()

    if result1 and result2:
        print(f"周期总访问量为：{result1[0]}")
        print(f"独立访客数为：{result2[0]}")
    else:
        print("未查询到数据！")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_behavior_count (
            user_id TEXT comment '用户ID',
            pv_type INTEGER comment '点击数',
            fav_type INTEGER comment '收藏数',
            cart_type INTEGRE comment '加购',
            buy_type INTEGER comment '购买'
        )
    """)
    conn.commit()

    cursor.execute("""
        SELECT is_done FROM task_status
        WHERE task_name='user_behavior_agg'
    """)
    result1 = cursor.fetchone()

    if result1 and result1[0]==1:
        print("用户画像已聚合！")
    else:
        cursor.execute("""
            INSERT INTO user_behavior_count (user_id, pv_type, fav_type, cart_type, buy_type)
            SELECT
                user_id,
                SUM(CASE WHEN behavior_type = 'pv' THEN 1 ELSE 0 END) AS pv_type,
                SUM(CASE WHEN behavior_type = 'fav' THEN 1 ELSE 0 END) AS fav_type,
                SUM(CASE WHEN behavior_type = 'cart' THEN 1 ELSE 0 END) AS cart_type,
                SUM(CASE WHEN behavior_type = 'buy' THEN 1 ELSE 0 END) AS buy_type
            FROM user_behavior
            GROUP BY user_id
        """)

        cursor.execute("""
            INSERT INTO task_status(task_name, is_done)
            VALUES ('user_behavior_agg', 1)
        """)
        conn.commit()
        print("用户画像已经聚合！")

    cursor.execute("""
        SELECT
            SUM(CASE WHEN buy_type > 1 THEN 1 ELSE 0 END) * 1.0 / SUM(CASE WHEN buy_type > 0 THEN 1 ELSE 0 END)
        FROM user_behavior_count
    """)
    result2 = cursor.fetchone()
    print(f"“购买次数 ≥ 2 的用户数”占“总购买用户数”的比例为：{result2[0]:.4f}")

    #df = pd.read_sql_query("SELECT * FROM user_behavior_count LIMIT 10", conn)
    #print(df)

    # 释放游标和数据库连接
    cursor.close()
    conn.close()
else:
    print("数据库不存在！")
