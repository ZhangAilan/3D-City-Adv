// DrawBoard.js
export default class DrawBoard {
    constructor(map, billboardHeight = 30, groundHeight = 30) {
      this.map = map;
      this.billboardHeight = billboardHeight;
      this.groundHeight = groundHeight;
      this.isDrawing = false;
      this.startPoint = null;
      this.tempLineId = 'temp-line';
      this.billboards = [];
      this.currentBillboardIndex=-1;  //初始状态：无活动广告牌
      console.log(`DrawLine初始化完成: 广告牌高度=${billboardHeight}米, 距地面高度=${groundHeight}米`);
      this.initLayers();
    }
  
    initLayers() {
      this.map.on('load', () => {
        // Temporary line layer
        this.map.addSource('temp-line-source', {
          type: 'geojson',
          data: {
            type: 'Feature',
            geometry: {
              type: 'LineString',
              coordinates: []
            }
          }
        });
        console.log('临时线段数据源已添加');
  
        this.map.addLayer({
          id: this.tempLineId,
          type: 'line',
          source: 'temp-line-source',
          paint: {
            'line-color': '#ff0000',
            'line-width': 2
          }
        });
        console.log('临时线段图层已添加');
  
        // 添加广告牌图层数据源
        // 使用GeoJSON格式存储广告牌数据
        // 'billboards'是数据源的唯一标识符
        // data中定义了一个空的FeatureCollection,用于后续添加广告牌要素
        this.map.addSource('billboards', {
          type: 'geojson', // 数据类型为GeoJSON
          data: {
            type: 'FeatureCollection', // GeoJSON要素集合
            features: [] // 初始化为空数组,稍后会添加广告牌要素
          }
        });
        console.log('广告牌数据源已添加'); // 日志记录数据源添加成功
  
        // 添加广告牌的3D图层
        this.map.addLayer({
            id: 'billboards-3d', // 图层唯一标识符
            type: 'fill-extrusion', // 3D填充挤出类型,用于创建3D效果
            source: 'billboards', // 使用之前创建的billboards数据源
            paint: {
              'fill-extrusion-color': ['get', 'color'], // 从feature属性中获取color值作为颜色
              'fill-extrusion-opacity': 0.8, // 设置透明度为0.8
              'fill-extrusion-height': ['get', 'height'], // 从feature属性中获取height值作为高度
              'fill-extrusion-base': ['get', 'base'], // 从feature属性中获取base值作为基准高度
              'fill-extrusion-vertical-gradient': true // 启用垂直渐变效果
            }
          });
        console.log('广告牌3D图层已添加');
      });
    }
  
    startDrawing() {
      this.isDrawing = true;
      this.map.on('click', this.onMapClick);
      this.map.on('mousemove', this.onMouseMove);
      this.currentBillboardIndex = -1; // 重置当前索引
      console.log('绘制模式已启动');
    }
  
    stopDrawing() {
      this.isDrawing = false;
      this.startPoint = null;
      this.map.off('click', this.onMapClick);
      this.map.off('mousemove', this.onMouseMove);
      this.updateTempLine([]);
      console.log('绘制模式已停止');
    }
  
    onMapClick = (e) => {
      if (!this.startPoint) {
        this.startPoint = [e.lngLat.lng, e.lngLat.lat];
        console.log(`起点已设置: [${this.startPoint}]`);
      } else {
        const endPoint = [e.lngLat.lng, e.lngLat.lat];
        console.log(`终点已设置: [${endPoint}]`);
        this.createBillboard(this.startPoint, endPoint);
        this.startPoint = null;
        this.updateTempLine([]);
      }
    }
  
    onMouseMove = (e) => {
      if (this.startPoint) {
        const currentPoint = [e.lngLat.lng, e.lngLat.lat];
        this.updateTempLine([this.startPoint, currentPoint]);
      }
    }
  
    updateTempLine(coordinates) {
      const source = this.map.getSource('temp-line-source');
      if (source) {
        source.setData({
          type: 'Feature',
          geometry: {
            type: 'LineString',
            coordinates: coordinates
          }
        });
      }
    }
  
