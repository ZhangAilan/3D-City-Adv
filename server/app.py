from flask import Flask,jsonify,request
from flask_cors import CORS  #跨域
from config.database import Database
from analysis.exposure import ExposureAnalyzer
import json

app = Flask(__name__)
CORS(app)

# 全局变量存储当前的广告牌数据
current_billboards = []

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

@app.route('/calculate-exposure', methods=['GET'])
def calculate_exposure():
    """计算所有广告牌的曝光区域"""
    try:
        # 初始化分析器并加载数据
        analyzer = ExposureAnalyzer()
        if not analyzer.load_data(current_billboards):
            return jsonify({
                "status": "error",
                "message": "加载数据失败"
            }), 500
            
        # 计算曝光区域
        exposure_geojson = analyzer.calculate_exposure_areas()
        if exposure_geojson is None:
            return jsonify({
                "status": "error",
                "message": "计算曝光区域失败"
            }), 500
            
        # 直接返回GeoJSON，不需要额外的data包装
        return jsonify(exposure_geojson)
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=3000)