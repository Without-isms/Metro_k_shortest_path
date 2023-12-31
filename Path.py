import copy

class Path:

    def __init__(self):
        self.from_stop = ""
        self.to_stop = ""
        self.start_index=0
        self.end_index=0
        self.routes = []  # 初始化为实例变量
        self.station_visit_sequence_route=[]
        self.station_visit_sequence = []

    def add_path(self, route):
        new_path=copy.deepcopy(self)
        new_path.to_stop=route.to_stop
        new_path.end_index=route.end_index
        new_path.routes.append(route)
        if len(new_path.station_visit_sequence_route)==0:
            new_path.station_visit_sequence_route = route
            new_path.from_stop = route.from_stop
            new_path.start_index = route.start_index
            new_path.station_visit_sequence_route=[route]
        else:
            new_path.station_visit_sequence_route = new_path.station_visit_sequence_route + [route]
        new_path.station_visit_sequence=new_path.station_visit_sequence+route.stations
        return new_path


