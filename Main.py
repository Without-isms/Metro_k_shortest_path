from LineManager import LineManager
from StationManager import StationManager
import MetroRequester_SuZhou
import MetroRequester
from Route import Route
from Path import Path

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

for i in range(0, len(stations_list)):
    v_matrix.append([])
    for j in range(0, len(stations_list)):
        same_lines = get_same_lines(stations_list[i], stations_list[j])
        v_matrix[i].append(line_manager.get_best_route(station_manager, stations_list[i], stations_list[j], same_lines))

import heapq
import copy

while True:
    try:
        one_or_k = int(input("如果想运行原版代码，请输入1，如果想运行改进版代码，请输入2: "))

        if one_or_k in [1, 2]:
            break
        else:
            print("输入不正确，请输入1或2。")
    except ValueError:
        print("默认值为2")
        one_or_k = 2
        break

def dijkstra(v_matrix, start_index, end_index, bias):
    # 初始化距离和路径记录数组
    book = [0] * len(v_matrix)
    dis = []
    #dis = [(9999,Path()) for _ in range(len(v_matrix))]
    for i in range(0, len(v_matrix)):
        dis.append((v_matrix[start_index][i].stops, Path().add_path(v_matrix[start_index][i],False)))
    dis[start_index] = (0,Path())
    while True:
        # 找到未处理的最小距离顶点
        candidates = [(d, idx) for idx, (d, _) in enumerate(dis) if book[idx] == 0]
        if candidates:
            u = min(candidates)[1]
        else:
            break
        if dis[u][0] == 9999:#????
            break
        # 更新邻接顶点的距离
        for v in range(len(v_matrix[u])):
            if v==13:
                bbbb=1
            if not book[v]:
                if v_matrix[u][v].stops < 9999:
                    new_distance = dis[u][0] + v_matrix[u][v].stops + bias
                    if new_distance < dis[v][0]:
                        dis[v] = (new_distance, dis[u][1].add_path(v_matrix[u][v],False))
                elif v_matrix[u][v].stops == 9999:
                    continue#此路不通
        # 标记u为已处理
        book[u] = 1
    return dis[end_index]

