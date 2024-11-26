import psycopg2
from psycopg2.extras import RealDictCursor

class Database:
    def __init__(self):
        self.config = {
            "dbname": "adv",
            "user": "postgres",
            "password": "123",
            "host": "localhost",
            "port": "5432"
        }
    
    def get_connection(self):
        try:
            conn = psycopg2.connect(**self.config)
            return conn
        except Exception as e:
            print(f"数据库连接错误: {str(e)}")
            raise e
    
    def fetch_geojson(self):
        conn = self.get_connection()
        try:
            cur = conn.cursor(cursor_factory=RealDictCursor)
            cur.execute("SELECT ST_AsGeoJSON(geometry) as st_asgeojson, properties FROM geojson")
            results = cur.fetchall()
            return results
        except Exception as e:
            print(f"查询错误: {str(e)}")
            raise e
        finally:
            cur.close()
            conn.close()

    def fetch_gps(self):
        conn = self.get_connection()
        try:
            cur = conn.cursor(cursor_factory=RealDictCursor)
            cur.execute("SELECT * FROM gps")
            results = cur.fetchall()
            return results
        except Exception as e:
            print(f"查询错误: {str(e)}")
            raise e
        finally:
            cur.close()
            conn.close()