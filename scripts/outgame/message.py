class Message:
	QUIT = 0
	JOIN = 1
	ACCEPT = 2
	REFUSE = 3
	START = 4
	UPDATE = 5
	CHAT = 6
	UPDATE_TEAM_CONFIG = 10
	UPDATE_GAME_INPUT = 11
	UPDATE_MAP = 12
	UPDATE_ARTY = 13
	SAME_NAME = 20
	FULL = 21
	STARTED = 22
	def update(package):
		return (Message.UPDATE, package)
	def quit(name):
		return (Message.QUIT, name)
	def join(name):
		return (Message.JOIN, name)
	def chat(name, text):
		return (Message.CHAT, name, text)

	def accept(*data):
		return (Message.ACCEPT, *data)
	def refuse(reason=None):
		return (Message.REFUSE, reason)
	def start(data=None):
		return (Message.START, data)

	def update_team_config(player):
		return (Message.UPDATE_TEAM_CONFIG, player)
	def update_game_input(name, pressed):
		return (Message.UPDATE_GAME_INPUT, name, pressed)
	def update_map(map_):
		return (Message.UPDATE_MAP, map_)
	def update_arty(arty):
		return (Message.UPDATE_ARTY, arty)