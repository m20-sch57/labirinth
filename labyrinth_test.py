from LabyrinthEngine import Labyrinth, Player
from LabyrinthObjects.Vanilla import Legs, EmptyLocation, Outside, Wall, Hole, Gun, Bomb, Arsenal,\
    FirstAidPost, Bear, Treasure, Exit
from LabyrinthEngine import load_lrmap, load_lrsave


# # ------------------------------------------------
# locations_list = [Outside()]
# locations_list += [EmptyLocation() for _ in range(9)]
# locations_list[2] = Hole()
# locations_list[7] = Hole()
# locations_list[4] = Arsenal()
# locations_list[8] = FirstAidPost()
# locations_list[9] = Exit()
# locations_list.append(Wall(
#   (locations_list[1], 'right', locations_list[2]),
#   (locations_list[2], 'left', locations_list[1])
#                           ))
# locations_list.append(Wall(
#   (locations_list[6], 'right', locations_list[7]),
#   (locations_list[7], 'left', locations_list[6])
#                           ))
# for i in range(len(locations_list)):
#   locations_list[i].name = i
# # -------------------------------------------------
# adjacence_list = [{},
#                 {'up': 0, 'down': 5, 'right': 10, 'left': 0},
#                 {'up': 0, 'down': 6, 'right': 3, 'left': 10},
#                 {'up': 0, 'down': 7, 'right': 4, 'left': 2},
#                 {'up': 0, 'down': 8, 'right': 0, 'left': 3},
#                 {'up': 1, 'down': 0, 'right': 6, 'left': 0},
#                 {'up': 2, 'down': 9, 'right': 11, 'left': 5},
#                 {'up': 3, 'down': 0, 'right': 8, 'left': 11},
#                 {'up': 4, 'down': 0, 'right': 0, 'left': 7},
#                 {'up': 6, 'down': 0, 'right': 0, 'left': 0},
#                 {},
#                 {}]

# #
# # OutSide = 0
# # Arsenal = 4
# # FirsAidPost = 8
# # HOLES:  2↔7
# # ┌───┬───────────┐
# # │ 1 │ 2   3   4 │
# # │               │
# # │ 5   6 │ 7   8 │
# # └───┐   ├───────┘
# #     │ 9 │
# #     └───┘
# # HOLES:  2↔7
# # ARSENAL: 4
# # FIRST AID POST: 8
# # EXIT: 9
# #

# # -------------------------------------------------
# items_list = [Legs(), Gun(), Bomb(), Treasure()]
# # -------------------------------------------------
# player = Player('player #1')
# prey = Player('prey')
# players_list = [player]
# # -------------------------------------------------
# bear = Bear()
# NPCs_list = [bear]
# # -------------------------------------------------
# settings = {
#   'locations': [{} for _ in range(len(locations_list))],
#   'items': [{} for _ in range(len(items_list))],
#   'npcs': [{} for _ in range(len(NPCs_list))]
# }
# settings['locations'][2]['fall_to'] = 7
# settings['locations'][7]['fall_to'] = 2
# settings['items'][3]['is_true'] = True
# settings['items'][3]['position'] = 3
# settings['npcs'][0]['position'] = 4

# MyLab = Labyrinth(locations_list, items_list, NPCs_list, players_list, adjacence_list, settings, 'test')

def generate_labyrinth(users, savefile, loadfile='test'):
    return load_lrmap(loadfile, savefile, users)

def loadsave_labyrinth(savefile, loadfile='test'):
    return load_lrsave(loadfile, savefile)


debug = True
if __name__ == '__main__':
    MyLab = generate_labyrinth(['player #1'], 'test')   
    while True:
        print('\n')
        print('┌──────────────────────────────────────────────────────────┐')
        if debug:
            print('│Player position    :  {:<36}│'.format(str(MyLab.get_active_player().get_parent())))
            print('│Bear position      :  {:<36}│'.format(str(MyLab.get_objects(and_key = lambda x: isinstance(x, Bear))[0].get_parent())))
            print('│Treasure position  :  {:<36}│'.format(str(MyLab.get_objects(and_key = lambda x: isinstance(x, Treasure))[0].get_parent())))
            print('├──────────────────────────────────────────────────────────┤')
        print('\n'.join('│{:<19}:  {:<36}│'.format(str(k), str(v)) for k, v in MyLab.get_active_player().states.items()))
        print('└──────────────────────────────────────────────────────────┘')
        ats = MyLab.get_active_player_ats()
        ats[0:-1:4] = list(map(lambda x: '\n'+x, ats[0:-1:4]))
        print('; '.join(ats), end = '\n\n')
        msgs = MyLab.make_turn(input('(' + MyLab.get_active_player().get_username() + ') '))
        for player in msgs:
            print('\n'.join('[{}] - {}'.format(player, msg) for msg in msgs[player]))
