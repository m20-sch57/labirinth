from Labyrinth.LS_CONSTS import *
from Labyrinth.game import LabyrinthObject as LO, ObjectID as OID


class EmptyLocation(LO):
    used = {}

    def main(self):
        next_active_player = self.labyrinth.get_next_active_player()

        if next_active_player.get_parent_id() == self.object_id:
            if next_active_player.get_object_id().number in self.used:
                self.used[next_active_player.get_object_id().number] += 1
                self.labyrinth.send_msg(ENTER_MSG, next_active_player.user_id)
            else:
                self.used[next_active_player.get_object_id().number] = 1
                self.labyrinth.send_msg(FIRST_ENTER_MSG, next_active_player.user_id)


class Outside(LO):
    pass

# TODO: To recode wall.
class Wall(LO):
    reverse_direction = {'up': 'down',
                         'down': 'up',
                         'left': 'right',
                         'right': 'left'}

    def __init__(self, arg):
        if type(arg) is list:
            new_arg = {}
            for arr in arg:
                d0 = new_arg.get(arr[0], {})
                d0[arr[2]] = arr[1]
                new_arg[arr[0]] = d0
                d1 = new_arg.get(arr[1], {})
                d1[self.reverse_direction[arr[2]]] = arr[0]
                new_arg[arr[1]] = d1
            arg = new_arg
        # behind_the_wall is list of dicts. For location with ID i on i-th place will be dict like
        # {'direction1': location_in_direction1_behind_wall, ...}.
        # So all list looks like [{'dir1': loc_in_dir1, ...}, ...].
        # loc_in_dir is integer (not location or ID) too.
        self.behind_the_wall = arg

    def break_wall(self, object_id_1, direction):
        if type(object_id_1) is not OID:
            raise ValueError('Invalid literal for break_wall()')
        object_id_2 = self.field.locations_list[self.behind_the_wall[object_id_1.number][direction]].get_object_id()
        self.field.adjacence_list[object_id_1.number][direction] = object_id_2.number
        self.field.adjacence_list[object_id_2.number][self.reverse_direction[direction]] = object_id_1.number
        del self.behind_the_wall[object_id_1.number][direction]
        del self.behind_the_wall[object_id_2.number][self.reverse_direction[direction]]

    def make_wall(self, object_id_1, direction):
        if type(object_id_1) is not OID:
            raise ValueError('Invalid literal for make_wall()')
        object_id_2 = self.field.get_neighbour_location_id(object_id_1, direction)
        num_1 = object_id_1.number
        num_2 = object_id_2.number
        self_num = self.get_object_id().number

        d1 = self.behind_the_wall.get(num_1, {})
        if direction in d1:
            raise ValueError('There is already wall between first room and some another in the direction')
        d1[direction] = num_2
        self.behind_the_wall[num_1] = d1
        self.field.adjacence_list[num_1][direction] = self_num

        d2 = self.behind_the_wall.get(num_2, {})
        if self.reverse_direction[direction] in d2:
            raise ValueError('There is already wall between second room and some another in the opposite direction')
        d2[self.reverse_direction[direction]] = num_1
        self.behind_the_wall[num_2] = d2
        self.field.adjacence_list[num_2][direction] = self_num


class Hole(LO):
    is_not_fall = set()

    def __init__(self, fall_to):
        self.fall_to = fall_to  # type is ObjectID
        self.new_at(function = self.go_into_hole, condition_function = self.condition, turn_name = INTO_TURN)

    def main(self):
        next_active_player = self.labyrinth.get_next_active_player()
        active_player = self.labyrinth.get_active_player()

        if active_player.get_parent_id() == self.get_object_id()\
                and active_player.get_object_id().number not in self.is_not_fall:
            active_player.set_parent_id(self.fall_to)
            if type(self.field.get_object(self.fall_to)) is Hole:
                self.is_not_fall.add(active_player.get_object_id().number)
            self.labyrinth.send_msg(FALL_MSG, active_player.user_id)

        if not type(self.field.get_object(next_active_player.get_parent_id())) is Hole:
            self.is_not_fall.discard(next_active_player.get_object_id().number)

    def go_into_hole(self):
        active_player = self.labyrinth.get_active_player()
        active_player.set_parent_id(self.fall_to)
        self.labyrinth.send_msg(TROUGH_HOLE_MSG, active_player.user_id)

    def condition(self):
        active_player = self.labyrinth.get_active_player()
        return active_player.get_parent_id() == self.get_object_id()


# TODO: To code classes of: treasure, river, outfall, arsenal, first-aid post and bear.
