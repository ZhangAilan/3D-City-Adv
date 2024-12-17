import mapboxgl from 'mapbox-gl';

class AccessibilityAnalysis {
  constructor(map) {
    this.map = map;
    this.hexagonLayer = null;
    this.sourceId = 'accessibility-source';
    this.layerId = 'accessibility-layer';
    this.markers = [];
    this.isMarkingPoints = false;
    this.pathLayer = null;
    this.pathSource = 'path-source';
    this.pathLayerId = 'path-layer';
  }

  // 生成六边形网格
  generateHexGrid(center, radius, walkingSpeed, timeThreshold) {
    console.log('生成六边形网格参数:', {
      center,
      radius,
      walkingSpeed,
      timeThreshold
    });

    // 将步行速度和时间转换为米
    const maxDistance = (walkingSpeed * 1000 * timeThreshold) / 60; // 最大可达距离(米)
    console.log('最大可达距离:', maxDistance, '米');

    // 修改网格大小和密度
    const gridSize = 40; // 增加网格大小，使整体更方正
    const hexSize = maxDistance / gridSize;
    const rows = gridSize;
    const cols = gridSize;
    const features = [];
    
    // 计算六边形的宽度和高度
    const width = hexSize * 2;
    const height = Math.sqrt(3) * hexSize;
    
    // 计算起始点 (使用经纬度增量)
    const metersPerDegree = 111319.9; // 赤道上1度对应的米数
    // 调整起始点计算，使网格更居中
    const startX = center[0] - ((width * cols * 0.75) / 2) / (metersPerDegree * Math.cos(center[1] * Math.PI / 180));
    const startY = center[1] - ((height * rows) / 2) / metersPerDegree;
    
    console.log('网格参数:', {
      hexSize,
      width,
      height,
      startX,
      startY
    });
    
    for (let row = 0; row < rows; row++) {
      for (let col = 0; col < cols; col++) {
        // 计算六边形中心点
        const x = startX + (col * width * 0.75) / (metersPerDegree * Math.cos(center[1] * Math.PI / 180));
        const y = startY + (row * height + (col % 2) * height / 2) / metersPerDegree;
        
        // 计算到广告牌的距离(米)
        const distance = this.calculateDistance([x, y], center) * metersPerDegree;
        
        // 计算可达性强度 (0-1之间)，使用指数衰减使过渡更自然
        const accessibility = Math.max(0, Math.exp(-distance / (maxDistance * 0.5)));
        
        // 生成六边形的顶点
        const vertices = this.generateHexagonVertices([x, y], hexSize / (metersPerDegree * Math.cos(y * Math.PI / 180)));
        
        features.push({
          type: 'Feature',
          properties: {
            accessibility: accessibility,
            distance: distance
          },
          geometry: {
            type: 'Polygon',
            coordinates: [vertices]
          }
        });
      }
    }
    
    console.log(`生成了 ${features.length} 个六边形单元`);
    return {
      type: 'FeatureCollection',
      features: features
    };
  }

  // 生成六边形顶点
  generateHexagonVertices(center, size) {
    const vertices = [];
    for (let i = 0; i < 6; i++) {
      const angle = (Math.PI / 3) * i;
      const x = center[0] + size * Math.cos(angle);
      const y = center[1] + size * Math.sin(angle);
      vertices.push([x, y]);
    }
    vertices.push(vertices[0]); // 闭合多边形
    return vertices;
  }

  // 计算两点之间的距离
  calculateDistance(point1, point2) {
    const dx = point2[0] - point1[0];
    const dy = point2[1] - point1[1];
    return Math.sqrt(dx * dx + dy * dy);
  }

