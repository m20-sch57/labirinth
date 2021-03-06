﻿from labyrinth_engine import Location


class Outside(Location):
    def set_settings(self, *args):
        self.set_flag('border')
        self.labyrinth.set_unique(self, 'outside')


class Wall(Location):
    def __init__(self):
        super().__init__()

        self.set_flag('border')

    def break_wall(self):
        for loc in self.labyrinth.get_objects('location'):
            for direction in loc.directions:
                if self == loc.get_neighbour(direction):
                    if direction in self.directions:
                        loc.set_neighbour(direction, self.get_neighbour(direction))
                    else:
                        outside = self.labyrinth.get_unique('outside')
                        loc.set_neighbour(direction, outside)
