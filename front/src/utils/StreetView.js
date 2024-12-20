class StreetView {
  constructor() {
    this.angles = [0, 90, 180, 270];
  }

  // 获取所有可用的图片坐标点
  getAvailablePoints() {
    try {
      const imageFiles = require.context('@/assets/images', false, /\.png$/);
      const points = new Set();
      
      imageFiles.keys().forEach(key => {
        const match = key.match(/(\d+\.\d+)_(\d+\.\d+)_\d+_0\.png$/);
        if (match) {
          points.add(`${match[1]}_${match[2]}`);
        }
      });

      return Array.from(points).map(point => {
        const [lng, lat] = point.split('_');
        return [lng, lat];
      });
    } catch (error) {
      console.error('获取可用坐标点失败:', error);
      return [];
    }
  }

  // 计算两点之间的距离
  calculateDistance(point1, point2) {
    const [lng1, lat1] = [parseFloat(point1[0]), parseFloat(point1[1])];
    const [lng2, lat2] = [parseFloat(point2[0]), parseFloat(point2[1])];
    
    return Math.sqrt(
      Math.pow(lng1 - lng2, 2) + 
      Math.pow(lat1 - lat2, 2)
    );
  }

  // 找到最近的坐标点
  findNearestPoint(clickedCoords) {
    const availablePoints = this.getAvailablePoints();
    
    if (availablePoints.length === 0) {
      return null;
    }

    let nearestPoint = availablePoints[0];
    let minDistance = this.calculateDistance(availablePoints[0], clickedCoords);

    availablePoints.forEach(point => {
      const distance = this.calculateDistance(point, clickedCoords);
      if (distance < minDistance) {
        minDistance = distance;
        nearestPoint = point;
      }
    });

    return nearestPoint;
  }

  // 获取指定坐标点和角度的图片URL
  getImageUrl(coordinates, angle) {
    if (!coordinates) return null;
    
    const [lng, lat] = coordinates;
    const filename = `${lng}_${lat}_${angle}_0.png`;
    
    try {
      return require(`@/assets/images/${filename}`);
    } catch (error) {
      console.error(`加载${angle}°图片失败:`, error);
      return null;
    }
  }

  // 获取所有角度的图片URL
  getAllImages(coordinates) {
    const urls = {};
    this.angles.forEach(angle => {
      urls[angle] = this.getImageUrl(coordinates, angle);
    });
    return urls;
  }
}

export default new StreetView(); 