  // 显示可达性分析结果
  displayAccessibility(walkingSpeed, timeThreshold) {
    console.log('开始可达性分析...');
    console.log(`步行速度: ${walkingSpeed} km/h, 时间阈值: ${timeThreshold} 分钟`);

    // 获取广告牌位置
    const billboardSource = this.map.getSource('billboards');
    if (!billboardSource) {
      console.error('未找到广告牌图层 (billboards)');
      return;
    }

    const billboardData = billboardSource._data;
    if (!billboardData || !billboardData.features.length) {
      console.error('未找到广告牌数据:', billboardData);
      return;
    }

    // 计算所有广告牌的平均位置
    const center = this.calculateCenterPoint(billboardData.features);
    console.log('广告牌中心点坐标:', center);

    // 生成六边形网格
    console.log('正在生成六边形网格...');
    const hexGrid = this.generateHexGrid(center, 0.01, walkingSpeed, timeThreshold);
    console.log(`生成了 ${hexGrid.features.length} 个六边形`);

    // 移除已有图层
    if (this.map.getLayer(this.layerId)) {
      console.log('移除已有的可达性图层');
      this.map.removeLayer(this.layerId);
    }
    if (this.map.getSource(this.sourceId)) {
      console.log('移除已有的可达性数据源');
      this.map.removeSource(this.sourceId);
    }

    try {
      console.log('添加新的数据源...');
      this.map.addSource(this.sourceId, {
        type: 'geojson',
        data: hexGrid
      });

      console.log('添加新的图层...');
      this.map.addLayer({
        id: this.layerId,
        type: 'fill',
        source: this.sourceId,
        paint: {
          // 颜色渐变：红->黄->透明
          'fill-color': [
            'interpolate',
            ['linear'],
            ['get', 'accessibility'],
            0, 'rgba(255, 255, 255, 0)', // 完全透明
            0.2, 'rgba(255, 255, 200, 0.4)', // 淡黄色
            0.4, 'rgba(255, 255, 0, 0.5)', // 黄色
            0.6, 'rgba(255, 200, 0, 0.6)', // 橙黄色
            0.8, 'rgba(255, 100, 0, 0.7)', // 橙红色
            1, 'rgba(255, 0, 0, 0.8)' // 红色
          ],
          'fill-opacity': 0.8,
          // 添加更细的描边
          'fill-outline-color': 'rgba(0, 0, 0, 0.1)'
        }
      });
      console.log('可达性分析完成');

    } catch (error) {
      console.error('创建可达性图层失败:', error);
      throw error;
    }
  }

  // 清除可达性分析结果
  clearAccessibility() {
    if (this.map.getLayer(this.layerId)) {
      this.map.removeLayer(this.layerId);
    }
    if (this.map.getSource(this.sourceId)) {
      this.map.removeSource(this.sourceId);
    }
  }

  // 修改计算中心点的方法
  calculateCenterPoint(features) {
    // 提取所有多边形的第一个点和第二个点（广告牌的起点和终点）
    let points = [];
    features.forEach(feature => {
      if (feature.geometry.type === 'Polygon') {
        // 获取多边形的第一个环的第一个点和第二个点
        const coords = feature.geometry.coordinates[0];
        points.push(coords[0]); // 起点
        points.push(coords[1]); // 终点
      }
    });

    if (points.length === 0) {
      console.error('没有找到有效的广告牌坐标点');
      return [0, 0];
    }

    // 计算所有点的平均值
    const sumCoords = points.reduce((sum, coord) => {
      return [sum[0] + coord[0], sum[1] + coord[1]];
    }, [0, 0]);

    const centerPoint = [
      sumCoords[0] / points.length,
      sumCoords[1] / points.length
    ];

    console.log('广告牌坐标点:', points);
    console.log('计算得到的中心点:', centerPoint);
    
    return centerPoint;
  }

  // 切换标注点模式
  toggleMarkPoints(enable) {
    this.isMarkingPoints = enable;
    if (enable) {
      this.map.on('click', this.handleMapClick);
    } else {
      this.map.off('click', this.handleMapClick);
    }
  }

  // 处理地图点击事件
  handleMapClick = (e) => {
    const point = [e.lngLat.lng, e.lngLat.lat];
    this.addMarker(point);
  }

