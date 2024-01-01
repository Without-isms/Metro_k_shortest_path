
from Line import Line
from Route import Route


class LineManager:
    lines = {}

    def add_line(self, line_number, new_station):
        if line_number in self.lines:
            self.lines[line_number].add_station(new_station)
        else:
            line = Line(line_number)
            line.add_station(new_station)
            self.lines[line_number] = line

    def print_line_info(self, line_number):
        print("Line: ", line_number)
        print("lines: ", end="")
        if line_number in self.lines:
            line = self.lines[line_number]
            for each_station in line.stations:
                print(each_station, end="->")
        print()

    def print_all_info(self):
        for each in self.lines:
            self.print_line_info(self.lines[each].line_number)
            print()
        print("Line count ", len(self.lines))

    def get_best_route(self, station_manager, from_station, to_station, lines):
        route = Route()
        route.from_stop = from_station.name
        route.to_stop = to_station.name
        route.start_index = from_station.index
        route.end_index = to_station.index
        route.stops = 9999
        if len(lines) == 0:
            route.stops = 9999
            return route
        else:
            for each_line in lines:
                line = self.lines[each_line]
                start_index = 0
                stop_index = 0
                find_start_index = False
                find_stop_index = False

                for i in range(0, len(line.stations)):
                    if line.stations[i].name == from_station.name:
                        start_index = i
                        find_start_index=True
                    if line.stations[i].name == to_station.name:
                        stop_index = i
                        find_stop_index=True
                    if find_start_index and find_stop_index:
                        break

                stops = abs(start_index - stop_index)

                if stops < route.stops:
                    route.stops = stops
                    route.line_number = line.line_number
                    # 清空之前的stations列表并添加新的站点
                    if start_index <= stop_index:
                        station_list = line.stations[start_index:stop_index + 1]
                    else:
                        station_list = line.stations[stop_index:start_index + 1][::-1]
                    for station in station_list:
                        route.stations.append(station_manager.stations[station.name])
        return route

    def print_stops(self, line_number, from_stop, to_stop):
        line = self.lines[line_number]
        start_index = 0
        end_index = 0
        stations = line.stations
        for i in range(0, len(stations)):
            if stations[i].name == from_stop:
                start_index = i
            elif stations[i].name == to_stop:
                end_index = i

        if start_index > end_index:
            start_printing = False
            for each in reversed(stations):
                if each.name == from_stop:
                    print(each.name, " -> ", end="")
                    start_printing = True
                elif each.name == to_stop:
                    print(each.name)
                    start_printing = False
                elif start_printing:
                    print(each.name, " -> ", end="")
        else:
            start_printing = False
            for each in stations:
                if each.name == from_stop:
                    print(each.name, " -> ", end="")
                    start_printing = True
                elif each.name == to_stop:
                    print(each.name)
                    start_printing = False
                elif start_printing:
                    print(each.name, " -> ", end="")

        print()


