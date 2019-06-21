from labyrinth_engine import Location


class Arsenal(Location):
    def __init__(self):
        super().__init__()

        self.stayed = set()

    def set_settings(self, settings, *args):
        self.ENTER_MSG = settings['enter_msg']['ru']
        self.STAY_MSG = settings['stay_msg']['ru']

        self.labyrinth.main_event.add_trigger(self, self.main)

    def main(self):
        ammo = self.labyrinth.get_unique('ammo')
        for player in self.get_children('player'):
            ammo.reset_all(player)
            if player in self.stayed:
                self.labyrinth.send_msg(self.STAY_MSG, player, 5)
            else:
                self.labyrinth.send_msg(self.ENTER_MSG, player, 5)
        self.stayed = set(self.get_children('player'))
