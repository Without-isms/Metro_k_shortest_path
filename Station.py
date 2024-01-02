



class Station:

    name = ""
    lines = []
    index = 0
    station_sequence_of_the_line = 0

    def __init__(self, name, index):
        self.name = name
        self.lines = []
        self.index = index

    def add_line(self, line_number):
        self.lines.append(line_number)


