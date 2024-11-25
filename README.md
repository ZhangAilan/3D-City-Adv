# 3D-City-Adv · 3D城市广告牌曝光分析系统
**目录**
- [运行项目](#运行项目)
- [参考论文](#参考论文)
- [实现功能](#实现功能)
- [原理介绍](#原理介绍)

![alt text](misc/demo.png)

## 运行项目
**前端**
```
cd front
npm install
npm run serve
```
或直接运行脚本(linux)
```
./1.sh
``` 

**后端**
```
cd server
pip install -r requirements.txt
python app.py
```

## 参考了这篇论文，按照论文思路实现
[1] Q. Yu, D. Feng, G. Li, Q. Chen, and H. Zhang, “AdvMOB: Interactive visual analytic system of billboard advertising exposure analysis based on urban digital twin technique,” Advanced Engineering Informatics, vol. 62, p. 102829, Oct. 2024, doi: 10.1016/j.aei.2024.102829.

## 实现的功能
- [x] 从数据库加载geojson建筑物数据，并以三维模型显示在mapbox底图上
- [x] 广告牌图层绘制并实时更新高度
- [x] 计算GEA(Ground Exposure Area)：地面曝光面积
- [x] 计算IA(Invisible Area)：建筑物遮挡区域
- [x] 计算VA(Visible Area)：可见区域

## 原理介绍
### GEA(Ground Exposure Area)：地面曝光面积计算
```
1. 计算广告牌中心点坐标、高度
2. 计算广告牌方向向量（顺时针90度）
3. 计算曝光区域圆心坐标、半径
```
**证明GEA为什么是圆形(来自论文中的证明过程)**
![alt text](misc/GEA.jpg)

### IA(Invisible Area)：建筑物遮挡区域计算