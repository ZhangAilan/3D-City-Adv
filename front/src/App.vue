<!-- App.vue -->
<template>
  <div id="app">
    <div id='map'></div>

    <!-- 添加侧边栏 -->
    <div class="sidebar">
      <button class="sidebar-btn" @click="toggleWindow('billboard-analysis')">
        曝光分析
      </button>
      <button class="sidebar-btn" @click="toggleWindow('audience-preference')">
        流量分析
      </button>
      <button class="sidebar-btn" @click="toggleWindow('billboard-optimization')">
        区位优化
      </button>
      <button class="sidebar-btn" @click="toggleWindow('location-optimization')">
        布局优化
      </button>
      <button class="sidebar-btn">
        第一人称
      </button>
      <button class="sidebar-btn" @click="toggleWindow('settings')">
        系统设置
      </button>
    </div>

    <FloatWindow title="3D城市广告牌曝光分析系统" class="analysis-window" v-show="activeWindow === 'billboard-analysis'">
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

    <FloatWindow title="流量分析" class="analysis-window" v-show="activeWindow === 'audience-preference'">
      <div class="analysis-buttons">
        <div class="drawing-controls">
          <button class="primary-btn" @click="handleChartDisplay('time')" :class="{ active: activeChart === 'time' }">
            GPS流量统计
          </button>
          <button class="primary-btn" @click="addHeatmapLayer">
            人流密度热力图
          </button>
          <button class="action-btn delete" @click="clearHeatmap">
            清除热力图
          </button>
        </div>
      </div>
      <div class="chart-container">
        <!--时间图表-->
        <div id="time-chart" class="chart-area" v-show="activeChart === 'time'"></div>
      </div>
    </FloatWindow>

    <FloatWindow title="区位优化" class="analysis-window" v-show="activeWindow === 'billboard-optimization'">
    </FloatWindow>

    <FloatWindow title="布局优化" class="analysis-window" v-show="activeWindow === 'location-optimization'">
    </FloatWindow>

    <!-- 新增系统设置窗口 -->
    <FloatWindow title="系统设置" class="analysis-window" v-show="activeWindow === 'settings'">
      <div class="settings-panel">
        <h3>系统设置</h3>
        <div class="settings-controls">
          <div class="setting-item">
            <label>地图样式</label>
            <select v-model="mapStyle">
              <option value="light">浅色</option>
              <option value="dark">深色</option>
              <option value="satellite">卫星</option>
            </select>
          </div>
          <div class="setting-item">
            <label>语言</label>
            <select v-model="language">
              <option value="zh">中文</option>
              <option value="en">English</option>
            </select>
          </div>
        </div>
      </div>
    </FloatWindow>
  </div>
</template>

