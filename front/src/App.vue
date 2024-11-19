<!-- App.vue -->
<template>
  <div id="app">
    <div id='map'></div>
    <FloatWindow title="3D城市广告牌曝光分析系统" class="analysis-window">
      <div class="control-panel">
        <div class="drawing-controls">
          <button class="primary-btn" @click="fetchGeojsonFromBackend">
            加载3D建筑
          </button>
          <button class="action-btn" :class="{ active: isDrawing }" @click="toggleDrawing">
            {{ isDrawing ? '停止绘制' : '开始绘制' }}
          </button>
          <button class="action-btn delete" @click="clearLastBillboard">
            清除上一个广告牌
          </button>
        </div>

        <div class="slider-group">
          <div class="slider-container">
            <div class="slider-header">
              <label>广告牌高度</label>
              <span class="value">{{ billboardHeight }}m</span>
            </div>
            <input type="range" v-model.number="billboardHeight" @input="updateBillboardDimensions" min="0" max="100"
              step="1" class="slider" />
          </div>

          <div class="slider-container">
            <div class="slider-header">
              <label>距地面高度</label>
              <span class="value">{{ groundHeight }}m</span>
            </div>
            <input type="range" v-model.number="groundHeight" @input="updateBillboardDimensions" min="0" max="100"
              step="1" class="slider" />
          </div>
        </div>
      </div>

      <div class="analysis-buttons">
        <h3>分析功能</h3>
        <div class="button-group">
          <button class="analysis-btn" @click="handleExposureAnalysis">
            曝光分析
          </button>
          <button class="analysis-btn" @click="handleOcclusionAnalysis">
            遮挡分析
          </button>
          <button class="analysis-btn" @click="handleVisibleAreaAnalysis">
            可见区域分析
          </button>
          <button class="analysis-btn clear" @click="clearAnalysisLayers">
            清除分析图层
          </button>
        </div>
      </div>
    </FloatWindow>
  </div>
</template>

<script>
import mapboxgl from "mapbox-gl";
import FloatWindow from "./components/FloatWindow.vue";
import DrawBoard from '@/utils/DrawBoard.js';
import ExposureAnalysis from '@/utils/ExposureAnalysis.js';
import MapLayerManager from '@/utils/MapLayer.js';
export default {
  name: "App",
  components: {
    FloatWindow,
  },
  data() {
    return {
      map: null,
      isDrawing: false,
      billboardHeight: 30,
      groundHeight: 50,
      drawLine: null,
      exposureAnalysis: null,
      mapLayerManager: null,
    };
  },

  mounted() {
    mapboxgl.accessToken = 'pk.eyJ1IjoiYWlsYW56aGFuZyIsImEiOiJjbTMycjh3b28xMXg0MmlwcHd2ZmttZWYyIn0.T42ZxSkFvc05u3vfMT6Paw';
    this.map = new mapboxgl.Map({
      container: 'map',
      style: 'mapbox://styles/mapbox/light-v11',
      center: { lng: 116.4170, lat: 39.9288 },  //北京东城区
      zoom: 15.4,           //缩放级别
      pitch: 69,          // 倾斜角度
      bearing: 15,        // 旋转角度
      antialias: true
    });

    //初始化DrawLine实例
    this.drawboard = new DrawBoard(this.map, this.billboardHeight, this.groundHeight);  //初始化绘制广告牌实例

    //初始化曝光分析实例
    this.exposureAnalysis = new ExposureAnalysis(this.map);

    //初始化地图图层管理实例
    this.mapLayerManager = new MapLayerManager(this.map);
  },

  methods: {
    // 从后端获取GeoJSON数据
    async fetchGeojsonFromBackend() {
      try {
        // 如果已经存在建筑物图层，先移除
        if (this.map.getLayer('3d-buildings')) {
          this.map.removeLayer('3d-buildings');
        }
        if (this.map.getSource('buildings')) {
          this.map.removeSource('buildings');
        }
        const response = await fetch('http://localhost:3000/geojson');
        const data = await response.json();
        console.log("从后端获取的GeoJSON数据:", data);
        // 添加数据源
        this.map.addSource('buildings', {
          'type': 'geojson',
          'data': data
        });
        // 添加3D建筑层
        this.map.addLayer({
          'id': '3d-buildings',
          'type': 'fill-extrusion',
          'source': 'buildings',
          'paint': {
            'fill-extrusion-color': '#000',  //色填充
            'fill-extrusion-height': ['to-number', ['get', 'height']],
            'fill-extrusion-base': 0,
            'fill-extrusion-opacity': 0.9
          }
        });
      } catch (error) {
        console.error("加载GeoJSON数据失败:", error);
      }
    },

    // 开始/停止绘制
    toggleDrawing() {
      this.isDrawing = !this.isDrawing;
      if (this.isDrawing) {
        this.drawboard.startDrawing();
      } else {
        this.drawboard.stopDrawing();
      }
    },
    // 清除上一个广告牌
    clearLastBillboard() {
      this.drawboard.clearLastBillboard();
    },
    // 更新广告牌高度和距地面高度
    updateBillboardDimensions() {
      this.drawboard.updateBillboardHeight(this.billboardHeight, this.groundHeight);
    },

    // 曝光分析
    async handleExposureAnalysis() {
      try {
        console.log('开始曝光分析...');

        // 发送广告牌数据到后端
        console.log('正在发送广告牌数据...');
        const result = await this.exposureAnalysis.sendBillboardsToBackend();
        console.log('发送广告牌数据结果:', result);

        if (!result || result.status !== 'success') {
          throw new Error('发送广告牌数据失败');
        }

        // 添加延迟，确保后端有足够时间处理数据
        await new Promise(resolve => setTimeout(resolve, 1000));

        await this.mapLayerManager.fetchAndDisplayLayer(
          'http://127.0.0.1:3000/GEA', 
          'exposure-area',
          '#ffff00',
          0.5
        );

      } catch (error) {
        console.error('曝光分析失败:', error);
        alert('曝光分析失败: ' + error.message);
      }
    },

    // 遮挡分析
    async handleOcclusionAnalysis() {
      try {
        console.log('开始遮挡分析...');

        await this.mapLayerManager.fetchAndDisplayLayer(
          'http://127.0.0.1:3000/IA',
          'occlusion-area', 
          '#0000ff',
          0.5
        );

      } catch (error) {
        console.error('遮挡分析失败:', error);
        alert('遮挡分析失败: ' + error.message);
      }
    },

    // 可见区域分析
    async handleVisibleAreaAnalysis() {
      try {
        console.log('开始可见区域分析...');
        // 先清除其他分析图层
        this.mapLayerManager.clearOtherLayers('visible-area');
        
        await this.mapLayerManager.fetchAndDisplayLayer(
          'http://127.0.0.1:3000/VA', 
          'visible-area', 
          '#00ff00', 
          0.5
        );
      } catch (error) {
        console.error('可见区域分析失败:', error);
        alert('可见区域分析失败: ' + error.message);
      }
    },

    clearAnalysisLayers() {
      try {
        this.mapLayerManager.clearAnalysisLayers();
      } catch (error) {
        console.error('清除分析图层失败:', error);
        alert('清除分析图层失败: ' + error.message);
      }
    }
  },
};
</script>

