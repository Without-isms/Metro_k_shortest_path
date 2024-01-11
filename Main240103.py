from LineManager import LineManager
from StationManager import StationManager
import MetroRequester_SuZhou
import MetroRequester
from Route import Route
from Path import Path
import heapq
import copy

#station_manager, line_manager = MetroRequester.request_shanghai_metro_data()
station_manager, line_manager = MetroRequester_SuZhou.request_suzhou_metro_data()
stations_list = list(station_manager.stations.values())
station_index = station_manager.station_index
v_matrix = []

book = []
dis = []
# Initialize your StationManager and LineManager here
station_manager = StationManager()
line_manager = LineManager()

def get_same_lines(from_station, to_station):
    line_numbers = []
    for each_line in from_station.lines:
        if each_line in to_station.lines:
            line_numbers.append(each_line)
    return line_numbers

"""
class TrackableList(list):
    def append(self, item):
        print(f"Appending to list: {item}")
        super().append(item)
    def __setitem__(self, index, item):
        print(f"Setting item at index {index}: {item}")
        super().__setitem__(index, item)
"""



def dijkstra(v_matrix, start_index, end_index, bias):
    # 初始化距离和路径记录数组
    book = [0] * len(v_matrix)
    dis = []
    for i in range(0, len(v_matrix)):
        dis.append((v_matrix[start_index][i].stops, Path().add_path(v_matrix[start_index][i])))
    dis[start_index] = (0,Path())
    while True:
        # 找到未处理的最小距离顶点
        candidates = [(d, idx) for idx, (d, _) in enumerate(dis) if book[idx] == 0]
        if candidates:
            u = min(candidates)[1]
        else:
            break
        if dis[u][0] == 9999:
            break
        # 更新邻接顶点的距离
        for v in range(len(v_matrix[u])):
            if not book[v]:
                if v_matrix[u][v].stops < 9999:
                    new_distance = dis[u][0] + v_matrix[u][v].stops + bias
                    if new_distance < dis[v][0]:
                        dis[v] = (new_distance, dis[u][1].add_path(v_matrix[u][v]))
                elif v_matrix[u][v].stops == 9999:
                    continue#此路不通
        # 标记u为已处理
        book[u] = 1
    return dis[end_index]

