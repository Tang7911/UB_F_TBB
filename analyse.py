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

    cursor.execute("""
        SELECT
            (SUM(CASE WHEN behavior_type = 'fav' THEN 1 ELSE 0 END) + SUM(CASE WHEN behavior_type = 'cart' THEN 1 ELSE 0 END)) * 1.0 / SUM(CASE WHEN behavior_type = 'pv' THEN 1 ELSE 0 END),
            SUM(CASE WHEN behavior_type = 'buy' THEN 1 ELSE 0 END) * 1.0 / (SUM(CASE WHEN behavior_type = 'fav' THEN 1 ELSE 0 END) + SUM(CASE WHEN behavior_type = 'cart' THEN 1 ELSE 0 END)),
            SUM(CASE WHEN behavior_type = 'buy' THEN 1 ELSE 0 END) * 1.0/ SUM(CASE WHEN behavior_type = 'pv' THEN 1 ELSE 0 END)
        FROM user_behavior
    """)
    result3 = cursor.fetchone()
    print(f"第一步转化率：(收藏数 + 加购数) / 点击数 (PV) = {result3[0]:.4f}")
    print(f"第二步转化率：购买数 / (收藏数 + 加购数) = {result3[1]:.4f}")
    print(f"总体转化率：购买数 / 点击数 (PV) = {result3[2]:.4f}")

    cursor.execute("""
        SELECT
            strftime('%H', datetime) AS hour,
            SUM(CASE WHEN behavior_type = 'pv' THEN 1 ELSE 0 END) AS pv_hour,
            SUM(CASE WHEN behavior_type = 'fav' THEN 1 ELSE 0 END) AS fav_hour,
            SUM(CASE WHEN behavior_type = 'cart' THEN 1 ELSE 0 END) AS cart_hour,
            SUM(CASE WHEN behavior_type = 'buy' THEN 1 ELSE 0 END) AS buy_hour
        FROM user_behavior
        GROUP BY hour
        ORDER BY hour
    """)
    result4 = cursor.fetchall()
    print(f"{'小时':<5} | {'点击':<10} | {'收藏':<10} | {'加购':<10} | {'购买':<10}")
    print("-" * 60)
    for row in result4:
        hour, pv, fav, cart, buy = row
        print(f"{hour:<5} | {str(pv):<10} | {str(fav):<10} | {str(cart):<10} | {str(buy):<10}")

    cursor.execute("""
        SELECT
            strftime('%w', datetime) AS week,
            SUM(CASE WHEN behavior_type = 'pv' THEN 1 ELSE 0 END) AS pv_hour,
            SUM(CASE WHEN behavior_type = 'fav' THEN 1 ELSE 0 END) AS fav_hour,
            SUM(CASE WHEN behavior_type = 'cart' THEN 1 ELSE 0 END) AS cart_hour,
            SUM(CASE WHEN behavior_type = 'buy' THEN 1 ELSE 0 END) AS buy_hour
        FROM user_behavior
        GROUP BY week
        ORDER BY week
    """)
    result5 = cursor.fetchall()
    print(f"{'week':<5} | {'点击':<10} | {'收藏':<10} | {'加购':<10} | {'购买':<10}")
    print("-" * 60)
    for row in result5:
        week, pv, fav, cart, buy = row
        print(f"{week:<5} | {str(pv):<10} | {str(fav):<10} | {str(cart):<10} | {str(buy):<10}")

    cursor.execute("""
        WITH CTE AS (
            SELECT
                user_id,
                CAST(JULIANDAY('2017-12-04') - JULIANDAY(MAX(datetime)) AS INTEGER) AS R,
                COUNT(*) AS F
            FROM user_behavior
            WHERE behavior_type = 'buy'
            GROUP BY user_id
        ),
        
        RankData AS (
            SELECT
                user_id,
                R,
                F,
                DENSE_RANK() OVER (ORDER BY R ASC) AS R_rank,
                DENSE_RANK() OVER (ORDER BY F DESC) AS F_rank
            FROM CTE
        ),

        ScoreData AS (
            SELECT
                user_id,
                R,
                R_rank,
                F,
                F_rank,
                CASE NTILE(5) OVER(ORDER BY R_rank) WHEN 1 THEN 5
                                                    WHEN 2 THEN 4
                                                    WHEN 3 THEN 3
                                                    WHEN 4 THEN 2
                                                    WHEN 5 THEN 1
                END AS R_score,
                CASE NTILE(5) OVER(ORDER BY F_rank) WHEN 1 THEN 5
                                                    WHEN 2 THEN 4
                                                    WHEN 3 THEN 3
                                                    WHEN 4 THEN 2
                                                    WHEN 5 THEN 1
                END AS F_score
            FROM RankData
        )
        
        SELECT
            user_id,
            R, R_rank, R_score,
            F, F_rank, F_score,
            (R_score + F_score) AS score
        FROM ScoreData
        ORDER BY score DESC, R_score DESC
        LIMIT 20
    """)
    result6 = cursor.fetchall()
    for row in result6:
        print(row)

    #df = pd.read_sql_query("SELECT * FROM user_behavior_count LIMIT 10", conn)
    #print(df)

    # 释放游标和数据库连接
    cursor.close()
    conn.close()
else:
    print("数据库不存在！")