<script>
import mapboxgl from "mapbox-gl";
import * as echarts from 'echarts';
import FloatWindow from "./components/FloatWindow.vue";
import DrawBoard from '@/utils/DrawBoard.js';
import ExposureAnalysis from '@/utils/ExposureAnalysis.js';
import MapLayerManager from '@/utils/MapLayer.js';
import TimeAnalysis from '@/utils/TimeAnalysis.js';
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
      activeWindow: 'billboard-analysis', // 当前激活的窗口
      activeChart: 'time',  //当前图表
      charts: {
        time: null,
      }
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

    // 清除分析图层
    clearAnalysisLayers() {
      try {
        this.mapLayerManager.clearAnalysisLayers();
      } catch (error) {
        console.error('清除分析图层失败:', error);
        alert('清除分析图层失败: ' + error.message);
      }
    },

    // 切换窗口
    toggleWindow(windowName) {
      this.activeWindow = this.activeWindow === windowName ? null : windowName;
    },

    // 处理图表显示
    async handleChartDisplay(chartType) {
      this.activeChart = chartType;
      //确保DOM更新
      await this.$nextTick();
      switch (chartType) {
        case 'time':
          await this.initTimeChart();
          break;
        case 'density':
          await this.initDensityChart();
          break;
      }
    },

    // 初始化时间图表
    async initTimeChart() {
      if (!this.charts.time) {
        const chartDom = document.getElementById('time-chart');
        this.charts.time = echarts.init(chartDom);
      }
      try {
        const response = await fetch('http://127.0.0.1:3000/gps-info');
        const data = await response.json();
        const hourCounts = TimeAnalysis.processTimeData(data);
        // 定义ECharts图表配置选项
        const option = {
          // 图表标题配置
          title: {
            text: '24小时GPS轨迹点统计', // 图表主标题文本
            left: 'center'  // 标题水平居中对齐
          },
          // 提示框配置
          tooltip: {
            trigger: 'axis', // 触发类型:坐标轴触发
            axisPointer: {
              type: 'shadow' // 指示器类型:阴影指示器
            }
          },
          // 直角坐标系内绘图网格设置
          grid: {
            left: '3%',  // 距离容器左侧的距离
            right: '4%', // 距离容器右侧的距离  
            bottom: '3%', // 距离容器底部的距离
            containLabel: true // 包含坐标轴标签
          },
          // X轴配置
          xAxis: {
            type: 'category', // 类目轴,适用于离散数据
            // 生成0-23的小时数据,补零对齐
            data: Array.from({ length: 24 }, (_, i) => i.toString().padStart(2, '0')),
            axisTick: {
              show: false // 不显示坐标轴刻度
            }
          },
          // Y轴配置
          yAxis: {
            type: 'value' // 数值轴,适用于连续数据
          },
          // 系列列表配置
          series: [{
            data: hourCounts, // 显示每小时的统计数据
            type: 'bar' // 柱状图类型
          }]
        }
        // 使用配置项设置图表
        this.charts.time.setOption(option);
      } catch (error) {
        console.error('时间图表初始化失败:', error);
      }
    },

    // 添加热力图图层
    async addHeatmapLayer() {
      try {
        // 获取热力图数据
        const response = await fetch('http://127.0.0.1:3000/heatmap');
        const heatmapData = await response.json();
        
        // 如果已存在热力图图层，先移除
        if (this.map.getLayer('heatmap-layer')) {
          this.map.removeLayer('heatmap-layer');
        }
        if (this.map.getSource('heatmap-source')) {
          this.map.removeSource('heatmap-source');
        }

        // 添加热力图数据源
        this.map.addSource('heatmap-source', {
          type: 'geojson',
          data: heatmapData
        });

        // 添加热力图图层
        this.map.addLayer({
          id: 'heatmap-layer',
          type: 'heatmap',
          source: 'heatmap-source',
          paint: {
            // 权重表达式
            'heatmap-weight': [
              'interpolate',
              ['linear'],
              ['get', 'weight'],
              0, 0,
              10000, 1
            ],
            // 热力图强度
            'heatmap-intensity': [
              'interpolate',
              ['linear'],
              ['zoom'],
              0, 1,
              15, 3
            ],
            // 热力图颜色渐变 - 使用更深的颜色
            'heatmap-color': [
              'interpolate',
              ['linear'],
              ['heatmap-density'],
              0, 'rgba(0,51,102,0)',
              0.2, 'rgb(0,102,204)',
              0.4, 'rgb(0,153,255)',
              0.6, 'rgb(255,153,51)',
              0.8, 'rgb(255,51,0)',
              1, 'rgb(153,0,0)'
            ],
            // 热力图半径
            'heatmap-radius': [
              'interpolate',
              ['linear'],
              ['zoom'],
              0, 2,
              15, 20
            ],
            // 热力图透明度 - 降低透明度使颜色更明显
            'heatmap-opacity': 0.9
          }
        });

        // 热力图加载完成后,调整地图视角
        this.map.easeTo({
          zoom: 13,
          pitch: 45, // 设置倾斜角度为69,俯视视角
          bearing: 135, // 设置旋转角度为15
          duration: 1000 // 动画持续1秒
        });

        console.log('热力图加载成功');
      } catch (error) {
        console.error('加载热力图失败:', error);
      }
    },

    // 清除热力图
    clearHeatmap() {
      if (this.map.getLayer('heatmap-layer')) {
        this.map.removeLayer('heatmap-layer');
      }
      if (this.map.getSource('heatmap-source')) {
        this.map.removeSource('heatmap-source');
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

/*控制面板*/
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
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
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
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.analysis-btn:active {
  transform: translateY(0);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.analysis-btn.clear {
  background: #e74c3c;
}

.analysis-btn.clear:hover {
  background: #c0392b;
}

.sidebar {
  position: fixed;
  left: 20px;
  top: 50%;
  transform: translateY(-50%);
  display: flex;
  flex-direction: column;
  gap: 10px;
  z-index: 1000;
}

.sidebar-btn {
  padding: 12px 20px;
  background: #40668b;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s ease;
  white-space: nowrap;
}

.sidebar-btn:hover {
  background: #487bad;
  transform: translateX(5px);
}

/*图表样式*/
.chart-container {
  padding: 15px;
  background: #f8f9fa;
  border-radius: 8px;
  margin: 10px;
}

.chart-area {
  width: 100%;
  height: 350px;
  background: #fff;
  border-radius: 8px;
  margin-top: 10px;
}
</style>
