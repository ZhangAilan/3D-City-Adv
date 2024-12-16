import psycopg2
from psycopg2.extras import RealDictCursor
import json
import os
import pandas as pd
from io import StringIO

class Database:
    def __init__(self):
        self.config = {
            "dbname": "adv",
            "user": "postgres",
            "password": "123",
            "host": "localhost",
            "port": "5432"
        }
        # 初始化所有表和数据
        self.init_database()
    
    def get_connection(self):
        try:
            conn = psycopg2.connect(**self.config)
            return conn
        except Exception as e:
            print(f"数据库连接错误: {str(e)}")
            raise e

    def init_database(self):
        """初始化数据库的所有表和数据"""
        # 创建扩展
        self.create_extensions()
        # 初始化各个表和数据
        self.init_geojson_data()
        self.init_gps_data()
        self.init_roads_data()
        print("数据库初始化完成")

    def create_extensions(self):
        """创建必要的PostgreSQL扩展"""
        conn = self.get_connection()
        try:
            cur = conn.cursor()
            cur.execute("CREATE EXTENSION IF NOT EXISTS postgis;")
            conn.commit()
        except Exception as e:
            print(f"创建扩展错误: {str(e)}")
            raise e
        finally:
            cur.close()
            conn.close()

    def init_geojson_data(self):
        """初始化geojson表和数据"""
        if self.check_table_has_data('geojson'):
            print("geojson表已存在且包含数据，跳过初始化")
            return

        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            
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

            # 读取GeoJSON文件
            geojson_path = os.path.join(os.path.dirname(__file__), 
                                  'db_data', 
                                  'beijing_building.geojson')
            with open(geojson_path, 'r', encoding='utf-8') as f:
                geojson_data = json.load(f)
            
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
            print("geojson数据导入成功！")

        except (psycopg2.Error, json.JSONDecodeError, FileNotFoundError) as e:
            print(f"导入数据时出错: {e}")
            if conn:
                conn.rollback()
        finally:
            if conn:
                conn.close()

    def init_gps_data(self):
        """初始化gps表和数据"""
        if self.check_table_has_data('gps'):
            print("gps表已存在且包含数据，跳过初始化")
            return

        conn = self.get_connection()
        try:
            cur = conn.cursor()
            # 创建gps表
            cur.execute("""
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
            
            # 创建索引
            cur.execute("CREATE INDEX IF NOT EXISTS gps_geometry_idx ON gps USING GIST (geometry);")
            cur.execute("CREATE INDEX IF NOT EXISTS gps_taxi_id_idx ON gps (taxi_id);")
            cur.execute("CREATE INDEX IF NOT EXISTS gps_timestamp_idx ON gps (timestamp);")
            
            conn.commit()
            
            # 读取并导入数据
            gps_path = os.path.join(os.path.dirname(__file__), 
                                  'db_data', 
                                  'taxi_GPS.csv')
            
            if not os.path.exists(gps_path):
                print(f"找不到GPS数据文件: {gps_path}")
                return
            
            # 读取CSV文件，只读取需要的列，并去除重复记录
            df = pd.read_csv(gps_path, 
                           usecols=['taxi_id', 'timestamp', 'longitude', 'latitude'])
            df = df.drop_duplicates(subset=['taxi_id', 'timestamp'])
            
            # 将DataFrame转换为内存中的CSV格式
            output = StringIO()
            df.to_csv(output, index=False, header=False)
            output.seek(0)
            
            # 使用COPY命令快速导入数据
            cur.copy_from(
                output,
                'gps',
                sep=',',
                columns=('taxi_id', 'timestamp', 'longitude', 'latitude')
            )
            
            # 更新几何字段
            cur.execute("""
                UPDATE gps 
                SET geometry = ST_SetSRID(ST_MakePoint(longitude, latitude), 4326)
                WHERE geometry IS NULL;
            """)
            
            conn.commit()
            print("gps数据初始化成功")
            
        except Exception as e:
            print(f"初始化gps表错误: {str(e)}")
            raise e
        finally:
            cur.close()
            conn.close()

    def check_table_has_data(self, table_name):
        """检查指定表是否存在且有数据"""
        conn = self.get_connection()
        try:
            cur = conn.cursor()
            # 检查表是否存在
            cur.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = %s
                );
            """, (table_name,))
            table_exists = cur.fetchone()[0]
            
            if not table_exists:
                return False
                
            # 检查表中是否有数据
            cur.execute(f"SELECT COUNT(*) FROM {table_name};")
            count = cur.fetchone()[0]
            return count > 0
        except Exception as e:
            print(f"检查{table_name}表错误: {str(e)}")
            return False
        finally:
            cur.close()
            conn.close()

    def create_roads_table(self):
        conn = self.get_connection()
        try:
            cur = conn.cursor()
            # 创建roads表，包含geometry和properties字段
            cur.execute("""
                CREATE TABLE IF NOT EXISTS roads (
                    id SERIAL PRIMARY KEY,
                    geometry geometry(MultiLineString, 4326),
                    properties JSONB
                );
            """)
            conn.commit()
        except Exception as e:
            print(f"创建roads表错误: {str(e)}")
            raise e
        finally:
            cur.close()
            conn.close()
    
    def import_roads_geojson(self, features):
        conn = self.get_connection()
        try:
            cur = conn.cursor()
            for feature in features:
                geometry = feature['geometry']
                properties = feature['properties']
                # 插入数据
                cur.execute("""
                    INSERT INTO roads (geometry, properties)
                    VALUES (ST_SetSRID(ST_GeomFromGeoJSON(%s), 4326), %s);
                """, (json.dumps(geometry), json.dumps(properties)))
            conn.commit()
        except Exception as e:
            print(f"导入roads数据错误: {str(e)}")
            raise e
        finally:
            cur.close()
            conn.close()

    def check_roads_table(self):
        """检查roads表是否存在且有数据"""
        conn = self.get_connection()
        try:
            cur = conn.cursor()
            # 检查表是否存在
            cur.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'roads'
                );
            """)
            table_exists = cur.fetchone()[0]
            
            if not table_exists:
                return False
                
            # 检查表中是否有数据
            cur.execute("SELECT COUNT(*) FROM roads;")
            count = cur.fetchone()[0]
            return count > 0
        except Exception as e:
            print(f"检查roads表错误: {str(e)}")
            return False
        finally:
            cur.close()
            conn.close()

    def init_roads_data(self):
        """初始化roads表和数据"""
        if self.check_roads_table():
            print("roads表已存在且包含数据，跳过初始化")
            return
            
        try:
            # 创建表
            self.create_roads_table()
            
            # 读取并导入数据
            import os
            geojson_path = os.path.join(os.path.dirname(__file__), 
                                      'db_data', 
                                      '东城区道路网.geojson')
            
            with open(geojson_path, 'r', encoding='utf-8') as f:
                geojson_data = json.load(f)
            
            if 'features' in geojson_data:
                self.import_roads_geojson(geojson_data['features'])
                print("roads数据初始化成功")
            else:
                print("GeoJSON文件格式错误")
                
        except Exception as e:
            print(f"初始化roads数据错误: {str(e)}")
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
            cur.execute("""
                SELECT taxi_id, timestamp, longitude, latitude, 
                       ST_AsGeoJSON(geometry) as geometry
                FROM gps
            """)
            results = cur.fetchall()
            return results
        except Exception as e:
            print(f"查询gps错误: {str(e)}")
            raise e
        finally:
            cur.close()
            conn.close()

    def fetch_roads(self):
        conn = self.get_connection()
        try:
            cur = conn.cursor(cursor_factory=RealDictCursor)
            cur.execute("""
                SELECT ST_AsGeoJSON(geometry) as geometry, properties 
                FROM roads
            """)
            results = cur.fetchall()
            return results
        except Exception as e:
            print(f"查询roads错误: {str(e)}")
            raise e
        finally:
            cur.close()
            conn.close()