def yen_ksp(start_station, terminal_station, k, v_matrix, bias, station_index, line_manager):
    original_v_matrix = copy.deepcopy(v_matrix)
    start_index = station_index[start_station]
    terminal_index = station_index[terminal_station]
    # 初始最短路径
    distance, first_path = dijkstra(v_matrix, start_index, terminal_index, bias)
    paths = [first_path]
    potential_k_paths = []

    def contains_subsequence(sequence, subsequence):
        """检查 sequence 是否包含与 subsequence 相同且顺序一致的子序列"""
        sub_len = len(subsequence)
        for i in range(len(sequence) - sub_len + 1):
            if sequence[i:i + sub_len] == subsequence:
                return True
        return False

    for i in range(1, k):
        the_latest_added_path=paths[-1]
        for j in range(len(the_latest_added_path.routes) - 1): #生成一个从0到n-1的整数序列
            route_belongs_dif_line=the_latest_added_path.routes[j]
            for spur_node in route_belongs_dif_line.stations:
                spur_node_index = station_index[spur_node.name] #这样的话，route头尾的站会被选择两次
                route_list_contains_root_path = the_latest_added_path.routes[:j + 1] #从列表 routes 中获取从开始（索引0）到 j+1（不包括索引为 j+1 的元素）的所有元素
                root_path = Path()
                for route_with_partial_root in route_list_contains_root_path:
                    list_route_of_partial_root = []
                    for station in route_with_partial_root.stations:
                        list_route_of_partial_root.append(station)
                        if station.name == spur_node.name:
                            break# 标记找到了spur_node
                    if(len(list_route_of_partial_root)>1):
                        route_of_partial_root = Route()
                        route_of_partial_root.construct_route(line_manager, station_manager, list_route_of_partial_root[0],
                                                              list_route_of_partial_root[-1], get_same_lines(list_route_of_partial_root[0],list_route_of_partial_root[-1]))
                        root_path=root_path.add_path(route_of_partial_root)
                spur_nodes_indices_in_stations_and_paths = [
                    (spur_nodes_path_index, spur_nodes_station_index)
                    for spur_nodes_path_index, path in enumerate(paths)
                    for spur_nodes_station_index, station in enumerate(path.station_visit_sequence)
                    if station.name == spur_node.name
                ]
                # 定位所有包含spur_node的path在paths中的index还有所有route在path.routes中的index
                # 之后找path中所有经过spur node的弧，找到它们的出点，让所有spur_node-出点的弧都不被经过
                # （此处需要注意，路过spur_node和出点但不以spur_node和出点为出发点的是不是也应该block
                spur_node_to_station_list = []
                for spur_node_to_path_station_index in spur_nodes_indices_in_stations_and_paths:
                    spur_node_to_station=paths[spur_node_to_path_station_index[0]].station_visit_sequence[
                        spur_node_to_path_station_index[1] + 1]
                    spur_node_to_station_list.append(spur_node_to_station)
                    for spur_node_to_station in spur_node_to_station_list:
                        # 找到v_matrix中含有spur_node到spur_node_to_index_list中所有点的弧，全部都赋值为9999
                        # 先识别spur_node到spur_node_to_index_list是正着的还是反着的，识别之后找到相应的线路，然后找到所有index符合的
                        same_line = get_same_lines(spur_node, spur_node_to_station)[0]
                        selected_line = line_manager.lines[same_line]
                        blocked_routes=[]
                        for from_stations in selected_line.stations:
                            for to_stations in selected_line.stations:
                                if spur_node.station_sequence_of_the_line > spur_node_to_station.station_sequence_of_the_line:  # 反着开
                                    if ((from_stations.station_sequence_of_the_line>=spur_node.station_sequence_of_the_line) & (to_stations.station_sequence_of_the_line<=spur_node_to_station.station_sequence_of_the_line)):
                                        blocked_routes.append((from_stations,to_stations))
                                elif spur_node.station_sequence_of_the_line < spur_node_to_station.station_sequence_of_the_line:
                                    if ((from_stations.station_sequence_of_the_line <= spur_node.station_sequence_of_the_line) & (to_stations.station_sequence_of_the_line >= spur_node_to_station.station_sequence_of_the_line)):
                                        blocked_routes.append((from_stations, to_stations))
                        for blocked_route in blocked_routes:
                            v_matrix[blocked_route[0].index][blocked_route[1].index].stops = 9999
                # 计算从spur_node到terminal的最短路径
                distance_plus_bias, spur_path = dijkstra(v_matrix, spur_node_index, terminal_index, bias)
                total_stops = sum(route.stops for route in spur_path.routes)
                if (total_stops < 9999) & (total_stops > 0):
                    new_path=copy.deepcopy(root_path)
                    for route_of_spur_path in spur_path.routes:
                        new_path=new_path.add_path(route_of_spur_path)
                    heapq.heappush(potential_k_paths, (distance_plus_bias, new_path))
                # 恢复原始图
                v_matrix = copy.deepcopy(original_v_matrix)

        # 添加下一个最短路径
        if(potential_k_paths==[]):
            continue
        duplicate_or_loop = True
        while duplicate_or_loop:
            duplicate_or_loop = False
            if (potential_k_paths == []):
                continue
            potential_new_path = heapq.heappop(potential_k_paths)[1]
            for path in paths:
                if path.station_visit_sequence_index == potential_new_path.station_visit_sequence_index:
                    duplicate_or_loop = True
                    break
            if len(set(potential_new_path.station_visit_sequence_index)) < len(
                    potential_new_path.station_visit_sequence_index):
                duplicate_or_loop = True
            if duplicate_or_loop==False:
                paths.append(potential_new_path)
    return paths


