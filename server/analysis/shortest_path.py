'''
@zyh 2024/12/17
计算最短路径
'''
import networkx as nx
from config.database import Database
import json

class ShortestPath:
    def __init__(self):
        print("[INFO] 初始化 ShortestPath...")
        self.G = nx.Graph()
        self.db = Database()
        self.roads_data = None
        
    def build_network(self, roads_data):
        """
        根据道路数据构建网络
        roads_data: 从数据库查询的道路数据列表
        """
        print("[INFO] 开始构建路网...")
        edge_count = 0
        
        for road in roads_data:
            # 解析geometry (此时已经是字符串)
            geom = road['geometry']
            if isinstance(geom, str):
                geom = json.loads(geom)
                
            if geom['type'] != 'MultiLineString':
                continue
                
            # 获取道路属性
            props = road['properties']
            
            # 遍历每条线段的坐标
            for line_coords in geom['coordinates']:
                # 添加边,使用坐标作为节点
                for i in range(len(line_coords)-1):
                    # 将坐标转换为浮点数元组
                    start = tuple(map(float, line_coords[i]))
                    end = tuple(map(float, line_coords[i+1]))
                    
                    # 计算该段路的长度作为权重
                    weight = self._calc_distance(start, end)
                    
                    # 添加边,附带道路属性
                    self.G.add_edge(start, end, 
                                  weight=weight,
                                  road_props=props)
                    edge_count += 1

        print(f"[INFO] 路网构建完成: {len(self.G.nodes())} 个节点, {edge_count} 条边")
    
    def _calc_distance(self, point1, point2):
        """
        计算两点间的欧氏距离
        point1, point2: 包含浮点数的坐标元组
        """
        return ((point1[0]-point2[0])**2 + 
                (point1[1]-point2[1])**2)**0.5
    
    def _find_nearest_node(self, point):
        """
        找到离给定点最近的图中节点
        point: (lon, lat)元组
        """
        if not self.G.nodes():
            print("[ERROR] 路网为空")
            return None
            
        min_dist = float('inf')
        nearest = None
        
        # 设置搜索范围(约1公里)
        search_radius = 0.01  # 经纬度差值
        
        # 只搜索附近的节点
        for node in self.G.nodes():
            # 快速过滤远处节点
            if (abs(node[0] - point[0]) > search_radius or 
                abs(node[1] - point[1]) > search_radius):
                continue
                
            dist = self._calc_distance(point, node)
            if dist < min_dist:
                min_dist = dist
                nearest = node
        
        if nearest is None:
            print(f"[WARNING] 在 {point} 附近未找到路网节点")
        else:
            print(f"[INFO] 找到最近节点: {nearest}, 距离: {min_dist}")
            
        return nearest
    
    def get_shortest_path(self, start_point, end_point):
        """
        计算最短路径
        start_point: (lon, lat)起点坐标元组
        end_point: (lon, lat)终点坐标元组
        返回: GeoJSON格式的路径
        """
        try:
            print(f"[INFO] 计算从 {start_point} 到 {end_point} 的最短路径")
            
            # 确保输入坐标是浮点数
            start_point = tuple(map(float, start_point))
            end_point = tuple(map(float, end_point))
            
            # 找到最近的网络节点
            start_node = self._find_nearest_node(start_point)
            end_node = self._find_nearest_node(end_point)
            
            if start_node is None or end_node is None:
                print("[ERROR] 无法找到最近的路网节点")
                return None
                
            if start_node == end_node:
                print("[WARNING] 起点和终点映射到了同一个节点")
                return self._create_path_geojson([start_node])
            
            # 使用Dijkstra算法计算最短路径
            try:
                path = nx.shortest_path(self.G, 
                                      start_node, 
                                      end_node,
                                      weight='weight')
                print(f"[INFO] 找到路径, 包含 {len(path)} 个节点")
                return self._create_path_geojson(path)
                
            except nx.NetworkXNoPath:
                print(f"[ERROR] 找不到从 {start_node} 到 {end_node} 的路径")
                return None
            
        except Exception as e:
            print(f"[ERROR] 计算最短路径失败: {str(e)}")
            return None
            
    def _create_path_geojson(self, path):
        """创建路径的GeoJSON"""
        return {
            "type": "Feature",
            "geometry": {
                "type": "LineString",
                "coordinates": [list(node) for node in path]
            },
            "properties": {
                "length": self._calc_path_length(path)
            }
        }
    
    def _calc_path_length(self, path):
        """计算路径总长度"""
        length = 0
        for i in range(len(path)-1):
            length += self._calc_distance(path[i], path[i+1])
        return length

    def load_roads(self, db=None):
        """
        从数据库加载路网数据
        db: Database实例(可选),如果不传入则使用self.db
        """
        try:
            # 使用传入的db或默认的self.db
            db = db or self.db
            rows = db.fetch_roads()
            
            # 直接构建路网,不需要额外的转换
            self.build_network(rows)
            print("[INFO] 路网数据加载成功")
            return True
            
        except Exception as e:
            print(f"[ERROR] 加载路网数据失败: {str(e)}")
            return False

