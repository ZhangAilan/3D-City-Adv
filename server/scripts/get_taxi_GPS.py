'''
@zyh 2024-11-26
筛选出北京市东城区内的出租车GPS数据（点位数据）
已知大量出租车txt文件，每个txt文件中包含一个时间段内的出租车GPS数据
1,2008-02-02 15:36:08,116.51172,39.92123
已知北京东城区的geojson文件，筛选出位于该区域的出租车GPS数据
'''
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

def filter_taxi_GPS(txt_file, geojson_file, output_file):
    '''
    筛选出位于指定区域内的出租车GPS数据
    '''
    # 读取txt文件
    df = pd.read_csv(txt_file, header=None, names=['id', 'timestamp', 'longitude', 'latitude'])
    # 读取geojson文件
    gdf = gpd.read_file(geojson_file)
    # 将出租车GPS数据转换为GeoDataFrame
    taxi_gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.longitude, df.latitude))
    # 筛选出位于指定区域内的出租车GPS数据
    filtered_gdf = taxi_gdf[taxi_gdf.geometry.within(gdf.geometry.iloc[0])]
    # 保存结果
    # output_file: 输出文件路径
    # mode='a': 追加模式写入文件
    # index=False: 不保存DataFrame的索引
    # header=not bool(i-1): 仅在第一次写入时(i=1)添加表头,后续追加时不再添加表头
    filtered_gdf.to_csv(output_file, mode='a', index=False, header=not bool(i-1))


if __name__ == '__main__':
    #txt文件从1.txt到10357.txt
    #将所有筛选出的数据保存到一个csv文件中，还包含id,timestamp,longitude,latitude
    output_file = 'data/taxi_GPS.csv'
    geojson_file = 'data/beijing_dongcheng.geojson'
    for i in range(1, 10358):
        txt_file = f'data/taxi_GPS/{i}.txt'
        filter_taxi_GPS(txt_file, geojson_file, output_file)
        print(f'已处理{i}个txt文件')
    print('所有txt文件处理完毕')



