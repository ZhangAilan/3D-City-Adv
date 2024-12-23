<!-- App.vue -->
<template>
  <div id="app">
    <div id='map'></div>

    <!-- 添加侧边栏 -->
    <div class="sidebar">
      <button class="sidebar-btn analysis" @click="toggleWindow('billboard-analysis')">
        曝光分析
      </button>
      <button class="sidebar-btn analysis" @click="toggleWindow('audience-preference')">
        流量分析
      </button>
      <button class="sidebar-btn analysis" @click="toggleWindow('accessibility-analysis')">
        可达性分析
      </button>
      <button class="sidebar-btn analysis" @click="toggleWindow('poi-analysis')">
        POI分析
      </button>
      <button class="sidebar-btn analysis" @click="toggleWindow('neighbor-analysis')">
        邻避分析
      </button>
      <button class="sidebar-btn optimization" @click="toggleWindow('location-optimization')">
        区位优化
      </button>
      <button class="sidebar-btn optimization" @click="toggleWindow('layout-optimization')">
        布局优化
      </button>
      <button class="sidebar-btn utility" @click="toggleFirstPerson">
        第一人称
      </button>
      <button 
        class="sidebar-btn utility" 
        @click="toggleStreetView"
        :class="{ active: isStreetViewMode }"
      >
        实景地图
      </button>
      <button class="sidebar-btn utility" @click="toggleWindow('settings')">
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

    <FloatWindow title="可达性分析" class="accessibility-window" v-show="activeWindow === 'accessibility-analysis'">
      <div class="accessibility-panel">
        <div class="parameter-section">
          <h3>分析参数</h3>
          <div class="parameter-controls">
            <div class="parameter-item">
              <label>步行速度 (km/h)</label>
              <div class="slider-input">
                <input type="range" v-model.number="walkingSpeed" min="1" max="10" step="0.1" class="slider">
                <span class="value">{{ walkingSpeed }}</span>
              </div>
            </div>
            <div class="parameter-item">
              <label>时间阈值 (分钟)</label>
              <div class="slider-input">
                <input type="range" v-model.number="timeThreshold" min="5" max="30" step="1" class="slider">
                <span class="value">{{ timeThreshold }}</span>
              </div>
            </div>
          </div>
          <div class="accessibility-actions">
            <button class="accessibility-btn" @click="handleAccessibilityAnalysis">
              开始分析
            </button>
            <button class="accessibility-btn clear" @click="clearAccessibilityResults">
              清除结果
            </button>
          </div>
        </div>
        <div class="legend-section">
          <h3>图例说明</h3>
          <div class="legend-content">
            <div class="legend-item">
              <div class="legend-color" style="background: linear-gradient(to right, rgba(255,0,0,0.8), rgba(255,255,0,0.8), rgba(255,255,255,0))"></div>
              <div class="legend-labels">
                <span>高可达性</span>
                <span>中等</span>
                <span>低可达性</span>
              </div>
            </div>
            <div class="legend-info">
              <p>颜色越表示可达性越强，计算基于：</p>
              <ul>
                <li>步行速度：{{ walkingSpeed }} km/h</li>
                <li>时间阈值：{{ timeThreshold }} 分钟</li>
                <li>最大可达距离：{{ (walkingSpeed * timeThreshold / 60 * 1000).toFixed(0) }} 米</li>
              </ul>
            </div>
          </div>
        </div>
        <div class="shortest-path-section">
          <h3>最短路径分析</h3>
          <div class="path-controls">
            <button 
              class="path-btn" 
              :class="{ active: isMarkingPoints }"
              @click="toggleMarkPoints"
            >
              {{ isMarkingPoints ? '停止标注' : '开始标注' }}
            </button>
            <button 
              class="path-btn" 
              @click="generateShortestPath"
              :disabled="markedPoints.length < 2"
            >
              生成路径
            </button>
            <button 
              class="path-btn clear" 
              @click="clearPathLayer"
            >
              清除路径
            </button>
            <button 
              class="path-btn clear" 
              @click="clearMarkedPoints"
            >
              清除标注点
            </button>
          </div>
          
          <div class="path-info" v-if="pathDistance">
            <div class="info-item">
              <span class="label">路径距离：</span>
              <span class="value">{{ pathDistance.toFixed(0) }} 米</span>
            </div>
          </div>

          <div class="marked-points-list" v-if="markedPoints.length > 0">
            <h4>已标注点位</h4>
            <div class="points-container">
              <div v-for="(point, index) in markedPoints" :key="index" class="point-item">
                <span class="point-index">{{ index + 1 }}</span>
                <span class="point-coords">
                  [{{ point[0].toFixed(4) }}, {{ point[1].toFixed(4) }}]
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </FloatWindow>

    <FloatWindow title="POI分析" class="analysis-window" v-show="activeWindow === 'poi-analysis'">
      <div class="poi-analysis-panel">
        <div class="poi-tags">
          <button 
            v-for="tag in poiTags" 
            :key="tag.id"
            class="poi-tag"
            :class="{ active: activePOITags.includes(tag.id) }"
            @click="togglePOITag(tag.id)"
          >
            {{ tag.name }}
          </button>
        </div>
        <div class="poi-controls">
          <button class="action-btn" @click="fetchPOIData">
            加载POI数据
          </button>
          <button class="action-btn clear" @click="clearPOIData">
            清除POI数据
          </button>
        </div>
        <div class="poi-legend" v-if="activePOITags.length > 0">
          <h3>图例</h3>
          <div class="poi-legend-items">
            <div 
              v-for="tag in poiTags.filter(t => activePOITags.includes(t.id))" 
              :key="tag.id" 
              class="poi-legend-item"
            >
              <div class="poi-color-dot" :style="{ backgroundColor: tag.color }"></div>
              <span>{{ tag.name }}</span>
            </div>
          </div>
        </div>
        <div class="poi-chart-wrapper">
          <div class="poi-chart-container">
            <div class="poi-chart-title">各街道POI分布统计</div>
            <div id="poi-region-chart"></div>
          </div>
        </div>
      </div>
    </FloatWindow>

    <FloatWindow title="邻避分析" class="analysis-window" v-show="activeWindow === 'neighbor-analysis'">
      <div class="neighbor-analysis-panel">
        <!-- 分析参数部分 -->
        <div class="analysis-section">
          <h3>分析参数</h3>
          <div class="parameter-item">
            <label>广告牌音量 (dB)</label>
            <div class="slider-input">
              <input 
                type="range" 
                v-model.number="noiseLevel" 
                min="30" 
                max="90" 
                step="1" 
                class="slider"
              >
              <span class="value">{{ noiseLevel }}</span>
            </div>
            <div class="reference-values">
              <p>参考值：</p>
              <ul>
                <li>30dB - 低声耳语</li>
                <li>50dB - 普通谈话</li>
                <li>70dB - 繁忙街道</li>
                <li>90dB - 重型卡车</li>
              </ul>
            </div>
          </div>
        </div>

        <!-- 图例说明部分 -->
        <div class="legend-section">
          <h3>图例说明</h3>
          <div class="legend-bar"></div>
          <div class="legend-labels">
            <span>低影响</span>
            <span>中等</span>
            <span>高影响</span>
          </div>
        </div>

        <!-- 底部按钮 -->
        <div class="bottom-actions">
          <button class="action-btn primary" @click="handleNoiseAnalysis">
            开始分析
          </button>
          <button class="action-btn danger" @click="clearNoiseAnalysis">
            清除结果
          </button>
        </div>
      </div>
    </FloatWindow>

    <FloatWindow title="区位优化" class="analysis-window" v-show="activeWindow === 'location-optimization'">
    </FloatWindow>

    <FloatWindow title="布局优化" class="analysis-window" v-show="activeWindow === 'layout-optimization'"></FloatWindow>

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

    <StreetViewPopup
      v-if="streetViewPopup.visible"
      :coordinates="streetViewPopup.coordinates"
      @close="closeStreetViewPopup"
    />

    <!-- 街景弹窗 -->
    <div 
      v-if="streetViewPopup.visible" 
      class="street-view-popup-container"
    >
      <StreetViewPopup
        :coordinates="streetViewPopup.coordinates"
        @close="closeStreetViewPopup"
      />
    </div>
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
import AccessibilityAnalysis from '@/utils/Accessibility.js';
import '@/styles/settings.css'  // 引入settings.css
import '@/styles/analysis.css'  // 引入analysis.css
import '@/styles/sidebar.css'   // 引入sidebar.css
import '@/styles/accessibility.css';
import '@/styles/neighbor.css'  // 添加这一行
import '@/styles/poi.css'      // 添加POI样式文件
import NoiseRadiation from '@/utils/NoiseRadiation.js';
import StreetViewPopup from './components/StreetViewPopup.vue';
import POIAnalysis from '@/utils/POIanaysis.js';

