from Labyrinth.LS_CONSTS import *
from Labyrinth.game import LabyrinthObject as LO, ObjectID
from Labyrinth.LS_locations import Wall, Outside


class Legs(LO):
    def __init__(self):
        self.new_at(self.turn_move('up'), condition_function = self.condition, turn_name = UP_TURN)
        self.new_at(self.turn_move('down'), condition_function = self.condition, turn_name = DOWN_TURN)
        self.new_at(self.turn_move('right'), condition_function = self.condition, turn_name = RIGHT_TURN)
        self.new_at(self.turn_move('left'), condition_function = self.condition, turn_name = LEFT_TURN)

    def turn_move(self, direction):
        def move():
            active_player = self.labyrinth.get_active_player()
            next_position = self.field.get_neighbour_location(active_player.get_parent_id(), direction)
            if type(next_position) in [Wall, Outside]:
                self.labyrinth.send_msg(WALL_MSG, active_player.get_user_id())
            else:
                active_player.set_parent_id(next_position.get_object_id())
        return move

    def condition(self):
        return True


class Gun(LO):
    def __init__(self):
        self.new_at(self.turn_fire('up'), self.condition, FIRE_UP)
        self.new_at(self.turn_fire('down'), self.condition, FIRE_DOWN)
        self.new_at(self.turn_fire('left'), self.condition, FIRE_LEFT)
        self.new_at(self.turn_fire('right'), self.condition, FIRE_RIGHT)

    def turn_fire(self, direction):
        def fire():
            active_player = self.labyrinth.get_active_player()
            active_player.states['count_of_bullets'] -= 1

            kicked_players = set()
            met_locations = set()
            current_location_id = active_player.get_parent_id()

            if CAN_PLAYER_HURT_EVB_IN_SAME_LOC:
                kicked_players |= set(self.field.get_players_in_location(current_location_id))

            current_location_id = self.field.get_neighbour_location_id(current_location_id, direction)
            while current_location_id.number not in met_locations\
                    and type(self.field.locations_list[current_location_id.number]) not in [Wall, Outside]:
                met_locations.add(current_location_id.number)
                kicked_players |= set(self.field.get_players_in_location(current_location_id))
                current_location_id = self.field.get_neighbour_location_id(current_location_id, direction)

            if not CAN_PLAYER_HURT_HIMSELF:
                kicked_players.discard(active_player)
            for player in kicked_players:
                player.hurt()
            self.labyrinth.active_player_number = active_player.get_object_id().number

            if kicked_players:
                self.labyrinth.send_msg(FIRE_SUCCESS_MSG
                                        + ', '.join(list(map(lambda pl: pl.user_id, kicked_players)))
                                        + '.', active_player.user_id)
            else:
                self.labyrinth.send_msg(FIRE_FAILURE_MSG, active_player.user_id)
        return fire

    def condition(self):
        active_player = self.labyrinth.get_active_player()
        return bool(active_player.states['count_of_bullets'])

# TODO: To add message for Outside and remake message for only 1 player.
class Bomb(LO):
    def __init__(self):
        self.new_at(self.turn_blow_up('up'), self.condition, BLOW_UP_UP)
        self.new_at(self.turn_blow_up('down'), self.condition, BLOW_UP_DOWN)
        self.new_at(self.turn_blow_up('left'), self.condition, BLOW_UP_LEFT)
        self.new_at(self.turn_blow_up('right'), self.condition, BLOW_UP_RIGHT)

    def turn_blow_up(self, direction):
        def blow_up():
            active_player = self.labyrinth.get_active_player()
            active_player.states['count_of_bombs'] -= 1

            current_location_id = active_player.get_parent_id()
            location_in_direction = self.field.get_neighbour_location(current_location_id, direction)
            if type(location_in_direction) is Wall:
                location_in_direction.break_wall(current_location_id, direction)
                self.labyrinth.send_msg(BLOW_UP_SUCCESS_MSG, active_player.user_id)
            elif type(location_in_direction) is not Outside:
                players_in_direction = self.field.get_players_in_location(location_in_direction.get_object_id())
                if CAN_PLAYER_HURT_EVB_IN_DIRECTION and players_in_direction:
                    self.labyrinth.send_msg(BLOW_UP_INJURING_MSG
                                            + ', '.join(list(map(lambda pl: pl.user_id, players_in_direction)))
                                            + '.', active_player.user_id)
                    for player in players_in_direction:
                        player.hurt()
                else:
                    self.labyrinth.send_msg(BLOW_UP_FAILURE_MSG, active_player.user_id)
        return blow_up

    def condition(self):
        active_player = self.labyrinth.get_active_player()
        return bool(active_player.states['count_of_bombs'])
