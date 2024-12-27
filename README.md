# 3D-City-Adv · 3D城市广告牌曝光分析系统
## [演示视频](https://www.bilibili.com/video/BV1pCCnYjEYq/?vd_source=012f01c73f97da5b9202e8ac4e57e620)
## [项目文档](项目文档.pdf)
## 运行项目
**前端**
```
cd front
npm install
npm run serve
```

**后端**
```
cd server
pip install -r requirements.txt
python app.py
```

## 项目结构
**前端**
```
src
├── App.vue
├── assets
│   ├── car.png                 街景查询logo
│   └── images                  存放街景图片
├── components
│   ├── FirstPersonView.vue     第一人称视角
│   ├── FloatWindow.vue         通用浮窗组件
│   └── StreetViewPopup.vue     街景查询弹窗
├── main.js
├── styles
│   ├── accessibility.css       可达性分析样式
│   ├── analysis.css            曝光分析样式
│   ├── neighbor.css            邻近分析样式
│   ├── poi.css                 POI分析样式
│   ├── settings.css            设置样式
│   └── sidebar.css             侧边栏样式
└── utils
    ├── Accessibility.js        可达性分析
    ├── DrawBoard.js            广告牌绘制
    ├── ExposureAnalysis.js     曝光分析
    ├── MapLayer.js             地图图层
    ├── NoiseRadiation.js       噪音辐射
    ├── POIanaysis.js           POI分析
    ├── StreetView.js           街景查询
    └── TimeAnalysis.js         24hGPS分析
```

**后端**
```
├── analysis
│   ├── exposure.py              曝光分析
│   ├── geometry.py              几何操作
│   ├── gps_info.py              查询GPS信息并生成热力图
│   └── shortest_path.py         生成最短路径
├── app.py
├── config
│   ├── database.py              数据库配置
│   └── db_data                  存放数据库数据
├── requirements.txt
└── scripts                      一些脚本（与启动项目无关）
    ├── create_db.py             
    ├── data                     
    ├── get_taxi_GPS.py
    ├── import_geojson.py
    └── import_gps.py
```