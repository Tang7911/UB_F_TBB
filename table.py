import pandas as pd
import sqlite3
import os

# csv 文件地址 与 db 文件地址
csv_path = "./Data/UserBehavior.csv"
db_path = "./Data/UserBehavior.db"

# os.path.exists 判断 db 文件是否存在
if os.path.exists(db_path):
    print("数据库已存在，直接读取")
    # 连接数据库
    conn = sqlite3.connect(db_path)
    #df=pd.read_sql_query("SELECT * FROM user_behavior LIMIT 10", conn)
    #print(df)
else:
    print("数据库不存在，开始导入...")
    # 连接数据库，若数据库不存在，则创建
    conn = sqlite3.connect(db_path)
    # 创建游标对象 游标对象可用来发送 SQL 语句
    cursor = conn.cursor()
    # 使用游标执行 SQL ，创建表
    cursor.execute("""
        CREATE TABLE user_behavior (
                user_id TEXT comment '用户ID',
                item_id TEXT comment '商品ID',
                category_id TEXT comment '商品类目ID',
                behavior_type TEXT comment '行为类型. 枚举类型. 包括(pv, buy, cart, fav)',
                timestamp INTEGER comment '行为时间戳',
                datetime TEXT comment '行为时间'
        )
    """)

    # 提交事务，将数据存入硬盘
    conn.commit()
    columns = ["user_id", "item_id", "category_id", "behavior_type", "timestamp"]

    chunk_size = 200000
    # 分块读取 csv 文件
    # enumerate 计数器返回序号给 i ,返回数据给 chunk
    # header=None 告诉 Pandas 别把第一行当表头
    # 因为header，数据现在没有表头。所以 names=columns 给数据贴上新标签
    for i, chunk in enumerate(pd.read_csv(csv_path, header=None, names=columns,chunksize = chunk_size)):
        # 数据写入sql
        # if_exists="append(表存在追加数据)/fail(表存在报错)/replace(表存在重新建表)"
        # index=False 禁止 Pandas 写入自带行号
        chunk.to_sql("user_behavior", conn, if_exists="append", index=False)
        print(f"已处理第 {i+1} 块，写入 {len(chunk)} 行")

    # 将 Unix 时间戳批量转换为“年月日 时分秒”的格式，保存到 datetime 这一列
    cursor.execute("""
        UPDATE user_behavior
        SET datetime = datetime(timestamp, 'unixepoch', 'localtime')
    """)
    conn.commit()
    cursor.close()
    print("导入完成！")

cursor=conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS task_status(
        task_name TEXT PRIMARY KEY,
        is_done INTEGER NOT NULL DEFAULT 0
    )
""")
cursor.execute("""
    SELECT is_done FROM task_status
    WHERE task_name='user_behavior_clean'
""")
result=cursor.fetchone()

if result and result[0]==1:
    print("数据清洗完毕！")
else:
    # 去除重复数据
    cursor.execute("""
        CREATE TABLE user_behavior_new AS
        SELECT DISTINCT * FROM user_behavior
    """)
    cursor.execute("DROP TABLE user_behavior")
    cursor.execute("ALTER TABLE user_behavior_new RENAME TO user_behavior")
    # 过滤时间异常值
    cursor.execute("""
        DELETE FROM user_behavior
        WHERE datetime NOT BETWEEN '2017-11-25 00:00:00' AND '2017-12-03 23:59:59'
    """)
    print("数据清洗完毕！")

    cursor.execute("""
        INSERT INTO task_status (task_name, is_done)
        VALUES ('user_behavior_clean', 1)
    """)
    conn.commit()

# 关闭数据库连接
cursor.close()
conn.close()
print(f"数据导入完成！数据已保存至：{db_path}")