def yen_ksp(start_station, terminal_station, k, v_matrix, bias, station_index, line_manager):
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
        for j in range(len(the_latest_added_path.routes) - 1):
            route_belongs_dif_line=the_latest_added_path.routes[j]
            for spur_node in route_belongs_dif_line.stations:
                spur_node_index = station_index[spur_node.name]
                paths_with_root = paths[-1].routes[:j + 1]
                root_path = Path()
                list_route_of_partial_root = []
                for route_with_partial_root in paths_with_root:
                    for station in route_with_partial_root.stations:
                        list_route_of_partial_root.append(station)
                        if station.name == spur_node.name:
                            break# 标记找到了spur_node
                    if(len(list_route_of_partial_root)>0):
                        route_of_partial_root=Route()
                        route_of_partial_root.construct_route(line_manager, station_manager, list_route_of_partial_root[0],
                                                              list_route_of_partial_root[-1], get_same_lines(list_route_of_partial_root[0],list_route_of_partial_root[-1]))
                        root_path=root_path.add_path(route_of_partial_root,False)
                original_v_matrix = copy.deepcopy(v_matrix)
                path_station_indices = [
                    (path_index, station_index)
                    for path_index, path in enumerate(paths)
                    for station_index, station in enumerate(path.station_visit_sequence)
                    if station.name == spur_node.name
                ]
                # 定位所有包含spur_node的path在paths中的index还有所有route在path.routes中的index
                # 之后找path中所有经过spur node的弧，找到它们的出点，让所有spur_node-出点的弧都不被经过
                # （此处需要注意，路过spur_node和出点但不以spur_node和出点为出发点的是不是也应该block
                spur_node_to_station_list = []
                for spur_node_to_path_sation_index in path_station_indices:
                    spur_node_to_station=paths[spur_node_to_path_sation_index[0]].station_visit_sequence[
                        spur_node_to_path_sation_index[1] + 1]
                    spur_node_to_station_list.append(spur_node_to_station)
                    for spur_node_to_station in spur_node_to_station_list:
                        # 找到v_matrix中含有spur_node到spur_node_to_index_list中所有点的弧，全部都赋值为9999
                        # 先识别spur_node到spur_node_to_index_list是正着的还是反着的，识别之后找到相应的线路，然后找到所有index符合的
                        same_line = get_same_lines(spur_node, spur_node_to_station)[0]
                        selected_line = line_manager.lines[same_line]
                        blocked_routes=[]
                        for from_stations in selected_line.stations:
                            for to_stations in selected_line.stations:
                                if spur_node.index > spur_node_to_station.index:  # 反着开
                                    if ((from_stations.index>=spur_node.index) & (to_stations.index<=spur_node_to_station.index)):
                                        blocked_routes.append((from_stations,to_stations))
                                elif spur_node.index < spur_node_to_station.index:
                                    if ((from_stations.index <= spur_node.index) & (to_stations.index >= spur_node_to_station.index)):
                                        blocked_routes.append((from_stations, to_stations))
                        for blocked_route in blocked_routes:
                            v_matrix[blocked_route[0].index][blocked_route[1].index].stops = 9999
                # 计算从spur_node到terminal的最短路径
                distance_plus_bias, spur_path = dijkstra(v_matrix, spur_node_index, terminal_index, bias)
                total_stops = sum(route.stops for route in spur_path.routes)
                if (total_stops < 9999) & (total_stops > 0):
                    new_path=copy.deepcopy(root_path)
                    for route_of_spur_path in spur_path.routes:
                        new_path=new_path.add_path(route_of_spur_path,True)
                    heapq.heappush(potential_k_paths, (distance_plus_bias, new_path))
                # 恢复原始图
                #解决下一个应该是从spurpath的最后一个节点出发
                v_matrix = original_v_matrix
        # 添加下一个最短路径
        if(potential_k_paths==[]):
            continue
        duplicate = True
        while duplicate:
            duplicate = False
            potential_new_path = heapq.heappop(potential_k_paths)[1]
            for path in paths:
                if path.station_visit_sequence_index == potential_new_path.station_visit_sequence_index:
                    duplicate=True
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

    def find_routes(one_or_k, start_station, terminal_station, v_matrix, bias, station_index, line_manager):
        start_index = station_index[start_station]
        terminal_index = station_index[terminal_station]
        n = len(stations_list)
        if one_or_k == 1:
            dis = []
            book = []
            for i in range(0, len(v_matrix)):
                dis.append((v_matrix[start_index][i].stops, [v_matrix[start_index][i]]))
                book.append(0)
            book[start_index] = 1

            for i in range(n - 1):
                min_and_route = (9999, [Route()])
                u = -1
                for j in range(0, n):
                    if book[j] == 0 and dis[j][0] < min_and_route[0]:
                        min_and_route = (dis[j][0], dis[j][1])
                        u = j
                if u == -1:  # No path found
                    break
                book[u] = 1
                for v in range(0, n):
                    if v_matrix[u][v].stops > 9999:
                        print("v_matrix[u][v].stops > 9999")
                    elif v_matrix[u][v].stops < 9999 and book[v] == 0:
                        new_stops = dis[u][0] + v_matrix[u][v].stops + bias
                        if dis[v][0] > new_stops:
                            new_route = dis[u][1].copy()
                            new_route.append(v_matrix[u][v])
                            dis[v] = (new_stops, new_route)

            print("Printing transfer solution")
            solution = dis[terminal_index][1]
            for each_route in solution:
                print_route_info(each_route, line_manager)

        elif one_or_k == 2:
            top_k_paths = yen_ksp(start_station, terminal_station, k, v_matrix, bias, station_index, line_manager)
            print("Top", k, "routes from", start_station, "to", terminal_station)
            route_number = 1
            for path in top_k_paths:
                print("Route number", route_number, ":")
                for each_route in path.routes:
                    print_route_info(each_route, line_manager)
                route_number += 1

    def print_route_info(each_route, line_manager):
        print("在 " + each_route.from_stop + " 乘坐 " + str(
            each_route.line_number) + "号线 到 " + each_route.to_stop + "(" + str(each_route.stops) + "站)")
        line_manager.print_stops(each_route.line_number, each_route.from_stop, each_route.to_stop)




    while True:
        # 获取用户选择执行手动输入还是自动遍历
        execution_mode = input("请输入 'hand' 执行手动输入，或 'auto' 执行自动遍历: ")

        if execution_mode == '' or execution_mode == 'hand':
            def get_valid_station_input(prompt, station_index):
                while True:
                    station_name = input(prompt)
                    if station_name in station_index:
                        return station_name
                    else:
                        print("输入的站点无效，请重新输入。")


            start_station = "劳动路"
            terminal_station = "宝带路"
            """
            start_station = get_valid_station_input("请输入起始站: ", station_index)
            terminal_station = get_valid_station_input("请输入终点站: ", station_index)
            """

            find_routes(one_or_k, start_station, terminal_station, v_matrix, bias, station_index, line_manager)

            break  # 退出循环
        elif execution_mode == 'auto':
            # 自动遍历流程
            for i in range(len(stations_list)):
                for j in range(len(stations_list)):
                    if i != j:
                        start_station = stations_list[i].name
                        terminal_station = stations_list[j].name
                        print(f"从 {start_station} 到 {terminal_station} 的路径。")
                        find_routes(one_or_k, start_station, terminal_station, v_matrix, bias, station_index,
                                    line_manager)
            break  # 退出循环
        else:
            print("输入无效，请输入 'hand' 或 'auto'。")


    start_index = station_index[start_station]
    terminal_index = station_index[terminal_station]






