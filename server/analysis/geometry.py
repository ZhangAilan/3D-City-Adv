'''
@zyh 2024-11-17
几何计算相关函数
'''

def calculate_exposure_area(billboard_center, direction_vector, d=0.01, alpha=3):
    '''
    计算广告牌曝光区域
    INPUT:
        billboard_center: 广告牌中心点，格式为 [x, y, z]
        direction_vector: 方向向量，格式为 [x, y]
        d: 距离(米)
        alpha: 角度
    OUTPUT:
        exposure_area: 曝光区域，格式为 [[x, y, r]]
    '''
    try:
        print("\n--- 计算曝光区域 ---")
        print(f"[INPUT] 广告牌中心点: {billboard_center}")
        print(f"[INPUT] 方向向量: {direction_vector}")
        
        import numpy as np
        exposure_area = []
        alpha = alpha*np.pi/180/3600
        
        # 先计算实际距离(米)
        distance_meters = d/(2*alpha)
        
        # 地球半径(米)
        R = 6371000
        # 1度对应的距离(米)
        meters_per_degree = 2 * np.pi * R / 360
        
        # 将距离从米转换为度来计算圆心位置
        distance_degree = distance_meters / meters_per_degree
        
        billboard_center_xy = billboard_center[:2]
        direction_vector = np.array(direction_vector)
        direction_vector = direction_vector / np.linalg.norm(direction_vector)
        circle_center = billboard_center_xy + distance_degree * direction_vector
        
        height = billboard_center[2]  # 高度单位为米
        radius = np.sqrt(distance_meters**2-height**2)  # 半径单位为米
        
        exposure_area.append([circle_center[0], circle_center[1], radius])
        
        print(f"[DEBUG] 计算参数:")
        print(f"  - 距离(米): {distance_meters:.6f}")
        print(f"  - 高度(米): {height:.6f}")
        print(f"  - 半径(米): {radius:.6f}")
        print(f"[SUCCESS] 曝光区域: {exposure_area}")
        
        return exposure_area
        
    except Exception as e:
        print("\n[ERROR] 曝光区域计算失败")
        print(f"[ERROR] 错误类型: {type(e).__name__}")
        print(f"[ERROR] 错误信息: {str(e)}")
        print(f"[ERROR] 位置: {e.__traceback__.tb_frame.f_code.co_filename}:{e.__traceback__.tb_lineno}")
        raise e

def calculate_billboard_direction(billboard_coords):
    '''
    计算广告牌方向，顺时针90度
    INPUT:
        billboard_coords: 广告牌坐标，格式为 [[x1, y1], [x2, y2]]
    OUTPUT:
        direction_vector: 方向向量，格式为 [x, y]
    '''
    try:
        print("\n--- 计算广告牌方向 ---")
        print(f"[INPUT] 广告牌坐标: {billboard_coords}")
        
        import numpy as np
        
        p1 = np.array(billboard_coords[0])
        p2 = np.array(billboard_coords[1])
        main_vector = p2 - p1
        
        # 计算顺时针90度的法向量
        direction_vector = np.array([main_vector[1], -main_vector[0]])
        # 单位化并缩小比例（避免坐标值过大）
        direction_vector = direction_vector / (np.linalg.norm(direction_vector) * 1000)
        
        print(f"[SUCCESS] 方向向量: {direction_vector}")
        
        return direction_vector.tolist()
        
    except Exception as e:
        print("\n[ERROR] 方向计算失败")
        print(f"[ERROR] 错误类型: {type(e).__name__}")
        print(f"[ERROR] 错误信息: {str(e)}")
        raise e

def create_circle_polygon(center, radius, num_points=64):
    """创建圆形多边形"""
    import math
    coordinates = []
    for i in range(num_points):
        angle = (i * 2 * math.pi) / num_points
        dx = radius * math.cos(angle)
        dy = radius * math.sin(angle)
        # 由于经纬度不是等距的，需要进行调整
        lat = center[1] + (dy / 111000)  # 1度纬度约等于111km
        lon = center[0] + (dx / (111000 * math.cos(math.radians(center[1]))))
        coordinates.append([lon, lat])
    coordinates.append(coordinates[0])  # 闭合多边形
    return coordinates

