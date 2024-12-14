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
      <button class="sidebar-btn" @click="toggleWindow('poi-analysis')">
        POI分析
      </button>
      <button class="sidebar-btn" @click="toggleWindow('location-optimization')">
        区位优化
      </button>
      <button class="sidebar-btn" @click="toggleFirstPerson">
        第一人称
      </button>
      <button class="sidebar-btn" @click="toggleWindow('settings')">
        系统设置
      </button>
    </div>

    <FirstPersonView v-show="showFirstPerson" :mainMap="map" />

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

    <FloatWindow title="POI分析" class="analysis-window" v-show="activeWindow === 'poi-analysis'"></FloatWindow>

    <FloatWindow title="区位优化" class="analysis-window" v-show="activeWindow === 'location-optimization'">
    </FloatWindow>

    <!-- 新增系统设置窗口 -->
    <FloatWindow title="系统设置" class="analysis-window settings-window" v-show="activeWindow === 'settings'">
      <div class="settings-panel">
        <div class="setting-section">
          <h3>地图样式</h3>
          <div class="map-styles">
            <div 
              v-for="style in mapStyles" 
              :key="style.id"
              class="style-item"
              :class="{ active: currentMapStyle === style.url }"
              @click="changeMapStyle(style.url)"
            >
              <img :src="style.preview" :alt="style.name">
              <span>{{ style.name }}</span>
            </div>
          </div>
        </div>

        <!-- 新增颜色设置部分 -->
        <div class="setting-section">
          <h3>颜色设置</h3>
          <div class="color-settings">
            <div class="color-item">
              <label>建筑物颜色</label>
              <div class="color-picker">
                <input 
                  type="color" 
                  v-model="colors.building" 
                  @change="updateBuildingColor"
                >
                <span>{{ colors.building }}</span>
              </div>
            </div>

            <div class="color-item">
              <label>曝光区域颜色</label>
              <div class="color-picker">
                <input 
                  type="color" 
                  v-model="colors.exposure" 
                  @change="updateExposureColor"
                >
                <span>{{ colors.exposure }}</span>
              </div>
            </div>

            <div class="color-item">
              <label>遮挡区域颜色</label>
              <div class="color-picker">
                <input 
                  type="color" 
                  v-model="colors.occlusion" 
                  @change="updateOcclusionColor"
                >
                <span>{{ colors.occlusion }}</span>
              </div>
            </div>

            <div class="color-item">
              <label>可见区域颜色</label>
              <div class="color-picker">
                <input 
                  type="color" 
                  v-model="colors.visible" 
                  @change="updateVisibleColor"
                >
                <span>{{ colors.visible }}</span>
              </div>
            </div>
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
import FirstPersonView from "./components/FirstPersonView.vue";
import DrawBoard from '@/utils/DrawBoard.js';
import ExposureAnalysis from '@/utils/ExposureAnalysis.js';
import MapLayerManager from '@/utils/MapLayer.js';
import TimeAnalysis from '@/utils/TimeAnalysis.js';
import '@/styles/settings.css'  // 引入settings.css
import '@/styles/analysis.css'  // 引入analysis.css
import '@/styles/sidebar.css'   // 引入sidebar.css

