// 曝光分析
export default class ExposureAnalysis {
    constructor(map) {
      this.map = map;
    }
  
    // 获取所有广告牌数据
    getAllBillboards() {
      const billboards = [];
      
      // 遍历地图上所有图层
      const layers = this.map.getStyle().layers;
      
      for (const layer of layers) {
        // 假设广告牌图层的 ID 都包含 'billboards' 字符串
        if (layer.id.includes('billboards')) {
          const source = this.map.getSource(layer.source);
          if (source) {
            const data = source._data; // 获取图层的 GeoJSON 数据
            billboards.push({
              id: layer.id,
              data: data,
              properties: {
                height: layer.paint['fill-extrusion-height'],
                groundHeight: layer.paint['fill-extrusion-base']
              }
            });
          }
        }
      }
      
      return billboards;
    }
  
    // 发送广告牌数据到后端
    async sendBillboardsToBackend() {
      try {
        const billboards = this.getAllBillboards();
        
        const response = await fetch('http://localhost:3000/save-billboards', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ billboards })
        });
  
        const result = await response.json();
        console.log('广告牌数据已发送到后端:', result);
        return result;
      } catch (error) {
        console.error('发送广告牌数据失败:', error);
        throw error;
      }
    }
  }