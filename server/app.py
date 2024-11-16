from flask import Flask,jsonify,request
from flask_cors import CORS  #跨域
from config.database import Database
import json

app = Flask(__name__)
CORS(app)

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

# 全局变量存储当前的广告牌数据
current_billboards = []

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=3000)