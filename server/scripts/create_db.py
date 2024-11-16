'''
@zyh 2024-11-16
创建数据库
'''

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def create_database():
    try:
        # 连接到默认的postgres数据库
        conn = psycopg2.connect(
            dbname="postgres",
            user="postgres",
            password="123",  # 请根据实际情况修改密码
            host="localhost",
            port="5432"
        )
        
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # 检查数据库是否已存在
        cursor.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = 'adv'")
        exists = cursor.fetchone()
        
        if not exists:
            # 创建新数据库
            cursor.execute('CREATE DATABASE adv')
            print("数据库'adv'创建成功！")
        else:
            print("数据库'adv'已存在。")
            
    except psycopg2.Error as e:
        print(f"创建数据库时出错: {e}")
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    create_database()

