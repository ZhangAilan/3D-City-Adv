'''
@zyh 2024-11-16
导入geojson数据
'''

import psycopg2
import json
import os
from pathlib import Path

def create_table():
    """创建geojson表"""
    conn = None
    try:
        conn = psycopg2.connect(
            dbname="adv",
            user="postgres",
            password="123",
            host="localhost",
            port="5432"
        )
        cursor = conn.cursor()
        
        # 删除已存在的表
        cursor.execute("DROP TABLE IF EXISTS geojson;")
        
        # 创建扩展（如果不存在）
        cursor.execute("CREATE EXTENSION IF NOT EXISTS postgis;")
        
        # 修改表定义，将GEOMETRY类型改为支持MultiPolygon
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS geojson (
            id SERIAL PRIMARY KEY,
            height NUMERIC,
            geometry GEOMETRY(MULTIPOLYGON, 4326),
            properties JSONB
        );
        """
        cursor.execute(create_table_sql)
        
        conn.commit()
        print("表创建成功！")
        
    except psycopg2.Error as e:
        print(f"创建表时出错: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

def import_geojson(file_path):
    """导入GeoJSON数据"""
    conn = None
    try:
        # 读取GeoJSON文件
        with open(file_path, 'r', encoding='utf-8') as f:
            geojson_data = json.load(f)
        
        conn = psycopg2.connect(
            dbname="adv",
            user="postgres",
            password="123",
            host="localhost",
            port="5432"
        )
        cursor = conn.cursor()
        
        # 清空现有数据
        cursor.execute("TRUNCATE TABLE geojson;")
        
        # 插入数据
        for feature in geojson_data['features']:
            geometry = json.dumps(feature['geometry'])
            properties = json.dumps(feature['properties'])
            height = feature['properties'].get('height', 0)
            
            insert_sql = """
            INSERT INTO geojson (height, geometry, properties)
            VALUES (%s, ST_SetSRID(ST_GeomFromGeoJSON(%s), 4326), %s::jsonb);
            """
            cursor.execute(insert_sql, (height, geometry, properties))
        
        conn.commit()
        print("数据导入成功！")
        
    except (psycopg2.Error, json.JSONDecodeError, FileNotFoundError) as e:
        print(f"导入数据时出错: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

def main():
    # 创建表
    create_table()
    
    # 设置GeoJSON文件路径
    current_dir = Path(__file__).parent
    geojson_path = current_dir / 'data' / 'beijing_building.geojson'
    
    # 导入数据
    if geojson_path.exists():
        import_geojson(str(geojson_path))
    else:
        print(f"找不到GeoJSON文件: {geojson_path}")

if __name__ == "__main__":
    main()

