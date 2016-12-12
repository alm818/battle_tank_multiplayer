from misc import Map
from random import randint

def normalize(tup):
	x, y = tup
	if tup[0] < 0:
		x += Team_Config.SCREEN_SIZE[0]
	if tup[1] < 0:
		y += Team_Config.SCREEN_SIZE[1]
	return x, y
class Team_Config:
	SCREEN_SIZE = (1366, 768)
	FIXED_SIZE = (25, 40)
	MAX_PLAYER_PER_TEAM = 5
	COLOR_LIST = {
		'Blue' : (3, 74, 254),
		'Teal' : (30, 235, 192),
		'Purple' : (94, 0, 141),
		'Yellow' : (255, 253, 2),
		'Orange' : (252, 149, 20),
		'Pink' : (231, 102, 182),
		'Green' : (0, 150, 0),
		'Light Grey' : (137, 195, 241),
		'Dark Green' : (23, 108, 79),
		'Brown' : (85, 51, 5)
	}
	LIGHT_TANK = 'Light Tank'
	HEAVY_TANK = 'Heavy Tank'
	SPG = 'SPG'
	TANK_DESTROYER = 'Tank Destroyer'
	TEAM1 = 10
	TEAM2 = 11
	READY = 20
	NOT_READY = 21
	HOST = 22
	def __init__(self, host_name):
		self.host_name = host_name
		self.TANK_OPTION = [Team_Config.LIGHT_TANK, Team_Config.HEAVY_TANK, Team_Config.SPG, Team_Config.TANK_DESTROYER]
		self.players = {}
		self.is_start = False
		self.add_player(host_name, Team_Config.HOST)
	def place_players(self, map_):
		team1 = []
		team2 = []
		for player in self.players.values():
			if player['team'] == Team_Config.TEAM1:
				team1.append(player)
			else:
				team2.append(player)
		self.place_team(team1, map_.spawns[0])
		self.place_team(team2, map_.spawns[1])
	def place_team(self, team, spawn):
		param = (normalize(spawn[Map.from_]), normalize(spawn[Map.to_]))
		top_left = tuple(min(tuple(x)) for x in zip(*param))
		down_right = tuple(max(tuple(x)) for x in zip(*param))
		for i, player in enumerate(team):
			while True:
				x = randint(top_left[0], down_right[0] - Team_Config.FIXED_SIZE[0])
				y = randint(top_left[1], down_right[1] - Team_Config.FIXED_SIZE[1])
				isPossible = True
				for j in range(0, i):
					other = team[j]
					if abs(x - other['x']) <= Team_Config.FIXED_SIZE[0] and abs(y - other['y']) <= Team_Config.FIXED_SIZE[1]:
						isPossible = False
						break
				if isPossible:
					player['x'] = x
					player['y'] = y
					break
	def is_start_possible(self):
		if self.count_player(Team_Config.TEAM1) == 0 or self.count_player(Team_Config.TEAM2) == 0:
			return False
		for player in self.players.values():
			if player['status'] == Team_Config.NOT_READY:
				return False
		return True
	def is_player_in(self, name):
		return name in self.players
	def remove_player(self, name):
		self.players.pop(name)
	def is_change_team_possible(self, name):
		player = self.players[name]
		if player['team'] == Team_Config.TEAM1:
			if self.is_full_team2():
				return False
			return True
		else:
			if self.is_full_team1():
				return False
			return True
	def is_change_color_possible(self, name, new_color):
		for player in self.players.values():
			if player['name'] != name and player['color'] == new_color:
				return False
		return True
	def change_team(self, name):
		player = self.players[name]
		if player['team'] == Team_Config.TEAM1:
			player['team'] = Team_Config.TEAM2
			player['index'] = self.find_first_slot(Team_Config.TEAM2)
		else:
			player['team'] = Team_Config.TEAM1
			player['index'] = self.find_first_slot(Team_Config.TEAM1)
	def count_player(self, team):
		cnt = 0
		for player in self.players.values():
			if player['team'] == team:
				cnt += 1
		return cnt
	def is_full(self):
		return self.is_full_team1() and self.is_full_team2()
	def is_full_team1(self):
		return self.count_player(Team_Config.TEAM1) == Team_Config.MAX_PLAYER_PER_TEAM
	def is_full_team2(self):
		return self.count_player(Team_Config.TEAM2) == Team_Config.MAX_PLAYER_PER_TEAM
	def find_first_slot(self, team):
		if team == Team_Config.TEAM1:
			marked = [x for x in range(Team_Config.MAX_PLAYER_PER_TEAM)]
		else:
			marked = [Team_Config.MAX_PLAYER_PER_TEAM + x for x in range(Team_Config.MAX_PLAYER_PER_TEAM)]
		for player in self.players.values():
			if player['index'] in marked:
				marked.remove(player['index'])
		return marked[0]
	def add_player(self, name, status):
		count1 = self.count_player(Team_Config.TEAM1)
		count2 = self.count_player(Team_Config.TEAM2)
		if count2 < count1:
			index = self.find_first_slot(Team_Config.TEAM2)
		else:
			index = self.find_first_slot(Team_Config.TEAM1)
		self.players[name] = self.make_player(name, index, status)
	def get_unused_color(self):
		marked = list(Team_Config.COLOR_LIST.keys())[:]
		for player in self.players.values():
			marked.remove(player['color'])
		return marked[0]
	def make_player(self, name, index, status):
		player = {}
		player['name'] = name
		player['tank'] = Team_Config.LIGHT_TANK
		player['color'] = self.get_unused_color()
		player['index'] = index
		if 0 <= index < Team_Config.MAX_PLAYER_PER_TEAM:
			player['team'] = Team_Config.TEAM1
		else:
			player['team'] = Team_Config.TEAM2
		player['status'] = status
		return player
