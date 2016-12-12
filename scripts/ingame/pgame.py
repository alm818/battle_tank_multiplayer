import pygame, time
from scripts.ingame import global_, setting
from global_ import Global
from setting import Setting

class Pgame:
	def __init__(self, client, team_config, owner, server_map):
		pygame.init()
		Setting.init()
		self.screen = pygame.display.set_mode((Setting.Window.WIDTH, Setting.Window.HEIGHT))
		self.client = client
		self.team_config = team_config
		self.owner = owner
		self.globe = Global(team_config, owner, server_map)
		pygame.mixer.set_num_channels(Setting.Sound.CHANNEL)
		self.globe.channels = []
		self.globe.arty = None
		self.pressed = None
		for i in range(Setting.Sound.CHANNEL):
			self.globe.channels.append(pygame.mixer.Channel(i))
	def frameize(self, list_dic_pressed):
		if list_dic_pressed == None:
			list_dic_pressed = [{}]
		end = self.globe.is_victory()
		if end != None:
			list_dic_pressed = [{}]
		self.globe.arty = None
		# previous = time.time()
		# now = time.time()
		# print('EVENT', (now - previous) * 1000, 'ms')
		# previous = now
		self.screen.fill(Setting.Environment.BACKGROUND_COLOR)
		# now = time.time()
		# print('FILL', (now - previous) * 1000, 'ms')
		# previous = now
		for dic_pressed in list_dic_pressed:
			self.globe.check_actions(dic_pressed)
			self.globe.update()
		# now = time.time()
		# print('CHECK_ACTION+UPDATE', (now - previous) * 1000, 'ms')
		# previous = now
		self.globe.draw(self.screen)
		# now = time.time()
		# print('DRAW', (now - previous) * 1000, 'ms')
		# previous = now
		if end == None:
			self.globe.sound()
			self.pressed = pygame.key.get_pressed()
		else:
			for channel in self.globe.channels:
				channel.stop()
			self.globe.display_end(self.screen, end)
			self.pressed = None
		# now = time.time()
		# print('SOUND', (now - previous) * 1000, 'ms')
		pygame.display.flip()
		pygame.event.pump()
	def quit(self):
		pygame.display.quit()
