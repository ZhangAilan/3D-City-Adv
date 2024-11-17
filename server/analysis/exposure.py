'''
@zyh 2024-11-17
曝光分析主要计算逻辑
'''
from config.database import Database
from analysis.geometry import calculate_billboard_direction, calculate_exposure_area, create_circle_polygon
import json
import numpy as np

class ExposureAnalyzer:
    def __init__(self):
        self.db = Database()
        self.buildings = None
        self.billboards = None
    
    def load_data(self, billboards_data):
        """加载建筑物和广告牌数据"""
        try:
            rows = self.db.fetch_geojson()
            self.buildings = []
            for row in rows:
                geojson = json.loads(row['st_asgeojson'])
                properties = row['properties']
                feature = {
                    "type": "Feature",
                    "geometry": geojson,
                    "properties": properties
                }
                self.buildings.append(feature)
            self.billboards = billboards_data
            return True
        except Exception as e:
            print(f"加载数据失败: {str(e)}")
            return False
            
    def calculate_exposure_areas(self):
        """计算所有广告牌的曝光区域"""
        try:
            print("\n=== 开始计算曝光区域 ===")
            exposure_features = []
            buildings_geojson = {
                "type": "FeatureCollection",
                "features": self.buildings
            }
            print(f"[INFO] 加载了 {len(self.buildings)} 个建筑物数据")
            
            for billboard in self.billboards:
                if billboard.get('id') == 'billboards-3d':
                    features = billboard['data']['features']
                    print(f"\n[INFO] 正在处理 {len(features)} 个广告牌...")
                    
                    for i, feature in enumerate(features):
                        print(f"\n--- 广告牌 {i+1}/{len(features)} ---")
                        
                        # 获取广告牌坐标
                        coords = feature['geometry']['coordinates'][0]
                        billboard_coords = [coords[0], coords[1]]
                        print(f"[DEBUG] 广告牌坐标: {billboard_coords}")
                        
                        # 计算中心点和高度
                        lons = [point[0] for point in coords]
                        lats = [point[1] for point in coords]
                        center_lon = sum(lons) / len(lons)
                        center_lat = sum(lats) / len(lats)
                        base_height = feature['properties']['base']
                        height = feature['properties']['height']
                        center_height = base_height + height/2
                        print(f"[DEBUG] 中心点: ({center_lon}, {center_lat}), 高度: {center_height}")
                        
                        # 计算方向向量
                        try:
                            direction_vector = calculate_billboard_direction(
                                billboard_coords
                            )
                            print(f"[SUCCESS] 方向向量计算完成: {direction_vector}")
                        except Exception as e:
                            print(f"[ERROR] 方向向量计算失败: {str(e)}")
                            continue
                        
                        # 计算曝光区域
                        try:
                            billboard_center = [center_lon, center_lat, center_height]
                            exposure_area = calculate_exposure_area(
                                billboard_center, 
                                direction_vector
                            )
                            print(f"[SUCCESS] 曝光区域计算完成: {exposure_area}")
                        except Exception as e:
                            print(f"[ERROR] 曝光区域计算失败: {str(e)}")
                            continue
                        
                        # 添加到特征集合
                        for circle in exposure_area:
                            center = [circle[0], circle[1]]
                            radius = circle[2]
                            polygon_coords = create_circle_polygon(center, radius)
                            exposure_features.append({
                                "type": "Feature",
                                "geometry": {
                                    "type": "Polygon",
                                    "coordinates": [polygon_coords]  # 注意这里需要是嵌套数组
                                },
                                "properties": {
                                    "billboard_height": center_height,
                                    "type": "exposure_area"
                                }
                            })
            
            print(f"\n[SUCCESS] 成功生成 {len(exposure_features)} 个曝光区域")
            print("=== 计算完成 ===\n")
            return {
                "type": "FeatureCollection",
                "features": exposure_features
            }
            
        except Exception as e:
            print("\n=== 错误信息 ===")
            print(f"[ERROR] 计算曝光区域失败")
            print(f"[ERROR] 错误类型: {type(e).__name__}")
            print(f"[ERROR] 错误信息: {str(e)}")
            print(f"[ERROR] 位置: {e.__traceback__.tb_frame.f_code.co_filename}:{e.__traceback__.tb_lineno}")
            print("===============\n")
            return None