export default {
  name: "App",
  components: {
    FloatWindow,
    FirstPersonView,
    StreetViewPopup,
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
      },
      walkingSpeed: 5.0,    // 默认步行速度 5 km/h
      timeThreshold: 15,    // 默认时间阈值 15 分钟
      isMarkingPoints: false,
      markedPoints: [],
      pathDistance: null,
      noiseLevel: 60,
      noiseRadiation: null,
      streetViewPopup: {
        visible: false,
        coordinates: null,
      },
      isStreetViewMode: false,
      streetViewMarker: null,
      poiTags: [
        { id: 'ACCOMMODATION', name: '住宿', color: '#FF0000' },  // 红色
        { id: 'AUTOMOTIVE', name: '汽车', color: '#00FF00' },    // 绿色
        { id: 'BUSINESS', name: '商业', color: '#0000FF' },    // 蓝色
        { id: 'EAT', name: '饮食', color: '#FFFF00' },        // 黄色
        { id: 'EDUCATION', name: '教育', color: '#FF00FF' },     // 品红
        { id: 'HEALTH', name: '健康', color: '#00FFFF' },        // 青色
        { id: 'LANDUSE', name: '土地利用', color: '#800000' },   // 栗色
        { id: 'PUBLICSERVICE', name: '公共服务', color: '#008000' }, // 深绿色
        { id: 'RELIGIOUS', name: '宗教', color: '#000080' },     // 海军蓝
        { id: 'SETTLEMENTS', name: '街道', color: '#FF4500' },   // 橙红色
        { id: 'SHOP', name: '购物', color: '#2E8B57' },      // 海洋绿
        { id: 'SPORT', name: '运动', color: '#8A2BE2' },        // 蓝紫色
        { id: 'TOURISM', name: '旅游', color: '#FFD700' },       // 金色
        { id: 'TRANSPORT', name: '交通', color: '#DC143C' } // 猩红
      ],
      activePOITags: [],
      poiAnalysis: null,
    };
  },

  // 使用类成员变量存储地图相关实例和数据
  map: null,
  drawboard: null,
  exposureAnalysis: null,
  mapLayerManager: null,
  geojsonData: null, // 存储GeoJSON数据
  heatmapData: null, // 存储热力图数据
  accessibilityAnalysis: null,

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
    this.accessibilityAnalysis = new AccessibilityAnalysis(this.map);
    this.noiseRadiation = new NoiseRadiation(this.map);
    this.poiAnalysis = new POIAnalysis(this.map);

    // 添加对新标记点的监听
    this.map.on('markerAdded', (e) => {
      this.markedPoints.push(e.point);
    });

    // 添加地图点击件监听
    this.map.on('click', (e) => {
      if (this.isStreetViewMode) {
        this.handleStreetViewClick(e);
      }
    });
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

        // 添加3D建筑层 - 除 minzoom 限制
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

    // 清除析图层
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
        // 定义ECharts图表置选项
        const option = {
          // 图表标题配置
          title: {
            text: '24小时GPS轨迹统计', // 图表主标题文本
            left: 'center'  // 标题水平居中对齐
          },
          // 提示框配置
          tooltip: {
            trigger: 'axis', // 触发类型:坐标轴触发
            axisPointer: {
              type: 'shadow' // 指示器类型:阴影指示器
            }
          },
          // 直角坐标系内绘图设置
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
        this.heatmapData.features = this.heatmapData.features.filter(f => f.properties.weight > 30);
        
        // 如果已存在热力图图层，先移除
        if (this.map.getLayer('heatmap-layer')) {
          this.map.removeLayer('heatmap-layer');
        }
        if (this.map.getSource('heatmap-source')) {
          this.map.removeSource('heatmap-source');
        }

        // 添加热力图数据源 - 移除聚类功能
        this.map.addSource('heatmap-source', {
          type: 'geojson',
          data: this.heatmapData
        });

        // 添加热力图图层 - 优化参数以适应非聚类数据
        this.map.addLayer({
          id: 'heatmap-layer',
          type: 'heatmap',
          source: 'heatmap-source',
          paint: {
            // 权重插值 - 调整权重范围
            'heatmap-weight': [
              'interpolate',
              ['linear'],
              ['get', 'weight'],
              30, 0,      // 最小权重
              100, 0.3,   // 低权重
              500, 0.6,   // 中等权重
              1000, 0.8,  // 高权重
              5000, 1     // 最大权重
            ],
            
            // 热力图强度 - 降低整体强度
            'heatmap-intensity': [
              'interpolate',
              ['linear'],
              ['zoom'],
              0, 0.5,    // 降低基础强度
              10, 0.8,   // 中等缩放级别
              15, 1.2,   // 较高缩放级别
              20, 1.5    // 最大缩放级别
            ],
            
            // 热力图半径 - 增大半径使热力图更平滑
            'heatmap-radius': [
              'interpolate',
              ['linear'],
              ['zoom'],
              0, 20,     // 基础半径
              10, 25,    // 中等缩放��别
              15, 30,    // 较高缩放级别
              20, 40     // 最大缩放级别
            ],
            
            // 热力图颜色 - 使用更渐进的颜色过渡
            'heatmap-color': [
              'interpolate',
              ['linear'],
              ['heatmap-density'],
              0, 'rgba(0, 0, 0, 0)',
              0.2, 'rgba(0, 0, 255, 0.4)',   // 深蓝色
              0.4, 'rgba(0, 255, 255, 0.6)', // 青
              0.6, 'rgba(0, 255, 0, 0.7)',   // 绿色
              0.8, 'rgba(255, 255, 0, 0.8)', // 黄色
              0.9, 'rgba(255, 128, 0, 0.9)', // 橙色
              1, 'rgba(255, 0, 0, 1)'        // 红色
            ],
            
            // 热力图不透明度 - 保持适中的透明度
            'heatmap-opacity': 0.7
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
          
          // 保存需要保留的层信息
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
    },

    // 处理可达性分析
    handleAccessibilityAnalysis() {
      try {
        this.accessibilityAnalysis.displayAccessibility(
          this.walkingSpeed,
          this.timeThreshold
        );
      } catch (error) {
        console.error('可达性分析失败:', error);
        alert('可达性分析失败: ' + error.message);
      }
    },

    // 清除可达性分析结果
    clearAccessibilityResults() {
      try {
        this.accessibilityAnalysis.clearAccessibility();
      } catch (error) {
        console.error('清除可达性分析结果失败:', error);
        alert('清除可达性分析结果失败: ' + error.message);
      }
    },

    toggleMarkPoints() {
      this.isMarkingPoints = !this.isMarkingPoints;
      this.accessibilityAnalysis.toggleMarkPoints(this.isMarkingPoints);
    },

    clearMarkedPoints() {
      this.markedPoints = [];
      this.accessibilityAnalysis.clearMarkers();
      this.accessibilityAnalysis.clearPathLayer();
      this.pathDistance = null;
    },

    // 生成最短路径
    async generateShortestPath() {
      try {
        const distance = await this.accessibilityAnalysis.generateShortestPath(this.markedPoints);
        if (distance) {
          this.pathDistance = distance;
        }
      } catch (error) {
        console.error('生成路径失败:', error);
        alert('生成路径失败: ' + error.message);
      }
    },

    // 清除径图层
    clearPathLayer() {
      this.accessibilityAnalysis.clearPathLayer();
      this.pathDistance = null;
    },

    // 处理噪音分析
    handleNoiseAnalysis() {
      try {
        // 获取当前广告牌位置
        const billboards = this.drawboard.getBillboards();
        if (!billboards || billboards.length === 0) {
          throw new Error('请先绘制广告牌');
        }

        // 对每个广告牌创建辐射圈
        billboards.forEach(billboard => {
          const position = billboard.getPosition();
          this.noiseRadiation.createRadiationCircle(
            [position.lng, position.lat],
            this.noiseLevel
          );
        });
      } catch (error) {
        console.error('噪音分析失败:', error);
        alert('噪音分析失败: ' + error.message);
      }
    },

    // 清除噪音分析
    clearNoiseAnalysis() {
      if (this.noiseRadiation) {
        this.noiseRadiation.clearRadiation();
      }
    },

    toggleStreetView() {
      this.isStreetViewMode = !this.isStreetViewMode;
      
      if (this.isStreetViewMode) {
        this.map.getCanvas().style.cursor = 'crosshair';
      } else {
        this.map.getCanvas().style.cursor = '';
        this.closeStreetViewPopup();
      }
    },

    handleStreetViewClick(e) {
      if (!this.isStreetViewMode) return;

      // 如果已存在标注点，先移除
      if (this.streetViewMarker) {
        this.streetViewMarker.remove();
      }

      // 创建标注点元素
      const el = document.createElement('div');
      el.className = 'street-view-marker';
      
      // 创建包装器用于动画
      const wrapper = document.createElement('div');
      wrapper.className = 'marker-wrapper';
      
      const img = document.createElement('img');
      img.src = require('@/assets/car.png');
      
      wrapper.appendChild(img);
      el.appendChild(wrapper);

      // 创建新的 Marker
      this.streetViewMarker = new mapboxgl.Marker({
        element: el,
        anchor: 'center'
      })
        .setLngLat(e.lngLat)
        .addTo(this.map);
      
      // 触发动画
      requestAnimationFrame(() => {
        wrapper.style.transform = 'scale(1)';
        wrapper.style.opacity = '1';
      });

      // 更新弹窗信息
      this.streetViewPopup.coordinates = [e.lngLat.lng, e.lngLat.lat];
      this.streetViewPopup.visible = true;
    },

    closeStreetViewPopup() {
      this.streetViewPopup.visible = false;
      if (this.streetViewMarker) {
        this.streetViewMarker.remove();
        this.streetViewMarker = null;
      }
    },

    // 切换POI标签
    async togglePOITag(tagId) {
      const index = this.activePOITags.indexOf(tagId);
      if (index === -1) {
        this.activePOITags.push(tagId);
        // 等待DOM更新
        await this.$nextTick();
        // 更新图表
        const chartDom = document.getElementById('poi-region-chart');
        if (chartDom) {
          await this.poiAnalysis.updateRegionChart(tagId, chartDom);
        }
      } else {
        this.activePOITags.splice(index, 1);
        // 如果没有选中的标签，清除图表
        if (this.activePOITags.length === 0) {
          this.poiAnalysis.clearChart();
        } else {
          // 等待DOM更新
          await this.$nextTick();
          // 更新为最后一个选中的标签的数据
          const lastTagId = this.activePOITags[this.activePOITags.length - 1];
          const chartDom = document.getElementById('poi-region-chart');
          if (chartDom) {
            await this.poiAnalysis.updateRegionChart(lastTagId, chartDom);
          }
        }
      }
    },

    // 获取POI数据
    async fetchPOIData() {
      try {
        if (this.activePOITags.length === 0) {
          alert('请至少选择一个POI类型');
          return;
        }

        // 对每个激活的标签发起请求
        for (const tagId of this.activePOITags) {
          const tag = this.poiTags.find(t => t.id === tagId);
          if (!tag) continue;

          await this.poiAnalysis.addPOILayer(tagId, tag.color);
        }

        // 等待DOM更新
        await this.$nextTick();
        // 更新图表（使用最后一个选中的标签）
        const lastTagId = this.activePOITags[this.activePOITags.length - 1];
        const chartDom = document.getElementById('poi-region-chart');
        if (chartDom) {
          await this.poiAnalysis.updateRegionChart(lastTagId, chartDom);
        }
      } catch (error) {
        console.error('POI数据加载失败:', error);
        alert('POI数据加载失败: ' + error.message);
      }
    },

    // 清除POI数据
    clearPOIData() {
      this.poiAnalysis.clearAllPOILayers();
      this.poiAnalysis.clearChart();
      this.activePOITags = [];
    },
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

.mapboxgl-popup {
  max-width: 300px;
}

.mapboxgl-popup-content {
  padding: 0;
}

.sidebar-btn.active {
  background-color: #4CAF50;
  color: white;
}

/* 确保弹窗显示在最上层 */
.street-view-popup {
  z-index: 1000;
}

.street-view-popup-container {
  position: fixed;  /* 改为固定定位 */
  top: 300px;       /* 距离顶部的距离 */
  right: 20px;     /* 距离右侧的距离 */
  z-index: 1000;
  pointer-events: auto;
}

.street-view-popup-container::after {
  display: none;
}

.street-view-marker {
  width: 24px;
  height: 24px;
}

.marker-wrapper {
  width: 100%;
  height: 100%;
  transform: scale(0.5);
  opacity: 0;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.marker-wrapper img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.street-view-marker:hover .marker-wrapper {
  transform: scale(1.1);
}
</style>