  // 添加标注点
  addMarker(point) {
    // 创建立体标注点元素
    const el = document.createElement('div');
    el.className = 'marker';
    el.style.width = '30px'; // 增加宽度
    el.style.height = '30px'; // 增加高度
    el.style.borderRadius = '50%';
    el.style.backgroundColor = '#1890ff';
    el.style.border = '2px solid white';
    el.style.boxShadow = '0 0 10px rgba(0,0,0,0.5)'; // 更强的阴影效果

    // 创建 Mapbox 标注点
    const marker = new mapboxgl.Marker(el)
      .setLngLat(point)
      .addTo(this.map);

    this.markers.push(marker);
    
    // 触发事件通知 Vue 组件
    if (this.map.fire) {
      this.map.fire('markerAdded', { point });
    }

    // 发送当前所有标记点到后端
    this.sendAllMarkersToBackend();
  }

  // 发送当前所有标记点到后端
  async sendAllMarkersToBackend() {
    const features = this.markers.map(marker => {
      const lngLat = marker.getLngLat();
      console.log(`标记点经纬度: 经度 ${lngLat.lng}, 纬度 ${lngLat.lat}`); // 输出经纬度
      return {
        type: 'Feature',
        geometry: {
          type: 'Point',
          coordinates: [lngLat.lng, lngLat.lat]
        }
      };
    });

    const geojson = {
      type: 'FeatureCollection',
      features: features
    };

    console.log('发送到后端的数据:', geojson); // 输出发送到后端的数据

    try {
      const response = await fetch('http://localhost:3000/markers', { 
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(geojson) // 确保发送的是 JSON 字符串
      });

      if (!response.ok) {
        throw new Error('网络响应不正常');
      }

      const data = await response.json();
      console.log('所有标记点已成功发送到后端:', data);
      return data;
    } catch (error) {
      console.error('发送标记点到后端时出错:', error);
      throw error;
    }
  }

  // 清除所有标注点
  clearMarkers() {
    this.markers.forEach(marker => marker.remove());
    this.markers = [];
  }

  // 生成最短路径
  async generateShortestPath() {
    try {
      // 清除已有的路径
      this.clearPathLayer();

      // 发送请求到后端
      const response = await fetch('http://127.0.0.1:3000/shortest-path');

      if (!response.ok) {
        throw new Error('获取路径数据失败');
      }

      const result = await response.json();
      console.log('最短路径:', result); // 移到这里打印结果
      
      if (result.status === 'success') {
        // 添加路径图层
        if (this.map.getSource(this.pathSource)) {
          this.map.removeSource(this.pathSource);
        }

        this.map.addSource(this.pathSource, {
          type: 'geojson',
          data: result.data
        });

        // 添加路径线图层
        this.map.addLayer({
          id: this.pathLayerId,
          type: 'line',
          source: this.pathSource,
          layout: {
            'line-join': 'round',
            'line-cap': 'round'
          },
          paint: {
            'line-color': '#FF4D4F',
            'line-width': 4,
            'line-opacity': 0.8
          }
        });

        // 调整地图视角以适应路径
        const coordinates = result.data.geometry.coordinates;
        const bounds = coordinates.reduce((bounds, coord) => {
          return bounds.extend(coord);
        }, new mapboxgl.LngLatBounds(coordinates[0], coordinates[0]));

        this.map.fitBounds(bounds, {
          padding: 50,
          duration: 1000
        });

        // 返回路径距离（米）
        const metersPerDegree = 111319.9; // 赤道上1度对应的米数
        return result.data.properties.length * metersPerDegree;
      }
      return null;
    } catch (error) {
      console.error('生成路径失败:', error);
      throw error;
    }
  }

  // 清除路径图层
  clearPathLayer() {
    if (this.map.getLayer(this.pathLayerId)) {
      this.map.removeLayer(this.pathLayerId);
    }
    if (this.map.getSource(this.pathSource)) {
      this.map.removeSource(this.pathSource);
    }
  }
}

export default AccessibilityAnalysis;