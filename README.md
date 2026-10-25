# UB_F_TBB (User Behavior From Taobao Batch)

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![SQLite](https://img.shields.io/badge/Database-SQLite-lightgrey.svg)](https://www.sqlite.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> 🚀 基于 Python + SQLite 的淘宝用户行为数据分析项目（Hive 离线批处理复刻版）

## 📖 项目简介

本项目是经典大数据实战项目 [UserBehaviorFromTaobao_Batch](https://github.com/TurboWay/bigdata_analyse/tree/main/UserBehaviorFromTaobao_Batch) 的 **Python + SQLite 轻量化复刻版本**。原项目使用 Hive 进行离线批处理，本项目将其迁移至 Python 生态，利用 SQLite 作为数据存储与查询引擎，实现了完整的亿级用户行为数据清洗、聚合与多维度分析流程。

本项目旨在提供一个低门槛、易部署的数据分析基线，适合用于学习 SQL 数据分析、理解电商用户行为指标，并作为后续高性能计算（如 Polars）和数据可视化的实验底座。

---

## 📊 数据集说明

- **数据来源**：阿里巴巴天池公开数据集（淘宝用户行为数据）
- **时间跨度**：2017-11-25 至 2017-12-03（共9天，含双12前夕及周末）
- **数据规模**：约 1 亿条记录（原始 CSV 约 3.5GB）
- **字段说明**：
  | 字段名 | 类型 | 描述 |
  | :--- | :--- | :--- |
  | `user_id` | TEXT | 用户ID |
  | `item_id` | TEXT | 商品ID |
  | `category_id` | TEXT | 商品类目ID |
  | `behavior_type`| TEXT | 行为类型，枚举值：`pv`(点击), `fav`(收藏), `cart`(加购), `buy`(购买) |
  | `timestamp` | INTEGER | 行为时间戳 |
  | `datetime` | TEXT | 格式化后的行为时间 (YYYY-MM-DD HH:MM:SS) |

---

## 🛠️ 核心分析功能

本项目通过 SQL 实现了以下核心电商数据分析指标：

1. **数据清洗 (Data Cleaning)**  
   - 去除完全重复的记录 (`DISTINCT`)。
   - 过滤非目标时间段（2017-11-25 至 2017-12-03）的异常数据。
   - 引入 `task_status` 状态表，实现数据清洗任务的**幂等性控制**，避免重复处理。

2. **流量与用户规模 (Traffic & UV/PV)**  
   - 统计周期内的总访问量 (PV) 和独立访客数 (UV)。

3. **用户行为聚合 (User Behavior Aggregation)**  
   - 构建 `user_behavior_count` 用户画像宽表，按 `user_id` 聚合统计每个用户的点击、收藏、加购、购买次数。

4. **漏斗转化率分析 (Funnel Conversion Rate)**  
   - 第一步转化率：`(收藏数 + 加购数) / 点击数 (PV)`
   - 第二步转化率：`购买数 / (收藏数 + 加购数)`
   - 总体转化率：`购买数 / 点击数 (PV)`

5. **时间维度分析 (Time-series Analysis)**  
   - **小时级**：统计一天 24 小时内各行为类型的分布，识别用户活跃高峰（如 21:00-22:00）。
   - **星期级**：统计一周内各天的行为分布，对比工作日与周末的活跃度差异。

6. **RFM 用户价值分层 (RFM Model)**  
   - 基于购买行为计算 **R (Recency, 最近一次购买距今天数)** 和 **F (Frequency, 消费频率)**。
   - 使用 `NTILE(5)` 窗口函数对 R 和 F 进行 5 分位打分，计算综合得分，输出 Top 20 高价值用户，为精准营销提供依据。

7. **商品与类目热度分析 (Product & Category Heat)**  
   - 统计并输出 Top 10 爆款商品（按购买量降序排列）。
   - 统计并输出 Top 10 热门商品类目。

---

## 📁 项目结构

```text
UB_F_TBB/
├── Data/                   # 数据目录 (已在 .gitignore 中忽略)
│   ├── UserBehavior.csv    # 原始数据集 (需自行下载)
│   └── UserBehavior.db     # SQLite 数据库文件 (运行后自动生成)
├── table.py                # 数据导入、建表与数据清洗逻辑 (含任务状态管理)
├── analyse.py              # 核心数据分析 SQL 查询与终端结果输出
├── .gitignore              # Git 忽略配置 (忽略虚拟环境和 .db 文件)
└── README.md               # 项目说明文档
```
---

## 🚀 快速开始

1. **环境准备**
Python 3.8+ (本项目仅依赖 Python 内置的 sqlite3 和 os 模块，无需安装第三方重型依赖)。
确保有足够的磁盘空间（建议 > 10GB）用于存放 CSV 和 SQLite 数据库文件。

2. **数据准备**
下载 淘宝用户行为数据集 (或从其他镜像源获取 UserBehavior.csv)。
在项目根目录下创建 Data 文件夹，并将 UserBehavior.csv 放入其中。

3. **运行项目**
# 1. 执行数据建表与清洗 (首次运行会自动导入 CSV，后续运行检测到标记会跳过清洗)
python table.py

# 2. 执行数据分析并打印结果
python analyse.py

## 🔮 未来计划 (Roadmap)
    - 📊 数据可视化 (Data Visualization)：引入 Matplotlib / Seaborn / Plotly，将转化率漏斗、小时/星期活跃度趋势、RFM 评分分布等分析结果转化为直观的交互式图表。
    - ⚡ Polars 版本重构：使用 Polars 替代 SQLite 进行内存/外存 DataFrame 计算，探索现代 Python 数据分析的最佳实践，大幅提升亿级数据的处理性能。
    - 📈 进阶分析：在引入商品维表的前提下，补充品类转化率、复购率深度分析及用户留存 Cohort 分析。

## 🙏 致谢
本项目复刻并参考了 TurboWay/bigdata_analyse 的 Hive 实现思路与分析维度，特此致谢。
感谢阿里巴巴天池提供高质量的开源数据集。