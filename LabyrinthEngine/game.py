﻿from copy import copy
from LabyirnthConsts.Basic.CONSTS import *
import json


def get_attr_safe(obj, attr, default_value):
	if hasattr(obj, attr):
		return obj.__dict__[attr]
	else:
		return default_value

# TODO: issue #30
def load_lrsave(filename):
	pass

def load_lrmap(filename, users):
	pass


class LabyrinthObject:
	'''
	LabyrinthObject is class of objects that can be used by players at their turns
	'''

	def new_at(self, function, condition_function, turn_name):
		'''
		new available turn
		'''

		if hasattr(self, 'turn_set'):
			self.turn_set[turn_name] = {
				'function': function, 'condition': condition_function}
		else:
			self.turn_set = {turn_name: {
				'function': function, 'condition': condition_function}}

	def set_parent(self, parent):
		if not isinstance(parent, LabyrinthObject):
			raise ValueError(
				'Invalid type of "parent" argument for LabyrinthObject.set_parent: ' + str(type(parent)))
		else:
			self.parent = parent

	def get_parent(self):
		return get_attr_safe(self, 'parent', None)

	def get_children(self, labtype=['location', 'item', 'player', 'NPC'], and_key=lambda x: True, or_key=lambda x: False):
		all_objs = self.labyrinth.get_all_objects()
		return set(filter(lambda obj: obj.get_parent() == self and (obj.type in labtype and and_key(obj) or or_key(obj)),
						all_objs))

	def get_neighbour(self, direction):
		if self.type != 'location':
			raise TypeError(
				'You can\'t get neighbour for object with type ' + self.type)
		elif direction not in self.directions:
			raise ValueError(
				'Invalid "direction" argument for LabyrinthObject.get_neighbour: ' + str(direction))
		else:
			return self.directions[direction]

	def set_neighbour(self, direction, neighbour):
		if self.type != 'location':
			raise TypeError(
				'You can\'t set neighbour for object with type ' + self.type)
		elif not isinstance(neighbour, LabyrinthObject):
			raise ValueError(
				'Invalid "neighbour" argument for LabyrinthObject.set_neighbour: ' + str(neighbour))
		else:
			self.directions[direction] = neighbour

	def get_turn_set(self):
		return get_attr_safe(self, 'turn_set', {})

	@property
	def type(self):
		return self._type

	def main(self):
		'''
		Основная функция объекта. Определяется здесь, чтобы потом не было ошибки при её вызове.
		'''
		pass

	def get_name(self):
		return get_attr_safe(self, 'name', '')

	def __str__(self):
		return '<{}: {}: {}>'.format(self.type, self.__class__.__name__, self.get_name())

	def __repr__(self):
		return '<{}: {}: {}>'.format(self.type, self.__class__.__name__, self.get_name())


class Labyrinth:
	def __init__(self, locations, items, NPCs, players, adjacence_list, filename, dead_players=[]):
		for i in range(len(locations)):
			locations[i].directions = {
				direction: locations[k] for direction, k in adjacence_list[i].items()}
		for player in players:
			player.states = copy(INITIAL_STATES)
		for player in dead_players:
			player._type = 'dead_player'

		for obj in locations + items + NPCs + players:
			obj.labyrinth = self

		self.locations = set(locations)
		self.items = set(items)
		self.NPCs = set(NPCs)
		self.players_list = players
		self.dead_players = set(dead_players)

		self.to_send = {player.get_username(): [] for player in self.players_list}
		self.active_player_number = 0

		self.filename = filename

		'''
		turns_log
		[{'player': first_player_name, 'turn': his_turn}, {'player': second_player_name, 'turn': his_turn}, ...]
		msgs_log
		{player_name: [first_msg, second_msg, ...]}
		'''
		self.turns_log = []
		self.msgs_log = {}

		# Временное решение.
		# Если True, то всё сохраняется
		self.save_mode = True

	def __str__(self):
		return '<labyrinth: {}>'.format(self.filename)

	def send_msg(self, msg, player):
		self.to_send[player.get_username()].append(msg)

	def make_turn(self, turn):
		'''
		Вызвать эту функцию, если активный игрок сделал ход turn

		to_send: словарь сообщения для отправки.
		{username1: msg1, ... , username_n: msg_n}
		'''

		# обнуляем to_send
		self.to_send = {player.get_username(): [] for player in self.players_list}

		# В списке возможных ходов локаций и предметов ищем ход с именем turn
		# и запускаем действия найденных локаций и предметов
		to_do = []
		for obj in self.get_all_objects():
			if turn in obj.get_turn_set() and obj.get_turn_set()[turn]['condition']():
				to_do.append(obj.get_turn_set()[turn]['function'])
		for function in to_do:
			function()

		# Запускаем для всех объектов main-функцию
		for obj in self.get_all_objects():
			obj.main()

		# Делаем слудующего игрока активным
		self.active_player_number += 1
		self.active_player_number %= len(self.players_list)

		# обновляем лог ходов
		self.turns_log.append({'username': self.get_active_player_username(), 'turn': turn})
		# обновляем лог сообщений
		for username in self.to_send:
			if username in self.msgs_log:
				self.msgs_log[username].append(self.player_to_send(username))
			else:
				self.msgs_log[username] = [self.player_to_send(username)]
		# если save_mode == True, сохраняем всё в файл tmp\test.log
		if self.save_mode == True:
			self.save(self.filename)

		# возвращаем все сообщения, которые нужно отправить
		return self.to_send

	def get_next_active_player(self):
		return self.players_list[(self.active_player_number + 1) % len(self.players_list)]

	def get_active_player(self):
		return self.players_list[self.active_player_number]

	def get_active_player_username(self):
		return self.get_active_player().get_username()

	def get_active_player_ats(self):
		'''
		Возвращает возможные для активного игрока ходы
		'''

		active_player_ats = []
		for obj in self.get_all_objects():
			for turn in obj.get_turn_set():
				if obj.get_turn_set()[turn]['condition']():
					active_player_ats.append(turn)

		return active_player_ats

	def get_all_objects(self):
		return self.locations | self.items | self.NPCs | set(self.players_list)

	def get_objects(self, types=['location', 'item', 'player', 'NPC'], and_key=lambda x: True, or_key=lambda x: False):
		return list(filter(lambda obj: obj.type in types and and_key(obj) or or_key(obj), self.get_all_objects()))

	def player_to_send(self, username):
		return self.to_send[username]

	def save(self, filename):
		# TODO: issue #30
		with open('tmp\\' + filename + '.save.json', 'w', encoding='utf-8') as f:
			json.dump(self.turns_log, f, indent = 4, ensure_ascii=False)

	def get_msgs(self, username):
		'''
		Возвращает все сообщения отосланные игроку username
		'''

		if username in self.msgs_log:
			return self.msgs_log[username]
		else:
			return [] 

	def get_turns(self, number = None, username = None):
		'''
		Возвращает все ходы сделанные игроками
		Возвращает ходы сделанные только указанным игроками, если указан параметр username
		Возвращает ход под номером number с конца, если указан параметр number
		Например get_turns(1, 'Вася') вернёт последний ход Васи
		'''

		if username is None:
			if number is None:
				return self.turns_log
			else:
				return self.turns_log[-number]
		else:
			if number is None:
				return list(filter(lambda turn: turn['player'] in username, self.turns))
			else:
				return list(filter(lambda turn: turn['player'] in username, self.turns))[-number]