import * as echarts from 'echarts';
export default class POIAnalysis {
  constructor(map) {
    this.map = map;
    this.poiLayers = new Set();
    this.regionsData = null;
    this.chart = null;
  }

  // 添加POI图层
  async addPOILayer(tagId, color) {
    try {
      // 构建图层ID
      const layerId = `poi-${tagId}`;
      const sourceId = `poi-source-${tagId}`;

      // 如果图层已存在，先移除
      this.removePOILayer(layerId);

      // 从后端获取POI数据
      const response = await fetch(`http://localhost:3000/poi/${tagId}`);
      if (!response.ok) {
        throw new Error(`获取${tagId}的POI数据失败`);
      }
      const data = await response.json();

      // 添加数据源
      this.map.addSource(sourceId, {
        type: 'geojson',
        data: data
      });

      // 添加POI点图层
      this.map.addLayer({
        id: layerId,
        type: 'circle',
        source: sourceId,
        paint: {
          'circle-radius': 6,
          'circle-color': color,
          'circle-opacity': 0.8,
          'circle-stroke-width': 1,
          'circle-stroke-color': '#ffffff'
        }
      });

      // 添加POI标签图层
      this.map.addLayer({
        id: `${layerId}-label`,
        type: 'symbol',
        source: sourceId,
        layout: {
          'text-field': ['get', 'name'],
          'text-size': 12,
          'text-offset': [0, 1.5],
          'text-anchor': 'top'
        },
        paint: {
          'text-color': '#333333',
          'text-halo-color': '#ffffff',
          'text-halo-width': 1
        }
      });

      // 记录添加的图层
      this.poiLayers.add(layerId);
      this.poiLayers.add(`${layerId}-label`);

      return true;
    } catch (error) {
      console.error('添加POI图层失败:', error);
      throw error;
    }
  }

  // 移除特定POI图层
  removePOILayer(layerId) {
    if (this.map.getLayer(layerId)) {
      this.map.removeLayer(layerId);
    }
    if (this.map.getLayer(`${layerId}-label`)) {
      this.map.removeLayer(`${layerId}-label`);
    }

    const sourceId = layerId.replace('poi-', 'poi-source-');
    if (this.map.getSource(sourceId)) {
      this.map.removeSource(sourceId);
    }

    // 从记录中移除
    this.poiLayers.delete(layerId);
    this.poiLayers.delete(`${layerId}-label`);
  }

  // 清除所有POI图层
  clearAllPOILayers() {
    // 复制一份图层ID列表，因为在遍历过程中会修改Set
    const layers = [...this.poiLayers];
    layers.forEach(layerId => {
      if (layerId.endsWith('-label')) return; // 跳过标签图层，它们会在主图层被移除时一起处理
      this.removePOILayer(layerId);
    });
  }

  // 获取街道数据
  async fetchRegionsData() {
    try {
      if (!this.regionsData) {
        const response = await fetch('http://localhost:3000/regions');
        if (!response.ok) {
          throw new Error('获取街道数据失败');
        }
        this.regionsData = await response.json();
      }
      return this.regionsData;
    } catch (error) {
      console.error('获取街道数据失败:', error);
      throw error;
    }
  }

  // 计算每个街道内的POI数量
  async calculatePOICountsByRegion(tagId) {
    try {
      // 获取街道数据
      const regions = await this.fetchRegionsData();
      
      // 获取POI数据
      const response = await fetch(`http://localhost:3000/poi/${tagId}`);
      if (!response.ok) {
        throw new Error(`获取${tagId}的POI数据失败`);
      }
      const poiData = await response.json();

      console.log('POI数据:', poiData.features.length, '个点');
      console.log('街道数据:', regions.features.length, '个街道');

      // 计算每个街道的POI数量
      const counts = regions.features.map(region => {
        const regionPolygon = region.geometry;
        // 确保多边形数据格式正确
        const polygonCoords = regionPolygon.type === 'MultiPolygon' 
          ? regionPolygon.coordinates[0][0]  // MultiPolygon格式
          : regionPolygon.coordinates[0];     // Polygon格式

        const poiCount = poiData.features.filter(poi => {
          const point = poi.geometry;
          // 确保点的坐标格式正确
          if (!point || !point.coordinates || point.coordinates.length !== 2) {
            console.warn('无效的POI点数据:', poi);
            return false;
          }
          return this.isPointInPolygon(point.coordinates, polygonCoords);
        }).length;

        console.log(`街道 ${region.properties.name} 的POI数量:`, poiCount);

        return {
          name: region.properties.name,
          count: poiCount
        };
      });

      return counts;
    } catch (error) {
      console.error('计算街道POI数量失败:', error);
      throw error;
    }
  }

  // 判断点是否在多边形内
  isPointInPolygon(point, polygon) {
    // 射线法判断点是否在多边形内
    let inside = false;
    const x = point[0], y = point[1];
    
    for (let i = 0, j = polygon.length - 1; i < polygon.length; j = i++) {
      const xi = polygon[i][0], yi = polygon[i][1];
      const xj = polygon[j][0], yj = polygon[j][1];
      
      // 点在多边形顶点上
      if ((xi === x && yi === y) || (xj === x && yj === y)) {
        return true;
      }
      
      // 射线与多边形边的交点判断
      if ((yi > y) !== (yj > y)) {
        const intersectX = (xj - xi) * (y - yi) / (yj - yi) + xi;
        if (x === intersectX) {
          return true;  // 点在多边形边上
        }
        if (x < intersectX) {
          inside = !inside;
        }
      }
    }
    
    return inside;
  }

  // 创建或更新折线图
  async updateRegionChart(tagId, chartDom) {
    try {
      if (!this.chart) {
        this.chart = echarts.init(chartDom);
      }

      const counts = await this.calculatePOICountsByRegion(tagId);
      
      // 检查是否所有值都为0
      const allZero = counts.every(item => item.count === 0);
      if (allZero) {
        console.warn('警告：所有街道的POI数量都为0，可能存在数据问题');
      }
      
      // 按POI数量排序
      counts.sort((a, b) => b.count - a.count);

      const option = {
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'shadow'
          },
          formatter: function(params) {
            const data = params[0];
            return `${data.name}<br/>POI数量：${data.value}`;
          }
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '15%',  // 增加底部空间以显示完整的x轴标签
          containLabel: true
        },
        xAxis: {
          type: 'category',
          data: counts.map(item => item.name),
          axisLabel: {
            interval: 0,
            rotate: 45,
            textStyle: {
              fontSize: 12
            }
          }
        },
        yAxis: {
          type: 'value',
          name: 'POI数量',
          minInterval: 1  // 确保y轴刻度为整数
        },
        series: [{
          data: counts.map(item => ({
            value: item.count,
            name: item.name
          })),
          type: 'line',
          smooth: true,
          markPoint: {
            data: [
              { type: 'max', name: '最大值' },
              { type: 'min', name: '最小值' }
            ]
          },
          markLine: {
            data: [
              { type: 'average', name: '平均值' }
            ]
          }
        }]
      };

      this.chart.setOption(option);
      
      // 输出调试信息
      console.log('图表数据:', counts);
    } catch (error) {
      console.error('更新街道POI统计图表失败:', error);
      throw error;
    }
  }

  // 清除图表
  clearChart() {
    if (this.chart) {
      this.chart.dispose();
      this.chart = null;
    }
  }
}
