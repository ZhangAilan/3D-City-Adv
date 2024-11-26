'''
@zyh 2024/11/26
已知曝光区域的geojson数据和GPS数据
从中获取价值信息供前端分析
1.统计曝光区域内的出租车GPS信息
'''
from config.database import Database
import json

class GPSAnalyzer:
    def __init__(self):
        print("[INFO] 初始化 GPSAnalyzer...")
        self.db = Database()
        self.gps_data = None

    def load_gps_data(self):
        try:
            print("[INFO] 开始加载GPS数据...")
            self.gps_data = self.db.fetch_gps()
            print(f"[SUCCESS] 成功加载 {len(self.gps_data)} 条GPS数据")
            return True
        except Exception as e:
            print(f"[ERROR] 加载GPS数据失败: {str(e)}")
            return False

    #筛选出在曝光区域内的出租车GPS信息
    def filter_gps_in_exposure(self, exposure_geojson):
        try:
            print("\n=== 开始筛选曝光区域内的GPS数据 ===")
            
            # 确保exposure_geojson是有效的GeoJSON
            if exposure_geojson is None:
                print("[ERROR] 曝光区域数据为空")
                return []
                
            # 标准化GeoJSON格式
            if isinstance(exposure_geojson, dict):
                if 'type' not in exposure_geojson or 'features' not in exposure_geojson:
                    print("[ERROR] 无效的GeoJSON格式")
                    return []
                    
                # 提取MultiPolygon geometry
                try:
                    geometry = exposure_geojson['features'][0]['geometry']
                    if geometry['type'] != 'MultiPolygon':
                        print(f"[WARNING] 预期geometry类型为MultiPolygon，实际为{geometry['type']}")
                except (KeyError, IndexError) as e:
                    print(f"[ERROR] 无法提取geometry: {str(e)}")
                    return []
                    
                import json
                exposure_geojson = json.dumps(geometry)
            
            print(f"[DEBUG] 处理后的GeoJSON类型: {type(exposure_geojson)}")
            
            # 构建空间查询SQL
            print("[INFO] 构建空间查询SQL...")
            sql = """
                WITH exposure AS (
                    SELECT ST_GeomFromGeoJSON(%s) as geom
                )
                SELECT DISTINCT g.* 
                FROM gps g, exposure e
                WHERE ST_Intersects(g.geometry, e.geom)
            """
            
            # 执行查询
            print("[INFO] 执行空间查询...")
            conn = self.db.get_connection()
            try:
                with conn.cursor() as cur:
                    cur.execute(sql, (exposure_geojson,))
                    filtered_gps = cur.fetchall()
                    print(f"[SUCCESS] 查询完成,找到 {len(filtered_gps)} 条符合条件的GPS数据")
                    return filtered_gps
            finally:
                conn.close()
            
        except Exception as e:
            print(f"[ERROR] 筛选GPS数据失败: {str(e)}")
            import traceback
            print(traceback.format_exc())
            return []

    def generate_heatmap(self, cell_size=0.0001):
        """
        生成热力图数据,计算全部GPS点的密度分布
        @param cell_size: 网格大小(经纬度),默认0.0001度(约10米)
        @return: GeoJSON格式的热力图数据
        """
        try:
            print("[INFO] 开始生成热力图...")
            print(f"[INFO] 使用网格大小: {cell_size}度")
            
            # 使用ST_SnapToGrid进行网格化并计算每个网格的点密度
            sql = """
                WITH grid AS (
                    SELECT 
                        ST_SnapToGrid(geometry, %s, %s) as geom,
                        COUNT(*) as point_count
                    FROM gps
                    GROUP BY ST_SnapToGrid(geometry, %s, %s)
                )
                SELECT 
                    ST_AsGeoJSON(ST_Centroid(geom)) as centroid,
                    point_count,
                    ST_X(ST_Centroid(geom)) as longitude,
                    ST_Y(ST_Centroid(geom)) as latitude
                FROM grid
                WHERE point_count > 0
            """
            
            conn = self.db.get_connection()
            try:
                with conn.cursor() as cur:
                    cur.execute(sql, (cell_size, cell_size, cell_size, cell_size))
                    grid_data = cur.fetchall()
                    
                # 构建GeoJSON
                features = []
                for row in grid_data:
                    feature = {
                        "type": "Feature",
                        "geometry": json.loads(row[0]),
                        "properties": {
                            "weight": row[1],  # 点密度作为权重
                            "longitude": row[2],
                            "latitude": row[3]
                        }
                    }
                    features.append(feature)
                
                geojson = {
                    "type": "FeatureCollection",
                    "features": features
                }
                
                print(f"[SUCCESS] 热力图生成完成，共{len(features)}个网格")
                return geojson
                
            finally:
                conn.close()
                
        except Exception as e:
            print(f"[ERROR] 生成热力图失败: {str(e)}")
            import traceback
            print(traceback.format_exc())
            return None

