export default class NoiseRadiation {
  constructor(map) {
    this.map = map;
    this.radiationLayerId = 'noise-radiation-layer';
    this.radiationSourceId = 'noise-radiation-source';
  }

  /**
   * 生成噪音辐射圈
   * @param {Array} position - 广告牌位置 [lng, lat]
   * @param {number} noiseLevel - 噪音分贝值 (30-90)
   */
  createRadiationCircle(position, noiseLevel) {
    // 清除已有的辐射圈
    this.clearRadiation();

    // 计算辐射圈半径 (基于噪音衰减公式)
    const baseRadius = 100; // 基础半径(米)
    const radiusMultiplier = 1 + (noiseLevel - 30) / 60;
    const maxRadius = baseRadius * radiusMultiplier;

    // 创建多个同心圆形成辐射圈效果
    const circles = [];
    const numCircles = 5; // 辐射圈数量

    for (let i = numCircles - 1; i >= 0; i--) {
      const radius = (maxRadius * (i + 1)) / numCircles;
      circles.push(this.createCircleFeature(
        position, 
        radius, 
        i / (numCircles - 1)  // 从0到1的相对距离
      ));
    }

    // 添加辐射圈数据源
    if (!this.map.getSource(this.radiationSourceId)) {
      this.map.addSource(this.radiationSourceId, {
        type: 'geojson',
        data: {
          type: 'FeatureCollection',
          features: circles
        }
      });
    } else {
      const source = this.map.getSource(this.radiationSourceId);
      source.setData({
        type: 'FeatureCollection',
        features: circles
      });
    }

    // 添加辐射圈图层
    if (!this.map.getLayer(this.radiationLayerId)) {
      this.map.addLayer({
        id: this.radiationLayerId,
        type: 'fill',
        source: this.radiationSourceId,
        paint: {
          'fill-color': [
            'interpolate',
            ['linear'],
            ['get', 'distance'],  // 使用相对距离而不是intensity
            0, 'rgba(255, 0, 0, 0.8)',      // 中心为红色，不透明度提高到0.8
            0.5, 'rgba(255, 255, 0, 0.7)',  // 中间为黄色，不透明度提高到0.7
            1, 'rgba(0, 255, 0, 0.5)'       // 外围为绿色，保持较低不透明度
          ],
          'fill-opacity': [
            'interpolate',
            ['linear'],
            ['get', 'intensity'],  // 仍然使用intensity控制动画效果
            0, 0.3,  // 最小不透明度提高到0.3
            0.5, 0.5,  // 中间不透明度为0.5
            1, 0.7   // 最大不透明度提高到0.7
          ]
        }
      });
    }

    // 添加动画效果
    this.animateRadiation();
  }

  /**
   * 创建单个圆形要素
   */
  createCircleFeature(center, radius, distance) {
    const points = 64;
    const coords = [];
    
    for (let i = 0; i < points; i++) {
      const angle = (i / points) * (2 * Math.PI);
      const lng = center[0] + (radius / 111320) * Math.cos(angle);
      const lat = center[1] + (radius / 111320) * Math.sin(angle);
      coords.push([lng, lat]);
    }
    coords.push(coords[0]);

    return {
      type: 'Feature',
      properties: {
        intensity: Math.random(),  // 用于动画效果
        distance: distance         // 用于颜色渐变
      },
      geometry: {
        type: 'Polygon',
        coordinates: [coords]
      }
    };
  }

  /**
   * 动画效果
   */
  animateRadiation() {
    if (!this.animationFrame) {
      const animate = () => {
        const source = this.map.getSource(this.radiationSourceId);
        if (source) {
          const data = source._data;
          data.features.forEach(feature => {
            feature.properties.intensity = Math.abs(Math.sin(Date.now() / 1000));
          });
          source.setData(data);
        }
        this.animationFrame = requestAnimationFrame(animate);
      };
      animate();
    }
  }

  /**
   * 清除辐射圈
   */
  clearRadiation() {
    if (this.animationFrame) {
      cancelAnimationFrame(this.animationFrame);
      this.animationFrame = null;
    }

    if (this.map.getLayer(this.radiationLayerId)) {
      this.map.removeLayer(this.radiationLayerId);
    }
    if (this.map.getSource(this.radiationSourceId)) {
      this.map.removeSource(this.radiationSourceId);
    }
  }
} 