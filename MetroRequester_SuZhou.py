

import json
from StationManager import StationManager
from LineManager import LineManager
import os
import pandas as pd

# 路径可能需要根据实际情况调整
excel_path = r'C:\Users\SuperDoctorCat\Desktop\writing\Suzhou_zhandian.xlsx'

# 读取Excel文件
df = pd.read_excel(excel_path, header=None)
def request_suzhou_metro_data():# 创建StationManager和LineManager实例
    station_manager = StationManager()
    line_manager = LineManager()
    # 遍历数据帧
    station_index = 0
    for index, row in df.iterrows():
        if index == 0:  # 表头，包含线路编号
            line_numbers = row
            continue
        for line_number, station_name in zip(line_numbers, row):
            if station_name != 0 and station_name != '0':  # 忽略占位符
                # 向StationManager和LineManager添加数据
                ori_station_num = len(list(station_manager.stations.values()))
                station_manager.add_station(station_name, line_number, station_index)
                line_manager.add_line(line_number, station_manager.stations[station_name])
                if(ori_station_num<len(list(station_manager.stations.values()))):
                    station_index += 1
    for line_key, line_value in LineManager.lines.items():
        sequence_of_the_line = 0
        for station_of_the_line in line_value.stations:
            station_of_the_line.station_sequence_of_the_line = sequence_of_the_line
            station_manager.stations[station_of_the_line.name].station_sequence_of_the_line = sequence_of_the_line
            sequence_of_the_line += 1


    # 如果需要查看加载的信息
    station_manager.print_all_info()
    # 返回StationManager和LineManager
    return station_manager, line_manager