export default {
  name: "App",
  components: {
    FloatWindow,
    FirstPersonView,
  },
  data() {
    return {
      isDrawing: false,
      billboardHeight: 30,
      groundHeight: 50,
      activeWindow: null,
      activeChart: 'time',
      charts: {
        time: null,
      },
      showFirstPerson: false,
      currentMapStyle: 'mapbox://styles/mapbox/light-v11',
      mapStyles: [
        {
          id: 'light',
          name: '浅色',
          url: 'mapbox://styles/mapbox/light-v11',
          preview: 'https://api.mapbox.com/styles/v1/mapbox/light-v11/static/0,0,1/300x200?access_token=pk.eyJ1IjoiYWlsYW56aGFuZyIsImEiOiJjbTMycjh3b28xMXg0MmlwcHd2ZmttZWYyIn0.T42ZxSkFvc05u3vfMT6Paw'
        },
        {
          id: 'dark',
          name: '深色',
          url: 'mapbox://styles/mapbox/dark-v11',
          preview: 'https://api.mapbox.com/styles/v1/mapbox/dark-v11/static/0,0,1/300x200?access_token=pk.eyJ1IjoiYWlsYW56aGFuZyIsImEiOiJjbTMycjh3b28xMXg0MmlwcHd2ZmttZWYyIn0.T42ZxSkFvc05u3vfMT6Paw'
        },
        {
          id: 'satellite',
          name: '卫星',
          url: 'mapbox://styles/mapbox/satellite-v9',
          preview: 'https://api.mapbox.com/styles/v1/mapbox/satellite-v9/static/0,0,1/300x200?access_token=pk.eyJ1IjoiYWlsYW56aGFuZyIsImEiOiJjbTMycjh3b28xMXg0MmlwcHd2ZmttZWYyIn0.T42ZxSkFvc05u3vfMT6Paw'
        },
        {
          id: 'streets',
          name: '街道',
          url: 'mapbox://styles/mapbox/streets-v12',
          preview: 'https://api.mapbox.com/styles/v1/mapbox/streets-v12/static/0,0,1/300x200?access_token=pk.eyJ1IjoiYWlsYW56aGFuZyIsImEiOiJjbTMycjh3b28xMXg0MmlwcHd2ZmttZWYyIn0.T42ZxSkFvc05u3vfMT6Paw'
        }
      ],
      colors: {
        building: '#000000',
        exposure: '#ffff00',
        occlusion: '#0000ff',
        visible: '#00ff00'
      }
    };
  },

  // 使用类成员变量存储地图相关实例和数据
  map: null,
  drawboard: null,
  exposureAnalysis: null,
  mapLayerManager: null,
  geojsonData: null, // 存储GeoJSON数据
  heatmapData: null, // 存储热力图数据

  mounted() {
    mapboxgl.accessToken = 'pk.eyJ1IjoiYWlsYW56aGFuZyIsImEiOiJjbTMycjh3b28xMXg0MmlwcHd2ZmttZWYyIn0.T42ZxSkFvc05u3vfMT6Paw';
    
    // 初始化地图
    this.map = new mapboxgl.Map({
      container: 'map',
      style: 'mapbox://styles/mapbox/light-v11',
      center: { lng: 116.4170, lat: 39.9288 },
      zoom: 15.4,
      pitch: 0,
      bearing: 0,
      maxPitch: 69,
      antialias: true,
      attributionControl: false,
      preserveDrawingBuffer: false
    });

    // 初始化其他实例
    this.drawboard = new DrawBoard(this.map, this.billboardHeight, this.groundHeight);
    this.exposureAnalysis = new ExposureAnalysis(this.map);
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
        this.geojsonData = await response.json(); // 存储到类成员变量
        
        // 添加数据源
        this.map.addSource('buildings', {
          'type': 'geojson',
          'data': this.geojsonData,
          'worker': true,
          'cluster': false
        });

        // 添加3D建筑层 - 移除 minzoom 限制
        this.map.addLayer({
          'id': '3d-buildings',
          'type': 'fill-extrusion',
          'source': 'buildings',
          'paint': {
            'fill-extrusion-color': this.colors.building,
            'fill-extrusion-height': ['to-number', ['get', 'height']],
            'fill-extrusion-base': 0,
            'fill-extrusion-opacity': 0.9,
            'fill-extrusion-vertical-gradient': true
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
          this.colors.exposure,  // 使用颜色变量
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
          this.colors.occlusion,  // 使用颜色变量
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
          this.colors.visible,  // 使用颜色变量
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
          // 直角坐标系内绘图��格设置
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
        const response = await fetch('http://127.0.0.1:3000/heatmap');
        this.heatmapData = await response.json();
        
        // 数据预处理 - 降低过滤阈值使更多点显示
        this.heatmapData.features = this.heatmapData.features.filter(f => f.properties.weight > 50);
        
        // 如果已存在热力图图层，先移除
        if (this.map.getLayer('heatmap-layer')) {
          this.map.removeLayer('heatmap-layer');
        }
        if (this.map.getSource('heatmap-source')) {
          this.map.removeSource('heatmap-source');
        }

        // 添加热力图数据源 - 减小聚类半径
        this.map.addSource('heatmap-source', {
          type: 'geojson',
          data: this.heatmapData,
          cluster: true,
          clusterRadius: 30  // 减小聚类半径
        });

        // 添加热力图图层 - 优化热力图参数
        this.map.addLayer({
          id: 'heatmap-layer',
          type: 'heatmap',
          source: 'heatmap-source',
          paint: {
            // 权重插值
            'heatmap-weight': [
              'interpolate',
              ['linear'],
              ['get', 'weight'],
              0, 0,
              100, 0.2,   // 增加中间值
              1000, 0.5,  // 增加中间值
              10000, 1
            ],
            
            // 热力图强度
            'heatmap-intensity': [
              'interpolate',
              ['linear'],
              ['zoom'],
              0, 0.5,
              20, 2
            ],
            
            // 热力图半径
            'heatmap-radius': [
              'interpolate',
              ['linear'],
              ['zoom'],
              0, 10,
              10, 15,
              15, 30
            ],
            
            // 热力图颜色
            'heatmap-color': [
              'interpolate',
              ['linear'],
              ['heatmap-density'],
              0, 'rgba(0, 0, 255, 0)',
              0.2, 'rgba(0, 0, 255, 0.5)',
              0.4, 'rgba(0, 255, 255, 0.7)',
              0.6, 'rgba(0, 255, 0, 0.7)',
              0.8, 'rgba(255, 255, 0, 0.8)',
              1, 'rgba(255, 0, 0, 0.9)'
            ],
            
            // 热力图不透明度
            'heatmap-opacity': 0.9
          }
        });

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
    },

    // 切换第一人称视角
    toggleFirstPerson() {
      this.showFirstPerson = !this.showFirstPerson;
    },

    // 修改 changeMapStyle 方法
    async changeMapStyle(styleUrl) {
      this.currentMapStyle = styleUrl;
      if (this.map) {
        try {
          // 保存当前的重要图层信息
          const preserveLayers = [];
          const layersToPreserve = ['3d-buildings', 'exposure-area', 'occlusion-area', 'visible-area', 'heatmap-layer'];
          
          // 保存需要保留的图层信息
          for (const layerId of layersToPreserve) {
            if (this.map.getLayer(layerId)) {
              const sourceId = this.map.getLayer(layerId).source;
              const sourceData = this.map.getSource(sourceId)._data;
              
              preserveLayers.push({
                layerId,
                sourceId,
                sourceData,
                // 保存图层的完整配置
                layerConfig: this.map.getLayer(layerId)
              });
            }
          }

          // 设置新样式
          this.map.setStyle(styleUrl);

          // 等待新样式加载完成
          this.map.once('style.load', () => {
            // 恢复之前保存的图层
            preserveLayers.forEach(({ layerId, sourceId, sourceData, layerConfig }) => {
              // 添加数据源
              if (!this.map.getSource(sourceId)) {
                this.map.addSource(sourceId, {
                  type: 'geojson',
                  data: sourceData
                });
              }
              
              // 添加图层，使用完整的图层配置
              if (!this.map.getLayer(layerId)) {
                this.map.addLayer(layerConfig);
              }
            });
          });

        } catch (error) {
          console.error('切换地图样式失败:', error);
        }
      }
    },

    // 更新建筑物颜色
    updateBuildingColor() {
      if (this.map.getLayer('3d-buildings')) {
        this.map.setPaintProperty('3d-buildings', 'fill-extrusion-color', this.colors.building);
      }
    },

    // 更新曝光区域颜色
    updateExposureColor() {
      if (this.map.getLayer('exposure-area')) {
        this.map.setPaintProperty('exposure-area', 'fill-color', this.colors.exposure);
      }
    },

    // 更新遮挡区域颜色
    updateOcclusionColor() {
      if (this.map.getLayer('occlusion-area')) {
        this.map.setPaintProperty('occlusion-area', 'fill-color', this.colors.occlusion);
      }
    },

    // 更新可见区域颜色
    updateVisibleColor() {
      if (this.map.getLayer('visible-area')) {
        this.map.setPaintProperty('visible-area', 'fill-color', this.colors.visible);
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
}
</style>