if __name__ == '__main__':
    def get_input_or_default(prompt, default):
        while True:
            user_input = input(prompt)
            if user_input == "":
                return default
            try:
                return int(user_input)
            except ValueError:
                print("请输入一个有效的数字，或直接回车使用默认值。")
    k = get_input_or_default("请输入要查询的路线数目 K (默认值为 3，直接回车使用默认值): ", 3)
    bias = get_input_or_default("换乘一次与坐几站花费的时间等价？ bias (默认值为 3，直接回车使用默认值): ", 3)

    for i in range(0, len(stations_list)):
        v_matrix.append([])
        for j in range(0, len(stations_list)):
            same_lines = get_same_lines(stations_list[i], stations_list[j])
            new_route = Route()
            new_route.construct_route(line_manager, station_manager, stations_list[i], stations_list[j], same_lines)
            v_matrix[i].append(new_route)

    """
    v_matrix = TrackableList()
    for i in range(0, len(stations_list)):
        v_matrix.append(TrackableList())
        for j in range(0, len(stations_list)):
            same_lines = get_same_lines(stations_list[i], stations_list[j])
            new_route = Route()
            new_route._track_changes = True
            new_route.construct_route(line_manager, station_manager, stations_list[i], stations_list[j], same_lines)
            v_matrix[i].append(new_route)
    """

    def find_routes(exist_path_number, OD_path_dic, section_path_dic, path_section_dic, start_station, terminal_station, v_matrix, bias, station_index, line_manager):
        top_k_paths = yen_ksp(start_station, terminal_station, k, v_matrix, bias, station_index, line_manager)
        print("Top", k, "routes from", start_station, "to", terminal_station)
        paths_info = []
        for path in top_k_paths:
            path_info = {
                "path_number": exist_path_number,
                "from_stop": path.from_stop,
                "to_stop": path.to_stop,
                "start_index": path.start_index,
                "end_index": path.end_index,
                "routes": path.routes,
                "station_visit_sequence_index": path.station_visit_sequence_index,
                "station_visit_sequence": path.station_visit_sequence,
                "number_of_stations": path.number_of_stations,
                "number_of_transfers": path.number_of_transfers,
            }
            paths_info.append(path_info)
            print("Path number", exist_path_number, ":")
            for each_route in path.routes:
                print_route_info(each_route, line_manager)
                for sta_index in range(len(each_route.stations)-1):
                    station_name_pair_keys = (each_route.stations[sta_index].name,each_route.stations[sta_index+1].name)
                    station_pair_values = (each_route.stations[sta_index], each_route.stations[sta_index + 1])
                    if exist_path_number in path_section_dic:
                        path_section_dic[exist_path_number].append(station_pair_values)
                    else:
                        path_section_dic[exist_path_number] = [station_pair_values]
                    if station_name_pair_keys in section_path_dic:
                        section_path_dic[station_name_pair_keys].append(path_info)
                    else:
                        section_path_dic[station_name_pair_keys] = [path_info]
            exist_path_number += 1
            # 将路径信息保存到字典中
        OD_path_dic[(start_station, terminal_station)] = paths_info
        return exist_path_number, OD_path_dic, section_path_dic, path_section_dic


    def print_route_info(each_route, line_manager):
        print("在 " + each_route.from_stop + " 乘坐 " + str(
            each_route.line_number) + "号线 到 " + each_route.to_stop + "(" + str(each_route.stops) + "站)")
        line_manager.print_stops(each_route.line_number, each_route.from_stop, each_route.to_stop)

    while True:
        # 获取用户选择执行手动输入还是自动遍历
        execution_mode = input("请输入 'hand' 执行手动输入，或 'auto' 执行自动遍历: ")
        exist_path_number = 1
        OD_path_dic = {}
        section_path_dic = {}
        path_section_dic = {}
        if execution_mode == '' or execution_mode == 'hand':
            def get_valid_station_input(prompt, station_index):
                while True:
                    station_name = input(prompt)
                    if station_name in station_index:
                        return station_name
                    else:
                        print("输入的站点无效，请重新输入。")
            start_station = get_valid_station_input("请输入起始站: ", station_index)
            terminal_station = get_valid_station_input("请输入终点站: ", station_index)
            print(f"====================从 {start_station} 到 {terminal_station} 的路径。====================")
            exist_path_number, OD_path_dic, section_path_dic, path_section_dic = (
                find_routes(exist_path_number, OD_path_dic, section_path_dic, path_section_dic, start_station,
                            terminal_station, v_matrix, bias, station_index, line_manager))
            break  # 退出循环
        elif execution_mode == 'auto':
            # 自动遍历流程
            for i in range(len(stations_list)):
                for j in range(len(stations_list)):
                    if i != j:
                        v_matrix_ori = copy.deepcopy(v_matrix)
                        start_station = stations_list[i].name
                        terminal_station = stations_list[j].name
                        print(f"====================从 {start_station} 到 {terminal_station} 的路径。====================")
                        exist_path_number, OD_path_dic, section_path_dic, path_section_dic = (
                            find_routes(exist_path_number, OD_path_dic, section_path_dic, path_section_dic, start_station, terminal_station, v_matrix_ori, bias, station_index, line_manager))
        else:
            print("输入无效，请输入 'hand' 或 'auto'。")


    start_index = station_index[start_station]
    terminal_index = station_index[terminal_station]


