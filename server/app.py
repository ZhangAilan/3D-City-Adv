from flask import Flask,jsonify,request
from flask_cors import CORS  #跨域
from config.database import Database
from analysis.exposure import ExposureAnalyzer
from analysis.gps_info import GPSAnalyzer
from analysis.shortest_path import ShortestPath
import json
import psycopg2

app = Flask(__name__)
CORS(app)

# 全局变量存储当前的广告牌数据
current_markers=[]
current_billboards = []
current_GEA = []
current_IA = []
current_VA = []

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/geojson')
def get_geojson():
    try:
        db = Database()
        rows = db.fetch_geojson()        
        features = []
        for row in rows:
            geojson = json.loads(row['st_asgeojson'])
            properties = row['properties']
            
            feature = {
                "type": "Feature",
                "geometry": geojson,
                "properties": properties
            }
            features.append(feature)        
        geojson_collection = {
            "type": "FeatureCollection",
            "features": features
        }   
        return jsonify(geojson_collection)      
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/markers', methods=['POST'])
def save_markers():
    try:
        markers_data = request.json.get('features', [])
        print("[INFO] 接收到的标记点数据:", markers_data)
        
        # 提取坐标数据
        global current_markers
        current_markers = []
        for marker in markers_data:
            if isinstance(marker, list) and len(marker) == 2:
                # 如果已经是[lon, lat]格式
                coords = marker
            elif isinstance(marker, dict):
                # 如果是GeoJSON格式
                coords = marker.get('geometry', {}).get('coordinates', [])
            else:
                continue
                
            if len(coords) == 2:
                current_markers.append(coords)
        
        print("[INFO] 当前保存的标记点坐标:", current_markers)
        
        return jsonify({
            "status": "success",
            "message": f"成功保存 {len(current_markers)} 个标记点数据",
            "count": len(current_markers)
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/save-billboards', methods=['POST'])
def save_billboards():
    try:
        billboards_data = request.json.get('billboards', [])
        global current_billboards
        current_billboards = billboards_data
        print("当前保存的广告牌数据:", current_billboards)  # 直接打印保存的数据     
        return jsonify({
            "status": "success",
            "message": f"成功保存 {len(billboards_data)} 个广告牌数据",
            "count": len(billboards_data)
        })        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route('/GEA', methods=['GET'])
def calculate_GEA():
    """计算所有广告牌的曝光区域"""
    try:
        # 初始化分析器并加载建筑物数据
        analyzer = ExposureAnalyzer()
        if not analyzer.load_buildings():
            return jsonify({
                "status": "error",
                "message": "加载数据失败"
            }), 500
            
        # 计算曝光区域
        exposure_geojson = analyzer.calculate_GEA(current_billboards)
        if exposure_geojson is None:
            return jsonify({
                "status": "error",
                "message": "计算曝光区域失败"
            }), 500
        global current_GEA
        current_GEA = exposure_geojson  # 保存计算结果
        # 直接返回GeoJSON，不需要额外的data包装
        return jsonify(exposure_geojson)
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/IA', methods=['GET'])
def calculate_IA():
    """计算所有广告牌的遮挡区域"""
    try:
        analyzer = ExposureAnalyzer()
        if not analyzer.load_buildings():
            return jsonify({
                "status": "error",
                "message": "加载数据失败"
            }), 500
        #计算遮挡区域
        occlusion_geojson = analyzer.calculate_IA(current_billboards,current_GEA)
        global current_IA
        current_IA = occlusion_geojson  # 保存计算结果
        if occlusion_geojson is None:
            return jsonify({
                "status": "error",
                "message": "计算遮挡区域失败"
            }), 500
        return jsonify(occlusion_geojson)
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/VA', methods=['GET'])
def calculate_VA():
    """计算所有广告牌的显示区域"""
    try:    
        analyzer = ExposureAnalyzer()
        visible_area_geojson = analyzer.calculate_visible_area(current_GEA, current_IA)
        global current_VA
        current_VA = visible_area_geojson  # 保存计算结果
        if visible_area_geojson is None:
            return jsonify({
                "status": "error",
                "message": "计算显示区域失败"
            }), 500
        return jsonify(visible_area_geojson)
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/gps-info', methods=['GET'])
def get_gps_info():
    """获取曝光区域内的出租车GPS信息"""
    try:
        print("开始获取GPS信息...")
        analyzer = GPSAnalyzer()
        #加载GPS数据
        if not analyzer.load_gps_data():
            return jsonify({
                "status": "error",
                "message": "加载GPS数据失败"
            }), 500
        #曝光区域
        gps_data = analyzer.filter_gps_in_exposure(current_VA)
        
        if gps_data is None:
            print("GPS数据为空")
            return jsonify({
                "status": "error",
                "message": "获取GPS信息失败"
            }), 500
        return jsonify(gps_data)
    except Exception as e:
        print(f"获取GPS信息时发生错误: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/heatmap', methods=['GET'])
def get_heatmap():
    """获取热力图"""
    try:    
        print("开始获取热力图...")
        analyzer = GPSAnalyzer()
        if not analyzer.load_gps_data():
            return jsonify({
                "status": "error",
                "message": "加载GPS数据失败"
            }), 500
        heatmap_data = analyzer.generate_heatmap()
        if heatmap_data is None:
            return jsonify({
                "status": "error",
                "message": "获取热力图失败"
            }), 500
        return jsonify(heatmap_data)
    except Exception as e:
        print(f"获取热力图时发生错误: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
    
@app.route('/shortest-path', methods=['GET'])
def get_shortest_path():
    """获取最短路径"""
    try:
        # 确保至少有两个标记点
        if len(current_markers) < 2:
            return jsonify({
                "status": "error",
                "message": "需要至少两个标记点来计算路径"
            }), 400
            
        # 获取最新的两个标记点的坐标
        # 假设标记点数据格式为 [lon, lat]
        end_coords = current_markers[-1]
        start_coords = current_markers[-2]
        
        if not isinstance(end_coords, list) or not isinstance(start_coords, list):
            return jsonify({
                "status": "error",
                "message": "标记点格式错误"
            }), 400
            
        print(f"[INFO] 起点坐标: {start_coords}, 终点坐标: {end_coords}")
        
        # 初始化并加载路网
        sp = ShortestPath()
        if not sp.load_roads(sp.db):
            return jsonify({
                "status": "error",
                "message": "加载路网数据失败"
            }), 500
            
        # 计算最短路径
        path = sp.get_shortest_path(start_coords, end_coords)
        if path is None:
            return jsonify({
                "status": "error",
                "message": "找不到可行的路径"
            }), 404
            
        return jsonify({
            "status": "success",
            "data": path
        })
        
    except Exception as e:
        print(f"[ERROR] 路径计算失败: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/poi/categories', methods=['GET'])
def get_poi_categories():
    """获取所有POI类别"""
    try:
        db = Database()
        cur = db.get_connection().cursor()
        cur.execute("SELECT DISTINCT category FROM poi WHERE category IS NOT NULL ORDER BY category;")
        categories = [row[0] for row in cur.fetchall()]
        return jsonify({
            "status": "success",
            "data": categories
        })
    except Exception as e:
        print(f"[ERROR] 获取POI类别失败: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/poi/<category>', methods=['GET'])
def get_poi_by_category(category):
    """根据类别获取POI数据"""
    try:
        db = Database()
        conn = db.get_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        # 查询特定类别的POI数据
        cur.execute("""
            SELECT 
                name,
                category,
                ST_AsGeoJSON(geometry) as geometry,
                properties
            FROM poi 
            WHERE category = %s;
        """, (category,))
        
        rows = cur.fetchall()
        
        # 构建GeoJSON格式的响应
        features = []
        for row in rows:
            geometry = json.loads(row['geometry'])
            feature = {
                "type": "Feature",
                "geometry": geometry,
                "properties": {
                    "name": row['name'],
                    "category": row['category'],
                    **row['properties']
                }
            }
            features.append(feature)
            
        geojson = {
            "type": "FeatureCollection",
            "features": features
        }
        
        return jsonify(geojson)
        
    except Exception as e:
        print(f"[ERROR] 获取{category}类别的POI数据失败: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

@app.route('/regions', methods=['GET'])
def get_regions():
    """获取所有区域数据"""
    try:
        db = Database()
        conn = db.get_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        # 查询region表中的所有数据
        cur.execute("""
            SELECT 
                name,
                ST_AsGeoJSON(geometry) as geometry,
                properties
            FROM region;
        """)
        
        rows = cur.fetchall()
        
        # 构建GeoJSON格式的响应
        features = []
        for row in rows:
            geometry = json.loads(row['geometry'])
            feature = {
                "type": "Feature",
                "geometry": geometry,
                "properties": {
                    "name": row['name'],
                    **row['properties']
                }
            }
            features.append(feature)
            
        geojson = {
            "type": "FeatureCollection",
            "features": features
        }
        
        return jsonify(geojson)
        
    except Exception as e:
        print(f"[ERROR] 获取区域数据失败: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=3000)