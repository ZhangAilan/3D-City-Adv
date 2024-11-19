// 创建新的工具类文件
export default class MapLayerManager {
    constructor(map) {
      this.map = map;
      // 添加一个数组来跟踪所有分析图层的ID
      this.analysisLayers = [];
    }
  
    async fetchAndDisplayLayer(url, layerId, color, opacity = 0.5) {
      try {
        console.log(`开始获取${layerId}数据...`);
        
        const response = await fetch(url, {
          method: 'GET',
          headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
          },
        }).catch(error => {
          console.error('请求失败:', error);
          throw new Error('网络请求失败');
        });
  
        if (!response.ok) {
          const errorText = await response.text();
          console.error('响应错误:', errorText);
          throw new Error(`HTTP error! status: ${response.status}`);
        }
  
        const data = await response.json();
  
        if (!data || data.status === 'error') {
          throw new Error(data.message || `获取${layerId}数据失败`);
        }
  
        // 如果已存在图层，先移除
        if (this.map.getLayer(layerId)) {
          this.map.removeLayer(layerId);
        }
        if (this.map.getSource(layerId)) {
          this.map.removeSource(layerId);
        }
  
        // 添加数据源
        this.map.addSource(layerId, {
          type: 'geojson',
          data: data
        });
  
        // 添加图层
        this.map.addLayer({
          id: layerId,
          type: 'fill',
          source: layerId,
          paint: {
            'fill-color': color,
            'fill-opacity': opacity
          }
        });

        // 将新图层ID添加到跟踪数组中
        if (!this.analysisLayers.includes(layerId)) {
          this.analysisLayers.push(layerId);
        }
  
        console.log(`${layerId}图层添加成功`);
        return true;
  
      } catch (error) {
        console.error(`${layerId}分析失败:`, error);
        throw error;
      }
    }

    // 添加清除所有分析图层的方法
    clearAnalysisLayers() {
      console.log('开始清除所有分析图层...');
      this.analysisLayers.forEach(layerId => {
        if (this.map.getLayer(layerId)) {
          this.map.removeLayer(layerId);
        }
        if (this.map.getSource(layerId)) {
          this.map.removeSource(layerId);
        }
      });
      // 清空跟踪数组
      this.analysisLayers = [];
      console.log('所有分析图层已清除');
    }

    // 添加一个方法来清除特定图层以外的所有图层
    clearOtherLayers(excludeLayerId) {
      console.log(`清除${excludeLayerId}以外的所有分析图层...`);
      this.analysisLayers.forEach(layerId => {
        if (layerId !== excludeLayerId) {
          if (this.map.getLayer(layerId)) {
            this.map.removeLayer(layerId);
          }
          if (this.map.getSource(layerId)) {
            this.map.removeSource(layerId);
          }
        }
      });
      // 更新分析图层数组，只保留未被清除的图层
      this.analysisLayers = this.analysisLayers.filter(layerId => layerId === excludeLayerId);
      console.log('其他分析图层已清除');
    }
}