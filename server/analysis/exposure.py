'''
@zyh 2024-11-17
曝光分析主要计算逻辑
'''
from config.database import Database
from analysis.geometry import calculate_billboard_direction, calculate_exposure_area, create_circle_polygon,calculate_IA_arc,create_IA_polygon,filter_buildings_in_circle

import json
import numpy as np

class ExposureAnalyzer:
    def __init__(self):
        self.db = Database()
        self.buildings = None
    
    def load_buildings(self):
        """加载建筑物geojson数据"""
        try:
            rows = self.db.fetch_geojson()
            self.buildings = []
            for row in rows:
                geojson = json.loads(row['st_asgeojson'])  # 将GeoJSON字符串转换为Python字典
                properties = row['properties']
                feature = {
                    "type": "Feature",
                    "geometry": geojson,
                    "properties": properties
                }
                self.buildings.append(feature)
            return True
        except Exception as e:
            print(f"加载数据失败: {str(e)}")
            return False


    def calculate_GEA(self, billboards):
        """计算所有广告牌的GEA"""
        try:
            print("\n=== 开始计算曝光区域 ===")
            exposure_features = []
            
            for billboard in billboards:
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
                                    "radius": radius,
                                    "center": center,
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


    def calculate_IA(self, billboards,exposure_geojson):
        """计算所有广告牌的IA"""
        try:
            print("\n=== 开始计算遮挡区域 ===")
            occlusion_features = []
            #确保建筑物数据已加载
            if not self.buildings:
                print("[ERROR] 建筑物数据未加载")
                return None

            #建筑物geojson数据
            buildings_geojson = {
                "type": "FeatureCollection",
                "features": self.buildings
            }
            
            #遍历广告牌
            for billboard in billboards:
                if billboard.get('id') == 'billboards-3d':
                    features = billboard['data']['features']
                    print(f"\n[INFO] 正在处理 {len(features)} 个广告牌的遮挡区域...")
                    for i, feature in enumerate(features):
                        print(f"\n--- 广告牌 {i+1}/{len(features)} ---")
                        #获取广告牌信息
                        coords = feature['geometry']['coordinates'][0]
                        base_height = feature['properties']['base']
                        height = feature['properties']['height']
                        #计算广告牌中心点和高度
                        lons = [point[0] for point in coords]
                        lats = [point[1] for point in coords]
                        center_lon = sum(lons) / len(lons)
                        center_lat = sum(lats) / len(lats)
                        center_height = base_height + height/2
                        billboard_center = [center_lon, center_lat, center_height]
                        billboard_xy=billboard_center[:2]
                        
                        #获取对应的曝光区域
                        for exposure in exposure_geojson['features']:
                            if exposure['properties'].get('billboard_height',0) == center_height:  #根据高度相同筛选广告牌对应GEA
                                circle_center = exposure['properties'].get('center',[])
                                circle_radius = exposure['properties'].get('radius',0)
                                
                                #筛选范围内的建筑物
                                buildings_in_circle = filter_buildings_in_circle(buildings_geojson,circle_center, circle_radius)

                                #处理每个建筑物
                                for building in buildings_in_circle['features']:
                                    building_height = building['properties'].get('height',0)
                                    building_height=float(building_height)
                                    building_coords = building['geometry']['coordinates'][0][0]

                                    #根据高度关系决定遮挡类型
                                    if building_height > center_height:
                                        #建筑物高于广告牌，计算弧形遮挡
                                        occlusion_polygon=calculate_IA_arc(
                                            billboard_xy,
                                            building_coords,
                                            circle_center,
                                            circle_radius
                                        )
                                    else:
                                        #建筑物低于广告牌，计算投影遮挡
                                        occlusion_polygon=create_IA_polygon(
                                            billboard_center,
                                            building_coords,
                                            building_height
                                        )

                                    #添加遮挡多边形到结果中
                                    if occlusion_polygon:
                                        occlusion_features.append({
                                            "type": "Feature",
                                            "geometry": {
                                                "type": "Polygon",
                                                "coordinates": [occlusion_polygon]
                                            },
                                            "properties": {
                                                "type": "occlusion_area",
                                                "type_of_occlusion": "arc" if building_height > center_height else "projection"
                                            }
                                        })
            print(f"[SUCCESS] 成功生成 {len(occlusion_features)} 个遮挡区域")
            print("=== 计算完成 ===\n")
            return {
                "type": "FeatureCollection",
                "features": occlusion_features
            }
        except Exception as e:
            print("\n=== 错误信息 ===")
            print(f"[ERROR] 计算遮挡区域失败")
            print(f"[ERROR] 错误类型: {type(e).__name__}")
            print(f"[ERROR] 错误信息: {str(e)}")
            print(f"[ERROR] 位置: {e.__traceback__.tb_frame.f_code.co_filename}:{e.__traceback__.tb_lineno}")
            print("===============\n")
            return None


    def calculate_visible_area(self, exposure_geojson, occlusion_geojson):
        '''
        计算显示区域
        INPUT:
            exposure_geojson: 曝光区域的GeoJSON数据 (FeatureCollection)
            occlusion_geojson: 遮挡区域的GeoJSON数据 (FeatureCollection)
        OUTPUT:
            visible_area: 显示区域的GeoJSON数据 (FeatureCollection)
        '''
        try:
            print("\n--- 计算显示区域 ---")
            from shapely.geometry import shape, mapping
            from shapely.ops import unary_union
            
            # 验证并修复几何图形
            def validate_and_fix_geometry(geom):
                if not geom.is_valid:
                    print(f"[WARNING] 检测到无效几何图形，尝试修复...")
                    return geom.buffer(0)  # 使用buffer(0)修复几何图形
                return geom

            # 处理曝光区域
            exposure_shapes = [validate_and_fix_geometry(shape(feature['geometry'])) 
                             for feature in exposure_geojson['features']]
            exposure_union = validate_and_fix_geometry(unary_union(exposure_shapes))
            
            # 处理遮挡区域
            occlusion_shapes = [validate_and_fix_geometry(shape(feature['geometry'])) 
                              for feature in occlusion_geojson['features']]
            occlusion_union = validate_and_fix_geometry(unary_union(occlusion_shapes))
            
            # 计算交集和差集
            intersection = validate_and_fix_geometry(exposure_union.intersection(occlusion_union))
            visible_area = validate_and_fix_geometry(exposure_union.difference(intersection))
            
            # 转换结果为GeoJSON格式
            result_geojson = {
                "type": "FeatureCollection",
                "features": [{
                    "type": "Feature",
                    "geometry": mapping(visible_area),
                    "properties": {
                        "type": "visible_area"
                    }
                }]
            }
            
            print(f"[SUCCESS] 显示区域计算完成")
            return result_geojson
            
        except Exception as e:
            print("\n[ERROR] 显示区域计算失败")
            print(f"[ERROR] 错误类型: {type(e).__name__}")
            print(f"[ERROR] 错误信息: {str(e)}")
            print(f"[ERROR] 位置: {e.__traceback__.tb_frame.f_code.co_filename}:{e.__traceback__.tb_lineno}")
            raise e
