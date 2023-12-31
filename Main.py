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

for i in range(0, len(stations_list)):
    v_matrix.append([])
    for j in range(0, len(stations_list)):
        same_lines = station_manager.get_same_lines(stations_list[i], stations_list[j])
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

def dijkstra(v_matrix, start, end, bias):
    # 初始化距离和路径记录数组
    dis = [(9999,Path()) for _ in range(len(v_matrix))]
    dis[start] = (0,Path())
    book = [0] * len(v_matrix)
    while True:
        # 找到未处理的最小距离顶点
        u = min((d, idx) for idx, (d, _) in enumerate(dis) if book[idx] == 0)[1]
        if u == end or dis[u][0] == 9999:#如果u是终止点或u是还未到达的点（dis[u][0] == 9999）
            break
        # 更新邻接顶点的距离
        for v in range(len(v_matrix[u])):
            if not book[v]:
                if v_matrix[u][v].stops < 9999:
                    new_distance = dis[u][0] + v_matrix[u][v].stops
                    bbbb=1
                    if new_distance < dis[v][0]:
                        dis[v] = (new_distance, dis[u][1].add_path(v_matrix[u][v]))
                elif v_matrix[u][v].stops == 9999:
                    continue#此路不通


        # 标记u为已处理
        book[u] = 1
    return dis[end]

def yen_ksp(start_station, terminal_station, k, v_matrix, bias, station_index):
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
                new_root_path = []
                found_spur_node = False  # 用于标记是否找到了spur_node
                for route_with_partial_root in paths_with_root:
                    route_of_partial_root=[]
                    if found_spur_node:
                        break  # 如果已经找到spur_node，跳出外部循环
                    for station in route_with_partial_root.stations:
                        if station.name == spur_node.name:
                            found_spur_node = True  # 标记找到了spur_node
                            break  # 找到后跳出内部循环
                        route_of_partial_root.append(station)
                    new_root_path.append(route_of_partial_root)
                root_path = new_root_path
                original_v_matrix = copy.deepcopy(v_matrix)
                for path in paths:
                    exists_or_not = any(
                        any(station.name == spur_node.name for station in route.stations)
                        for path in paths
                        for route in path.routes
                    )
                    #找到path集合里面所有path是否包括spur node，之后找path中所有经过spur node的弧，找到它们的出点，让所有spur_node-出点的弧都不被经过
                    # （此处需要注意，路过spur_node和出点但不以spur_node和出点为出发点的是不是也应该block
                    if len(path.routes) > j and exists_or_not:
                        spur_node_to_index = station_index[path.routes[j].to_stop]
                        # v_matrix中含有南门-乐桥的部分的弧全部都赋值为9999
                        #把line中的station改为Station对象
                        matching_elements = v_matrix[spur_node_to_index]
                        for matching_element in matching_elements:
                            blocked_route_to_stop = matching_element.to_stop
                            v_matrix[spur_node_to_index][station_index[blocked_route_to_stop]].stops = 9999
                # 计算从spur_node到terminal的最短路径
                _, spur_path = dijkstra(v_matrix, spur_node_index, terminal_index, bias)
                total_stops = sum(route.stops for route in spur_path.routes)
                if total_stops < 9999 & total_stops > 0:
                    total_path = root_path + spur_path
                    heapq.heappush(potential_k_paths, (len(total_path), total_path))
                # 恢复原始图
                v_matrix = original_v_matrix
        # 添加下一个最短路径
        if(potential_k_paths==[]):
            continue
        paths.append(heapq.heappop(potential_k_paths)[1])
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
            print("Calculating using Dijkstra")
            dis = []
            book = []
            for i in range(0, len(v_matrix)):
                dis.append((v_matrix[start_index][i].stops, [v_matrix[start_index][i]]))
                book.append(0)
            book[start_index] = 1

            for i in range(n - 1):
                min = (9999, [Route()])
                u = -1
                for j in range(0, n):
                    if book[j] == 0 and dis[j][0] < min[0]:
                        min = (dis[j][0], dis[j][1])
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
            top_k_paths = yen_ksp(start_station, terminal_station, k, v_matrix, bias, station_index)
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
            """
            start_station = get_valid_station_input("请输入起始站: ", station_index)
            terminal_station = get_valid_station_input("请输入终点站: ", station_index)
            """
            start_station = "南门"
            terminal_station = "广济南路"

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






