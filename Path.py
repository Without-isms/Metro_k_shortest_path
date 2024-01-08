import copy

class Path:

    def __init__(self):
        self.from_stop = ""
        self.to_stop = ""
        self.start_index=0
        self.end_index=0
        self.routes = []  # 初始化为实例变量
        self.station_visit_sequence_index=[]
        self.station_visit_sequence = []
        self.path_number = 0
        self.number_of_stations = 0
        self.number_of_transfers = 0

    def __lt__(self, other):
        # 无论何时，这个方法总是返回 False
        # 这意味着当 distance_plus_bias 相等时，插入顺序将被保留
        return False

    def add_path(self, route, path_or_not):
        new_path=copy.deepcopy(self)
        new_path.to_stop=route.to_stop
        new_path.end_index=route.end_index
        if (len(new_path.routes)==0):
            new_path.from_stop = route.from_stop
            new_path.start_index = route.start_index
            new_path.routes=[]
        new_path.routes.append(route)
        if path_or_not == False: #这个与下面的判断有点写重复了，有空可以重新修改一下
            new_path.station_visit_sequence = new_path.station_visit_sequence[:-1] + route.stations
            new_path.station_visit_sequence_index = new_path.station_visit_sequence_index[:-1] + [int(station.index) for
                                                                                                  station in
                                                                                                  route.stations]
        else:
            if new_path.station_visit_sequence_index[-1]!=route.start_index:
                new_path.station_visit_sequence = new_path.station_visit_sequence + route.stations
                new_path.station_visit_sequence_index = new_path.station_visit_sequence_index + [int(station.index) for
                                                                                                 station in
                                                                                                 route.stations]
            else:
                new_path.station_visit_sequence = new_path.station_visit_sequence[:-1] + route.stations
                new_path.station_visit_sequence_index = new_path.station_visit_sequence_index[:-1] + [int(station.index)
                                                                                                      for
                                                                                                      station in
                                                                                                      route.stations]

        return new_path