<style>
#app {
  width: 100vw;
  height: 100vh;
  overflow: hidden;
  position: relative;
}

#map {
  width: 100%;
  height: 100%;
  position: absolute;
  top: 0;
  left: 0;
  z-index: 0;
  /*地图图层在最底层*/
}

.analysis-window {
  min-width: 320px;
  padding: 0px;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);

}

.primary-btn {
  flex: 1;
  padding: 10px;
  background: #4CAF50;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.primary-btn:hover {
  background: #45a049;
  transform: translateY(-5px);
}

.control-panel {
  background: #f5f5f5;
  padding: 15px;
  border-radius: 6px;
  margin: 0px 10px 20px 10px;
  /*上右下左*/
}

.drawing-controls {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.action-btn {
  padding: 8px 16px;
  border: 2px solid #4CAF50;
  background: white;
  color: #4CAF50;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
}

.action-btn.active {
  background: #4CAF50;
  color: white;
}

.action-btn.delete {
  border-color: #ff4444;
  color: #ff4444;
}

.action-btn.delete:hover {
  background: #ff4444;
  color: white;
}

.slider-group {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.slider-container {
  width: 100%;
}

.slider-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.slider-header label {
  color: #666;
  font-weight: 500;
}

.value {
  color: #4CAF50;
  font-weight: 600;
}

.slider {
  width: 100%;
  height: 6px;
  border-radius: 3px;
  background: #ddd;
  outline: none;
  -webkit-appearance: none;
}

.slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: #4CAF50;
  cursor: pointer;
  border: 2px solid white;
  box-shadow: 0 0 2px rgba(0, 0, 0, 0.2);
}

.slider::-moz-range-thumb {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: #4CAF50;
  cursor: pointer;
  border: 2px solid white;
  box-shadow: 0 0 2px rgba(0, 0, 0, 0.2);
}

.analysis-buttons {
  background: #f8f9fa;
  padding: 15px;
  border-radius: 8px;
  margin: 10px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.analysis-buttons h3 {
  margin: 0 0 15px 0;
  color: #2c3e50;
  font-size: 16px;
  font-weight: 600;
  text-align: center;
}

.button-group {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.analysis-btn {
  padding: 12px 20px;
  background: #2c3e50;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s ease;
  text-align: center;
  width: 100%;
}

.analysis-btn:hover {
  background: #34495e;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

.analysis-btn:active {
  transform: translateY(0);
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.analysis-btn.clear {
  background: #e74c3c;
}

.analysis-btn.clear:hover {
  background: #c0392b;
}
</style>
