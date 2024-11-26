from flask import Flask,jsonify,request
from flask_cors import CORS  #跨域
from config.database import Database
from analysis.exposure import ExposureAnalyzer
from analysis.gps_info import GPSAnalyzer
import json

app = Flask(__name__)
CORS(app)

# 全局变量存储当前的广告牌数据
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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=3000)