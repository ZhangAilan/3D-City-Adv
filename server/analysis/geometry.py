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
        billboard_coords: 广告牌坐标，格式为 [[lon1, lat1], [lon2, lat2]]
        注意：第一个值是经度，第二个值是纬度
    OUTPUT:
        direction_vector: 方向向量，格式为 [x, y]
    '''
    try:
        print("\n--- 计算广告牌方向 ---")
        print(f"[INPUT] 广告牌坐标: {billboard_coords}")
        
        import numpy as np
        
        # 提取坐标点
        lon1, lat1 = billboard_coords[0]
        lon2, lat2 = billboard_coords[1]
        
        # 转换为弧度
        lat1 = np.radians(lat1)
        lon1 = np.radians(lon1)
        lat2 = np.radians(lat2)
        lon2 = np.radians(lon2)
        
        # 计算广告牌的方向角（方位角）
        dlon = lon2 - lon1
        y = np.sin(dlon) * np.cos(lat2)
        x = np.cos(lat1) * np.sin(lat2) - np.sin(lat1) * np.cos(lat2) * np.cos(dlon)
        bearing = np.arctan2(y, x)
        
        # 将方向角转换为顺时针90度的方向
        bearing = bearing + np.pi/2
        
        # 计算方向向量
        direction_vector = np.array([np.sin(bearing), np.cos(bearing)])
        
        # 缩小比例（可选）
        direction_vector = direction_vector / 1000
        
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


def haversine_distance(lon1, lat1, lon2, lat2):
    """
    计算两个经纬度点之间的距离(单位:米)
    使用 Haversine 公式计算球面两点间的距离
    """
    import math
    R = 6371000  # 地球平均半径(米)
    
    # 将经纬度转换为弧度
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # haversine 公式
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    return R * c


def filter_buildings_in_circle(geojson_data,circle_center,circle_radius):
    """
    筛选圆形范围内的建筑物
    
    参数:
    geojson_data: GeoJSON 数据字典
    circle_center: 圆心坐标，格式为 [lon, lat]
    circle_radius: 圆形半径(米)
    
    返回:
    包含在圆形范围内建筑物的新 GeoJSON 数据
    """
    print(f"\n[INFO] 开始筛选圆形范围内的建筑物")
    print(f"[DEBUG] 圆心坐标: {circle_center}")
    print(f"[DEBUG] 圆形半径: {circle_radius}米")
    
    # 创建结果 GeoJSON
    result = {
        "type": "FeatureCollection",
        "features": []
    }
    
    # 遍历所有建筑物
    total_buildings = len(geojson_data["features"])
    print(f"[INFO] 共有 {total_buildings} 个建筑物待检查")
    
    for i, feature in enumerate(geojson_data["features"]):
        # 获取建筑物的几何数据
        geometry = feature["geometry"]
        coordinates = geometry["coordinates"]
        
        # 对于 MultiPolygon 类型,检查任意一个点是否在圆内
        is_in_circle = False
        
        for polygon in coordinates:
            for ring in polygon:
                for point in ring:
                    lon, lat = point  # GeoJSON 中经度在前,纬度在后
                    distance = haversine_distance(circle_center[0], circle_center[1], lon, lat)
                    if distance <= circle_radius:
                        is_in_circle = True
                        break
                if is_in_circle:
                    break
            if is_in_circle:
                break
                
        # 如果建筑物在圆内,添加到结果中
        if is_in_circle:
            result["features"].append(feature)
    
    print(f"[SUCCESS] 筛选完成,共找到 {len(result['features'])} 个圆内建筑物")
    return result


def calculate_ground_intersection(billboard_pos,building_vertex,height):
    '''
    计算广告牌视线经过建筑物顶点与地面的交点
    INPUT:
        billboard_pos: 广告牌位置，格式为 [x, y, z]
        building_vertex: 建筑物顶点，格式为 [x,y]
        height: 建筑物高度
    OUTPUT:
        ground_point: 地面交点，格式为 [x, y]
    '''
    try:
        #广告牌坐标
        x1,y1,z1 = billboard_pos
        #建筑物顶点坐标
        x2,y2 = building_vertex
        z2 = height
        if z1 == z2:
            z2=z2-1  # 防止建筑物顶点在广告牌正下方,导致视线与建筑物顶点重合
        #参数方程：P(t) = P1 + t*(P2-P1)
        #当z=0时求解t
        t = -z1/(z2-z1)
        #地面交点坐标
        x = x1 + t*(x2-x1)
        y = y1 + t*(y2-y1)
        return [x,y]
    except Exception as e:
        print("\n[ERROR] 地面交点计算失败")
        print(f"[ERROR] 错误类型: {type(e).__name__}")
        print(f"[ERROR] 错误信息: {str(e)}")
        raise e


def create_IA_polygon(billboard_pos, building_vertices, height):
    '''
    创建广告牌视线经过建筑物顶点与地面的交点构成的多边形
    INPUT:
        billboard_pos: 广告牌位置，格式为 [x, y, z]
        building_vertices: 建筑物顶点，格式为 [[x,y],[x,y],[x,y]]
        height: 建筑物高度
    OUTPUT:
        occlusion_polygon: 遮挡多边形，格式为 [[x,y],[x,y],[x,y]]
    '''
    try:
        import numpy as np
        
        # 计算所有地面交点
        points_data = []
        billboard_xy = np.array(billboard_pos[:2])
        
        for vertex in building_vertices:
            ground_point = calculate_ground_intersection(billboard_pos, vertex, height)
            
            # 计算从广告牌到顶点和地面点的向量
            vertex_vector = np.array(vertex) - billboard_xy
            ground_vector = np.array(ground_point) - billboard_xy
            
            # 计算向量的角度（相对于x轴正方向）
            vertex_angle = np.arctan2(vertex_vector[1], vertex_vector[0])
            ground_angle = np.arctan2(ground_vector[1], ground_vector[0])
            
            points_data.append({
                'vertex': vertex,
                'ground_point': ground_point,
                'vertex_angle': vertex_angle,
                'ground_angle': ground_angle
            })
        
        # 按角度排序
        points_data.sort(key=lambda x: x['ground_angle'])
        
        # 构建多边形
        polygon_coords = []
        
        # 添加所有地面点
        for point_data in points_data:
            polygon_coords.append(point_data['ground_point'])
        
        # 添加所有建筑物顶点（按角度逆序）
        for point_data in sorted(points_data, key=lambda x: x['vertex_angle'], reverse=True):
            polygon_coords.append(point_data['vertex'])
            
        # 闭合多边形
        polygon_coords.append(polygon_coords[0])
        
        return polygon_coords
        
    except Exception as e:
        print("\n[ERROR] 遮挡多边形创建失败")
        print(f"[ERROR] 错误类型: {type(e).__name__}")
        print(f"[ERROR] 错误信息: {str(e)}")
        return None
    

def calculate_IA_arc(billboard_pos, building_points, circle_center, circle_radius):
    '''
    计算圆弧形遮挡区域
    INPUT:
        billboard_pos: 广告牌位置，格式为 [lon, lat]
        building_points: 建筑物顶点，格式为 [[lon,lat],[lon,lat],...]
        circle_center: 圆心坐标，格式为 [lon, lat]
        circle_radius: 圆形半径(米)
    OUTPUT:
        occlusion_polygon: 遮挡多边形，格式为 [[lon,lat],[lon,lat],...]
    '''
    import numpy as np
    try:
        def get_point_at_distance(center_lon, center_lat, angle, distance):
            """
            从中心点出发，给定角度和距离(米)，计算目标点的经纬度
            angle: 弧度，相对于正东方向
            """
            # 纬度方向上1度对应的距离约为111000米
            # 经度方向上1度对应的距离需要根据纬度进行调整
            lat_offset = (distance * np.sin(angle)) / 111000
            lon_offset = (distance * np.cos(angle)) / (111000 * np.cos(np.radians(center_lat)))
            return [center_lon + lon_offset, center_lat + lat_offset]

        arc_points = []
        # 计算每个建筑物点对应的射线与圆的交点
        for building_point in building_points:
            # 计算广告牌到建筑物点的方向角度
            dx = haversine_distance(billboard_pos[0], billboard_pos[1], 
                                  building_point[0], billboard_pos[1])
            dy = haversine_distance(billboard_pos[0], billboard_pos[1], 
                                  billboard_pos[0], building_point[1])
            if building_point[0] < billboard_pos[0]:
                dx = -dx
            if building_point[1] < billboard_pos[1]:
                dy = -dy
            angle = np.arctan2(dy, dx)

            # 计算广告牌到圆心的距离
            distance_to_center = haversine_distance(billboard_pos[0], billboard_pos[1],
                                                  circle_center[0], circle_center[1])
            
            # 计算广告牌到圆心的方向角度
            dx_center = haversine_distance(billboard_pos[0], billboard_pos[1], 
                                         circle_center[0], billboard_pos[1])
            dy_center = haversine_distance(billboard_pos[0], billboard_pos[1], 
                                         billboard_pos[0], circle_center[1])
            if circle_center[0] < billboard_pos[0]:
                dx_center = -dx_center
            if circle_center[1] < billboard_pos[1]:
                dy_center = -dy_center
            angle_to_center = np.arctan2(dy_center, dx_center)

            # 计算射线与圆的交点
            theta = angle - angle_to_center
            d = distance_to_center * np.sin(theta)
            
            # 如果射线与圆相交
            if abs(d) <= circle_radius:
                # 计算交点到圆心的距离
                l = np.sqrt(circle_radius**2 - d**2)
                # 计算交点
                intersection_point = get_point_at_distance(
                    circle_center[0], circle_center[1],
                    angle,
                    circle_radius
                )
                arc_points.append({
                    'point': intersection_point,
                    'building_point': building_point,
                    'angle': angle
                })

        if len(arc_points) >= 2:
            # 按角度排序
            arc_points.sort(key=lambda x: x['angle'])
            
            # 构建多边形
            occlusion_polygon = []
            
            # 1. 添加第一个建筑点
            occlusion_polygon.append(arc_points[0]['building_point'])
            
            # 2. 添加圆弧上的点
            start_angle = arc_points[0]['angle']
            end_angle = arc_points[-1]['angle']
            if end_angle < start_angle:
                end_angle += 2*np.pi
                
            num_points = 32
            for i in range(num_points + 1):
                angle = start_angle + i*(end_angle-start_angle)/num_points
                point = get_point_at_distance(
                    circle_center[0], circle_center[1],
                    angle,
                    circle_radius
                )
                occlusion_polygon.append(point)
            
            # 3. 添加最后一个建筑点
            occlusion_polygon.append(arc_points[-1]['building_point'])
            
            # 4. 闭合多边形
            occlusion_polygon.append(occlusion_polygon[0])
            
            return occlusion_polygon
            
        return None
        
    except Exception as e:
        print("\n[ERROR] 圆弧形遮挡区域计算失败")
        print(f"[ERROR] 错误类型: {type(e).__name__}")
        print(f"[ERROR] 错误信息: {str(e)}")
        print(f"[ERROR] 位置: {e.__traceback__.tb_frame.f_code.co_filename}:{e.__traceback__.tb_lineno}")
        return None

