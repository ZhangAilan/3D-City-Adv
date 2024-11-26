'''
@zyh 2024-11-26
将出租车csv数据导入到postgresql数据库
'''

import pandas as pd
import psycopg2
import logging
import time
from datetime import datetime
import os
from io import StringIO

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('gps_import.log'),
        logging.StreamHandler()
    ]
)

# 数据库连接参数
db_params = {
    'dbname': 'adv',
    'user': 'postgres',
    'password': '123',
    'host': 'localhost',
    'port': '5432'
}

try:
    logging.info("开始连接数据库...")
    conn = psycopg2.connect(**db_params)
    cursor = conn.cursor()
    logging.info("数据库连接成功")

    logging.info("创建GPS数据表...")
    # 创建gps数据表
    cursor.execute("""
    DROP TABLE IF EXISTS gps;  
    CREATE TABLE gps (
        taxi_id INTEGER,
        timestamp TIMESTAMP,
        longitude FLOAT,
        latitude FLOAT,
        geometry GEOMETRY(POINT, 4326),
        PRIMARY KEY (taxi_id, timestamp)
    );
    """)
    
    logging.info("创建空间索引...")
    cursor.execute("CREATE INDEX IF NOT EXISTS gps_geometry_idx ON gps USING GIST (geometry);")
    cursor.execute("CREATE INDEX IF NOT EXISTS gps_taxi_id_idx ON gps (taxi_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS gps_timestamp_idx ON gps (timestamp);")

    # 读取csv文件
    logging.info("开始读取CSV文件...")
    start_time = time.time()
    
    # 只读取需要的列，并去除重复记录
    df = pd.read_csv('data/taxi_GPS.csv', usecols=['taxi_id', 'timestamp', 'longitude', 'latitude'])
    original_count = len(df)
    df = df.drop_duplicates(subset=['taxi_id', 'timestamp'])  # 去除重复记录
    duplicate_count = original_count - len(df)
    logging.info(f"CSV文件读取完成，共 {original_count} 条记录，去除 {duplicate_count} 条重复记录，剩余 {len(df)} 条记录")

    logging.info("开始导入数据...")
    # 将DataFrame转换为内存中的CSV格式
    output = StringIO()
    df.to_csv(output, index=False, header=False)
    output.seek(0)
    
    # 使用StringIO对象导入数据
    cursor.copy_from(
        output,
        'gps',
        sep=',',
        columns=('taxi_id', 'timestamp', 'longitude', 'latitude')
    )
    
    # 更新几何字段
    logging.info("更新几何字段...")
    cursor.execute("""
    UPDATE gps 
    SET geometry = ST_SetSRID(ST_MakePoint(longitude, latitude), 4326)
    WHERE geometry IS NULL;
    """)
    
    conn.commit()
    end_time = time.time()
    logging.info(f"数据导入完成，耗时: {end_time - start_time:.2f} 秒")

except Exception as e:
    logging.error(f"发生错误: {str(e)}")
    conn.rollback()
    raise e

finally:
    if cursor:
        cursor.close()
    if conn:
        conn.close()
    logging.info("数据库连接已关闭")
