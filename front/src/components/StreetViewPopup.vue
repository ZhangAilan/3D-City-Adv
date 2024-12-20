<template>
  <div class="street-view-container">
    <div class="street-view-header">
      <h3>街景照片</h3>
      <button class="close-btn" @click="handleClose">&times;</button>
    </div>
    <div class="street-view-content">
      <div class="coordinates-card">
        <div class="coordinate-group">
          <h4>点击位置</h4>
          <div class="coordinate-item">
            <span class="coordinate-label">经度</span>
            <span class="coordinate-value">{{ coordinates[0].toFixed(12) }}°E</span>
          </div>
          <div class="coordinate-item">
            <span class="coordinate-label">纬度</span>
            <span class="coordinate-value">{{ coordinates[1].toFixed(12) }}°N</span>
          </div>
        </div>
        
        <div class="coordinate-group" v-if="nearestPoint">
          <h4>最近街景点</h4>
          <div class="coordinate-item">
            <span class="coordinate-label">经度</span>
            <span class="coordinate-value">{{ nearestPoint[0] }}°E</span>
          </div>
          <div class="coordinate-item">
            <span class="coordinate-label">纬度</span>
            <span class="coordinate-value">{{ nearestPoint[1] }}°N</span>
          </div>
          <div class="distance-info">
            <span class="distance-label">距离</span>
            <span class="distance-value">{{ calculateDistance() }}</span>
          </div>
        </div>
      </div>
      
      <div class="street-view-grid">
        <div class="street-view-image" v-for="n in 4" :key="n">
          <img 
            v-if="imageUrls[angles[n-1]]"
            :src="imageUrls[angles[n-1]]"
            :alt="`街景照片 ${angles[n-1]}°`"
            @error="handleImageError(angles[n-1])"
          />
          <div v-else class="image-placeholder">
            {{ loadingError[angles[n-1]] ? '无法加载照片' : '等待加载街景照片' }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import StreetView from '@/utils/StreetView';

export default {
  name: 'StreetViewPopup',
  props: {
    coordinates: {
      type: Array,
      required: true
    }
  },

  data() {
    return {
      angles: [0, 90, 180, 270],
      imageUrls: {},
      loadingError: {},
      nearestPoint: null
    }
  },

  watch: {
    coordinates: {
      immediate: true,
      handler() {
        this.loadImages()
      }
    }
  },

  methods: {
    loadImages() {
      // 重置状态
      this.imageUrls = {};
      this.loadingError = {};

      // 找到最近的坐标点
      this.nearestPoint = StreetView.findNearestPoint(this.coordinates);
      
      if (!this.nearestPoint) {
        this.angles.forEach(angle => {
          this.loadingError[angle] = true;
        });
        return;
      }

      // 获取所有角度的图片
      this.imageUrls = StreetView.getAllImages(this.nearestPoint);
    },

    handleImageError(angle) {
      this.loadingError[angle] = true;
    },

    calculateDistance() {
      if (!this.nearestPoint) return '';
      
      const distance = StreetView.calculateDistance(this.nearestPoint, this.coordinates);
      // 将距离转换为米为单位，并保留2位小数
      const meters = (distance * 111000).toFixed(2); // 粗略转换，1度约等于111公里
      return `${meters} 米`;
    },

    handleClose() {
      this.$emit('close');
    }
  }
}
</script>

<style scoped>
.street-view-container {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.15);
  width: 460px;
  height: 400px;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
}

.street-view-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 20px;
  border-bottom: 1px solid #eee;
  background: #f8f8f8;
  border-radius: 8px 8px 0 0;
  flex-shrink: 0;
}

.street-view-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.street-view-content {
  padding: 16px;
  overflow-y: auto;
  flex-grow: 1;
}

.coordinates-card {
  background: #f8f9fa;
  border-radius: 6px;
  padding: 12px 16px;
  margin-bottom: 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.coordinate-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.coordinate-label {
  font-size: 14px;
  color: #666;
  font-weight: 500;
}

.coordinate-value {
  font-size: 16px;
  color: #333;
  font-weight: 600;
}

.street-view-grid {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 8px 0;
}

.street-view-image {
  width: 100%;
  height: 320px;
  background: #f5f5f5;
  border-radius: 6px;
  overflow: hidden;
}

.image-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #999;
  font-size: 14px;
  background: linear-gradient(45deg, #f5f5f5 25%, #efefef 25%, #efefef 50%, #f5f5f5 50%, #f5f5f5 75%, #efefef 75%);
  background-size: 20px 20px;
}

.close-btn {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  color: #666;
  padding: 0 4px;
  transition: color 0.2s;
}

.close-btn:hover {
  color: #000;
}

/* 优化滚动条样式 */
.street-view-content::-webkit-scrollbar {
  width: 6px;
}

.street-view-content::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.street-view-content::-webkit-scrollbar-thumb {
  background: #ccc;
  border-radius: 3px;
  &:hover {
    background: #999;
  }
}

.coordinate-group {
  background: #f8f9fa;
  border-radius: 6px;
  padding: 12px 16px;
  margin-bottom: 12px;
}

.coordinate-group h4 {
  margin: 0 0 8px 0;
  font-size: 14px;
  color: #666;
  font-weight: 600;
}

.distance-info {
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px dashed #ddd;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.distance-label {
  font-size: 14px;
  color: #666;
  font-weight: 500;
}

.distance-value {
  font-size: 14px;
  color: #333;
  font-weight: 600;
}

.coordinates-card {
  margin-bottom: 16px;
}

.coordinate-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}

.coordinate-label {
  font-size: 14px;
  color: #666;
}

.coordinate-value {
  font-size: 14px;
  color: #333;
  font-family: monospace;
}
</style> 