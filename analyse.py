import sqlite3
import os
import pandas as pd

def task_status_sign_monitoring(cursor:sqlite3.Cursor, name:str):
    sql = """
        SELECT is_done FROM task_status
        WHERE task_name=?
    """
    cursor.execute(sql, (name,))
    sign = cursor.fetchone()
    return sign

def task_status_sign_update(cursor:sqlite3.Cursor, name:str):
    sql = """
        INSERT INTO task_status(task_name, is_done)
        VALUES (?, 1)
    """
    cursor.execute(sql, (name,))



db_path = "./Data/UserBehavior.db"

# 数据库存在，对数据进行分析
if os.path.exists(db_path):
    # 连接数据库
    conn = sqlite3.connect(db_path)
    print("数据库存在, 已连接！")

    # 创建游标
    cursor = conn.cursor()


    print("----------用户流量及购物概况分析----------")
    sign1 = task_status_sign_monitoring(cursor, 'metric_overview_sign')

    # 分析周期总访问量
    if sign1 and sign1[0]==1:
        # 接收结果
        cursor.execute("""
            SELECT * FROM metric_overview
        """)
        result1 = cursor.fetchone()

        if result1:
            print(f"周期总访问量为：{result1[0]}")
            print(f"独立访客数为：{result1[1]}")
        else:
            print("未查询到数据！")
    else:
        cursor.execute("""
            CREATE TABLE metric_overview AS
            SELECT
                SUM(CASE WHEN behavior_type = 'pv' THEN 1 ELSE 0 END) AS pv_nums,
                COUNT(DISTINCT user_id) AS uv_nums 
            FROM user_behavior
        """)
        conn.commit()

        # 接收结果
        cursor.execute("""
            SELECT * FROM metric_overview
        """)
        result1 = cursor.fetchone()

        if result1:
            print(f"周期总访问量为：{result1[0]}")
            print(f"独立访客数为：{result1[1]}")
        else:
            print("未查询到数据！")
        task_status_sign_update(cursor, 'metric_overview_sign')
        conn.commit()


    # 用户画像聚合
    # 创建中间表
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
    # 判断聚合任务是否完成
    sign2 = task_status_sign_monitoring(cursor, 'user_behavior_count_sign')

    if sign2 and sign2[0]==1:
        print("用户画像已聚合！")
    else:
        # 未进行聚合，插入聚合数据
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
        # 更新聚合任务状态，改为已完成
        task_status_sign_update(cursor, 'user_behavior_count_sign')
        conn.commit()
        print("用户画像已经聚合！")


    # 复购率计算
    cursor.execute("""
        SELECT
            SUM(CASE WHEN buy_type > 1 THEN 1 ELSE 0 END) * 1.0 / SUM(CASE WHEN buy_type > 0 THEN 1 ELSE 0 END)
        FROM user_behavior_count
    """)
    result2 = cursor.fetchone()
    print(f"“购买次数 ≥ 2 的用户数”占“总购买用户数”的比例为：{result2[0]:.4f}")


    print("----------用户行为转化漏斗分析----------")
    sign3 = task_status_sign_monitoring(cursor, 'conversion_rate_sign')
    
    if sign3 and sign3[0]==1:
        cursor.execute("""
            SELECT * FROM conversion_rate
        """)
        result3 = cursor.fetchone()
        print(f"第一步转化率：(收藏数 + 加购数) / 点击数 (PV) = {result3[0]:.4f}")
        print(f"第二步转化率：购买数 / (收藏数 + 加购数) = {result3[1]:.4f}")
        print(f"总体转化率：购买数 / 点击数 (PV) = {result3[2]:.4f}")
    else:
        cursor.execute("""
            CREATE TABLE conversion_rate AS
            SELECT
                (SUM(CASE WHEN behavior_type = 'fav' THEN 1 ELSE 0 END) + SUM(CASE WHEN behavior_type = 'cart' THEN 1 ELSE 0 END)) * 1.0 / SUM(CASE WHEN behavior_type = 'pv' THEN 1 ELSE 0 END) AS one_rate,
                SUM(CASE WHEN behavior_type = 'buy' THEN 1 ELSE 0 END) * 1.0 / (SUM(CASE WHEN behavior_type = 'fav' THEN 1 ELSE 0 END) + SUM(CASE WHEN behavior_type = 'cart' THEN 1 ELSE 0 END)) AS two_rate,
                SUM(CASE WHEN behavior_type = 'buy' THEN 1 ELSE 0 END) * 1.0/ SUM(CASE WHEN behavior_type = 'pv' THEN 1 ELSE 0 END) AS overall_rate
            FROM user_behavior
        """)
        conn.commit()

        cursor.execute("""
            SELECT * FROM conversion_rate
        """)
        result3 = cursor.fetchone()
        print(f"第一步转化率：(收藏数 + 加购数) / 点击数 (PV) = {result3[0]:.4f}")
        print(f"第二步转化率：购买数 / (收藏数 + 加购数) = {result3[1]:.4f}")
        print(f"总体转化率：购买数 / 点击数 (PV) = {result3[2]:.4f}")

        task_status_sign_update(cursor, 'conversion_rate_sign')
        conn.commit()


    print("----------用户行为习惯分析（时间维度）----------")
    print("----------日内活跃时段----------")
    sign4 = task_status_sign_monitoring(cursor, 'behavior_hourly_sign')

    if sign4 and sign4[0]==1:
        cursor.execute("""
            SELECT * FROM behavior_hourly
        """)
        result4 = cursor.fetchall()
        print(f"{'小时':<5} | {'点击':<10} | {'收藏':<10} | {'加购':<10} | {'购买':<10}")
        print("-" * 60)
        for row in result4:
            hour, pv, fav, cart, buy = row
            print(f"{hour:<5} | {str(pv):<10} | {str(fav):<10} | {str(cart):<10} | {str(buy):<10}")
    else:
        cursor.execute("""
            CREATE TABLE behavior_hourly AS
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
        conn.commit()

        cursor.execute("""
            SELECT * FROM behavior_hourly
        """)
        result4 = cursor.fetchall()
        print(f"{'小时':<5} | {'点击':<10} | {'收藏':<10} | {'加购':<10} | {'购买':<10}")
        print("-" * 60)
        for row in result4:
            hour, pv, fav, cart, buy = row
            print(f"{hour:<5} | {str(pv):<10} | {str(fav):<10} | {str(cart):<10} | {str(buy):<10}")

        task_status_sign_update(cursor, 'behavior_hourly_sign')
        conn.commit()
    
    print("----------周内活跃分布----------")
    sign5 = task_status_sign_monitoring(cursor, 'behavior_weekly_sign')

    if sign5 and sign5[0]==1:
        cursor.execute("""
            SELECT * FROM behavior_weekly
        """)
        result5 = cursor.fetchall()
        print(f"{'week':<5} | {'点击':<10} | {'收藏':<10} | {'加购':<10} | {'购买':<10}")
        print("-" * 60)
        for row in result5:
            week, pv, fav, cart, buy = row
            print(f"{week:<5} | {str(pv):<10} | {str(fav):<10} | {str(cart):<10} | {str(buy):<10}")
    else:
        cursor.execute("""
            CREATE TABLE behavior_weekly AS
            SELECT
                CASE CAST(strftime('%w', datetime) AS INTEGER) 
                    WHEN 0 THEN 'Sunday'
                    WHEN 1 THEN 'Monday'
                    WHEN 2 THEN 'Tuesday'
                    WHEN 3 THEN 'Wednesday'
                    WHEN 4 THEN 'Thursday'
                    WHEN 5 THEN 'Friday'
                    WHEN 6 THEN 'Saturday'
                END AS week,
                SUM(CASE WHEN behavior_type = 'pv' THEN 1 ELSE 0 END) AS pv_week,
                SUM(CASE WHEN behavior_type = 'fav' THEN 1 ELSE 0 END) AS fav_week,
                SUM(CASE WHEN behavior_type = 'cart' THEN 1 ELSE 0 END) AS cart_week,
                SUM(CASE WHEN behavior_type = 'buy' THEN 1 ELSE 0 END) AS buy_week
            FROM user_behavior
            GROUP BY CAST(strftime('%w', datetime) AS INTEGER)
            ORDER BY 
                CASE CAST(strftime('%w', datetime) AS INTEGER)
                    WHEN 0 THEN 7
                    ELSE CAST(strftime('%w', datetime) AS INTEGER)
                END
        """)
        conn.commit()

        cursor.execute("""
            SELECT * FROM behavior_weekly
        """)
        result5 = cursor.fetchall()
        print(f"{'week':<5} | {'点击':<10} | {'收藏':<10} | {'加购':<10} | {'购买':<10}")
        print("-" * 60)
        for row in result5:
            week, pv, fav, cart, buy = row
            print(f"{week:<5} | {str(pv):<10} | {str(fav):<10} | {str(cart):<10} | {str(buy):<10}")

        task_status_sign_update(cursor, 'behavior_weekly_sign')
        conn.commit()

    print("----------高价值用户挖掘 (RF模型)----------")
    # WITH TABLE AS() 创建临时表，RankData 和 ScoreData 也为临时表
    # WITH 末尾要跟搜索语句
    # R (Recency)：计算每个用户最后一次购买时间距离基准日（2017-12-04）的天数，天数越少（R值越小）越活跃。
    # F (Frequency)：统计每个用户的总购买次数，次数越多越忠诚。
    # 打分逻辑：使用窗口函数 dense_rank() 对 R 和 F 分别排名，
    # 再用 ntile(5) 将用户均分为 5 个梯队，分别赋予 5~1 分。
    # 最后将 R 分和 F 分相加得到用户总价值得分，得分最高的 Top 用户即为高价值核心用户，可用于后续的精准营销。
    sign6 = task_status_sign_monitoring(cursor, 'user_rf_top_sign')

    if sign6 and sign6[0]==1:
        cursor.execute("""
            SELECT * FROM user_rf_top
            LIMIT 10
        """)
        result6 = cursor.fetchall()
        for row in result6:
            print(row)
    else:
        cursor.execute("""
            CREATE TABLE user_rf_top AS
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
        """)
        conn.commit()

        cursor.execute("""
            SELECT * FROM user_rf_top
            LIMIT 10
        """)
        result6 = cursor.fetchall()
        for row in result6:
            print(row)

        task_status_sign_update(cursor, 'user_rf_top_sign')
        conn.commit()


    print("----------商品维度分析----------")
    print("----------Top 10 爆款商品！----------")
    sign7 = task_status_sign_monitoring(cursor, 'top_items_sign')

    if sign7 and sign7[0]==1:
        cursor.execute("""
            SELECT * FROM top_items
        """)
        result7 = cursor.fetchall()
        for row in result7:
            print(row)
    else:
        cursor.execute("""
            CREATE TABLE top_items AS
            SELECT
                item_id,
                SUM(CASE WHEN behavior_type = 'pv' THEN 1 ELSE 0 END) AS pv_item,
                SUM(CASE WHEN behavior_type = 'fav' THEN 1 ELSE 0 END) AS fav_item,
                SUM(CASE WHEN behavior_type = 'cart' THEN 1 ELSE 0 END) AS cart_item,
                SUM(CASE WHEN behavior_type = 'buy' THEN 1 ELSE 0 END) AS buy_item
            FROM user_behavior
            GROUP BY item_id
            ORDER BY buy_item DESC
            LIMIT 10
        """)
        conn.commit()

        cursor.execute("""
            SELECT * FROM top_items
        """)
        result7 = cursor.fetchall()
        for row in result7:
            print(row)

        task_status_sign_update(cursor, 'top_items_sign')
        conn.commit()


    print("----------Top 10 热门类目! ----------")
    sign8 = task_status_sign_monitoring(cursor, 'top_categories_sign')

    if sign8 and sign8[0]==1:
        cursor.execute("""
            SELECT * FROM top_categories
        """)
        result8 = cursor.fetchall()
        for row in result8:
            print(row)
    else:
        cursor.execute("""
            CREATE TABLE top_categories AS
            SELECT
                category_id,
                SUM(CASE WHEN behavior_type = 'pv' THEN 1 ELSE 0 END) AS pv_category,
                SUM(CASE WHEN behavior_type = 'fav' THEN 1 ELSE 0 END) AS fav_category,
                SUM(CASE WHEN behavior_type = 'cart' THEN 1 ELSE 0 END) AS cart_category,
                SUM(CASE WHEN behavior_type = 'buy' THEN 1 ELSE 0 END) AS buy_category
            FROM user_behavior
            GROUP BY category_id
            ORDER BY buy_category DESC
            LIMIT 10
        """)
        conn.commit()

        cursor.execute("""
            SELECT * FROM top_categories
        """)
        result8 = cursor.fetchall()
        for row in result8:
            print(row)

        task_status_sign_update(cursor, 'top_categories_sign')
        conn.commit()

    #df = pd.read_sql_query("SELECT * FROM user_behavior_count LIMIT 10", conn)
    #print(df)

    # 释放游标和数据库连接
    cursor.close()
    conn.close()
else:
    print("数据库不存在！")