    createBillboard(start, end) {
        // 计算广告牌的四个顶点
        const dx = end[0] - start[0];
        const dy = end[1] - start[1];
        const length = Math.sqrt(dx * dx + dy * dy);
        
        // 计算垂直于线段的方向向量
        const perpendicular = [
          -dy / length * 0.0000001, // 缩小比例以适应地理坐标，确定广告牌的宽度
          dx / length * 0.0000001   // 缩小比例以适应地理坐标
        ];
      
        // 构建广告牌的四个顶点
        const p1 = start;
        const p2 = end;
        const p3 = [end[0] + perpendicular[0], end[1] + perpendicular[1]];
        const p4 = [start[0] + perpendicular[0], start[1] + perpendicular[1]];
      
        const billboard = {
          type: 'Feature',
          geometry: {
            type: 'Polygon',
            coordinates: [[
              p1,
              p2,
              p3,
              p4,
              p1  // 闭合多边形
            ]]
          },
          properties: {
            base: this.groundHeight,
            height: this.groundHeight + this.billboardHeight,
            color: '#FF0000'  // 修改为红色
          }
        };
      
        this.billboards.push(billboard);
        this.currentBillboardIndex=this.billboards.length-1;  // 更新当前广告牌索引
        console.log(`广告牌已创建: 
          起点=[${start}], 
          终点=[${end}], 
          高度=${this.billboardHeight}米, 
          距地面高度=${this.groundHeight}米`
        );
        this.updateBillboards();
    }
  
    updateBillboards() {
      const source = this.map.getSource('billboards');
      if (source) {
        source.setData({
          type: 'FeatureCollection',
          features: this.billboards
        });
        console.log(`广告牌已更新: 总数=${this.billboards.length}`);
      }
    }
  
    clearLastBillboard() {
      if (this.billboards.length > 0) {
        this.billboards.pop();
        this.currentBillboardIndex=this.billboards.length-1;  // 更新当前广告牌索引
        console.log('已删除上一个广告牌');
        this.updateBillboards();
      }
    }
  
    updateBillboardHeight(billboardHeight, groundHeight) {
      this.billboardHeight = billboardHeight;
      this.groundHeight = groundHeight;
      
       // 只更新当前广告牌
       if (this.currentBillboardIndex >= 0 && this.currentBillboardIndex < this.billboards.length) {
        this.billboards[this.currentBillboardIndex] = {
            ...this.billboards[this.currentBillboardIndex],
            properties: {
                ...this.billboards[this.currentBillboardIndex].properties,
                base: groundHeight,
                height: groundHeight + billboardHeight
            }
        };
        
        console.log(`当前广告牌尺寸已更新: 高度=${billboardHeight}米, 距地面高度=${groundHeight}米, 索引=${this.currentBillboardIndex}`);
        this.updateBillboards();
        }
    }
  
    /**
     * 获取广告牌中心位置
     * @returns {Array} 广告牌位置数组，每个元素包含 lng 和 lat 属性
     */
    getBillboards() {
      return this.billboards.map((billboard, index) => {
        // 获取广告牌多边形的坐标
        const coordinates = billboard.geometry.coordinates[0];
        console.log(`广告牌索引=${index}, 坐标=${JSON.stringify(coordinates)}`);
        
        // 计算中心点
        const center = coordinates.reduce((acc, curr, i) => {
          // 跳过最后一个点（因为它与第一个点相同，用于闭合多边形）
          if (i === coordinates.length - 1) return acc;
          
          return [
            acc[0] + curr[0] / (coordinates.length - 1),
            acc[1] + curr[1] / (coordinates.length - 1)
          ];
        }, [0, 0]);

        console.log(`广告牌索引=${index}, 中心点=lng:${center[0]}, lat:${center[1]}`);

        // 返回带有 lng 和 lat 属性的对象
        return {
          getPosition: () => ({
            lng: center[0],
            lat: center[1]
          })
        };
      });
    }

}