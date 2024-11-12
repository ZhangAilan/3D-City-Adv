<!-- App.vue -->
<template>
  <div id="app">
    <div id='map'></div> 
      <FloatWindow title="3D城市广告牌曝光分析系统" class="analysis-window">
      <div class="button-group">
        <button class="primary-btn" @click="triggerFileInput">
          <i class="fas fa-building"></i>
          加载3D建筑
        </button>
        <button class="primary-btn" @click="addCustomThreeboxModel">
          <i class="fas fa-cube"></i>
          加载Threebox模型
        </button>
        <button class="primary-btn" @click="toggleFloatWindow">
          <i class="fas fa-window-maximize"></i>
          显示浮动窗口
        </button>
      </div>

      <input ref="fileInput" type="file" style="display: none" @change="handleFileSelect" accept=".geojson"/>
      
      <div class="control-panel">
        <div class="drawing-controls">
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
              <span class="value">{{billboardHeight}}m</span>
            </div>
            <input 
              type="range"
              v-model.number="billboardHeight"
              @input="updateBillboardDimensions"
              min="0"
              max="100"
              step="1"
              class="slider"
            />
          </div>
          
          <div class="slider-container">
            <div class="slider-header">
              <label>距地面高度</label>
              <span class="value">{{groundHeight}}m</span>
            </div>
            <input 
              type="range"
              v-model.number="groundHeight"
              @input="updateBillboardDimensions"
              min="0"
              max="100"
              step="1"
              class="slider"
            />
          </div>
        </div>
      </div>
    </FloatWindow>
    <FloatWindow v-if="showFloatWindow" title="3D模型展示">
      <ThreeDModel></ThreeDModel>
    </FloatWindow>
  </div>
</template>

<script>
import mapboxgl from "mapbox-gl";
import ThreeDModel from "./components/ThreeDModel.vue";
import FloatWindow from "./components/FloatWindow.vue";
import DrawBoard from '@/utils/DrawBoard.js';

export default {
name: "App",
components: {
  FloatWindow,
  ThreeDModel,
},
data() {
  return {
    map: null,
    tb: null,
    showFloatWindow: false,
    isDrawing:false,
    billboardHeight:30,
    groundHeight:50,
    drawLine:null,
  };
},

mounted() {
  mapboxgl.accessToken = 'pk.eyJ1IjoiYWlsYW56aGFuZyIsImEiOiJjbTMycjh3b28xMXg0MmlwcHd2ZmttZWYyIn0.T42ZxSkFvc05u3vfMT6Paw';
  this.map = new mapboxgl.Map({
      container: 'map',
      style: 'mapbox://styles/mapbox/light-v11',       
      center: { lng: 118.7497830, lat: 32.0527050 },  //南京鼓楼区
      zoom: 15.4,           //缩放级别
      pitch: 64.9,          // 倾斜角度
      bearing: 17.5,        // 旋转角度
      antialias: true 
  });

  //初始化DrawLine实例
  this.drawboard=new DrawBoard(this.map,this.billboardHeight,this.groundHeight);  //初始化绘制广告牌实例

  // 初始化Threebox
  this.tb = (window.tb = new window.Threebox(
        this.map,
        this.map.getCanvas().getContext('webgl'),
        {
            defaultLights: true
        },
        console.log("Threebox初始化完成")
    ));
  
},

methods:{
  // 加载GeoJSON数据
  loadGeojson(file){
    const reader=new FileReader();  
    reader.onload=(event)=>{
      const data=JSON.parse(event.target.result);
      console.log("GeoJSON数据加载完成", data);
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
          'fill-extrusion-color': '#000',  //黑色填充
          'fill-extrusion-height': ['to-number', ['get', 'height']],  // 确保转换为数值
          'fill-extrusion-base': 0,  // 设置建筑物的基础高度，通常为0
          'fill-extrusion-opacity': 0.9  // 设置建筑物的透明度
        }
      });
    }
    reader.readAsText(file);
  },
  // 打开文件窗口并加载geojson数据
  triggerFileInput(){
        this.$refs.fileInput.click();
    },
  handleFileSelect(event){
      const file=event.target.files[0];
      if(file && file.name.endsWith('.geojson')){
          console.log('加载GeoJSON文件', file);
          this.loadGeojson(file);
      }else{
          alert('请选择一个GeoJSON文件');
      }
  },

  // 加载Threebox模型
  addCustomThreeboxModel() {
    const map = this.map;
    const tb = this.tb;
    map.addLayer({
      id: 'custom-threebox-model',
      type: 'custom',
      renderingMode: '3d',
      onAdd: function () {
          console.log("开始加载Threebox模型....");
          const scale = 3.2;
          const options = {
              obj: 'https://docs.mapbox.com/mapbox-gl-js/assets/metlife-building.gltf',
              type: 'gltf',
              scale: { x: scale, y: scale, z: 2.7 },
              units: 'meters',
              rotation: { x: 90, y: -90, z: 0 }
          };
          tb.loadObj(options, (model) => {
              model.setCoords([118.7497830, 32.0527050 ]);
              model.setRotation({ x: 0, y: 0, z: 241 });
              tb.add(model);
              console.log("Threebox模型加载完成....");
          });
      },
      render: function () {
          tb.update();
      }
    });
  },

  // 显示浮动窗口(3维模型)
  toggleFloatWindow(){
    this.showFloatWindow=!this.showFloatWindow;
  },

  // 开始/停止绘制
  toggleDrawing(){
    this.isDrawing=!this.isDrawing;
    if(this.isDrawing){
      this.drawboard.startDrawing();
    }else{
      this.drawboard.stopDrawing();
    }
  },
  // 清除上一个广告牌
  clearLastBillboard(){
    this.drawboard.clearLastBillboard();
  },
  // 更新广告牌高度和距地面高度
  updateBillboardDimensions(){
    this.drawboard.updateBillboardHeight(this.billboardHeight,this.groundHeight);
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
  z-index: 0;  /*地图图层在最底层*/
}

.analysis-window {
  min-width: 320px;
  padding: 0px;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);

}

.button-group {
  display: flex;
  gap:10px;
  margin-bottom: 5px;
  padding: 10px;
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
  margin: 0px 10px 20px 10px;  /*上右下左*/
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
  box-shadow: 0 0 2px rgba(0,0,0,0.2);
}

.slider::-moz-range-thumb {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: #4CAF50;
  cursor: pointer;
  border: 2px solid white;
  box-shadow: 0 0 2px rgba(0,0,0,0.2);
}

</style>
