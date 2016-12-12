import pygame, time, math
from utils import Utils
from setting import Setting
from assets import Sound
from sprite import Wall, Boundary, Cannon_Explosion, Shell_Explosion, Arty_Shell
from tank import Heavy_Tank, Light_Tank, SPG, Tank_Destroyer
from scripts.outgame import misc, network
from threading import Timer
from random import randint

class Global:
	def __init__(self, team_config, owner, server_map):
		self.game_quit = False
		self.boundary_group = pygame.sprite.Group()
		self.wall_group = pygame.sprite.Group()
		self.body_tank_group = pygame.sprite.Group()
		self.turret_tank_group = pygame.sprite.Group()
		self.shell_group = pygame.sprite.Group()
		self.arty_shell_group = pygame.sprite.Group()
		self.cannon_explosion_group = pygame.sprite.Group()
		self.shell_explosion_group = pygame.sprite.Group()
		self.hp_bar_group = pygame.sprite.Group()
		self.name_bar_group = pygame.sprite.Group()
		self.flame_group = pygame.sprite.Group()
		self.team_config = team_config
		self.owner = owner
		self.server_map = server_map
		self.all_groups = [
			self.wall_group, 
			self.body_tank_group, 
			self.turret_tank_group, 
			self.shell_group,
			self.arty_shell_group,
			self.cannon_explosion_group,
			self.shell_explosion_group,
			self.hp_bar_group,
			self.name_bar_group,
			self.flame_group
		]
		self.tanks = {}
		self.last_detect = {}
		for name in self.team_config.players:
			self.last_detect[name] = None
			player = self.team_config.players[name]
			center = player['x'] + self.team_config.FIXED_SIZE[0] // 2, player['y'] + self.team_config.FIXED_SIZE[1] // 2
			param = (self, name, pygame.Color(*self.team_config.COLOR_LIST[player['color']]), center)
			if player['tank'] == self.team_config.LIGHT_TANK:
				tank = Light_Tank(*param)
			elif player['tank'] == self.team_config.HEAVY_TANK:
				tank = Heavy_Tank(*param)
			elif player['tank'] == self.team_config.SPG:
				tank = SPG(*param)
			elif player['tank'] == self.team_config.TANK_DESTROYER:
				tank = Tank_Destroyer(*param)
			self.tanks[name] = tank
		self.add_wall() 
		self.add_boundary()
	def is_victory(self):
		ally_defeat = True
		enemy_defeat = True
		for name in self.team_config.players:
			tank = self.tanks[name]
			if tank.is_alive():
				if self.is_same_team(name):
					ally_defeat = False
				else:
					enemy_defeat = False
		if not ally_defeat and enemy_defeat:
			return True
		elif ally_defeat and not enemy_defeat:
			return False
		else:
			return None
	def display_end(self, screen, end):
		if end:
			value = 'VICTORY'
			color = Setting.Environment.VICTORY_COLOR
			link = Sound.Tank.Misc.VICTORY
		else:
			value = 'DEFEAT'
			color = Setting.Environment.DEFEAT_COLOR
			link = Sound.Tank.Misc.DEFEAT
		font = pygame.font.SysFont(Setting.Window.FONT, Setting.Window.END_FONT_SIZE)
		text = font.render(value, True, color)
		textpos = text.get_rect(center=(Setting.Window.WIDTH // 2, Setting.Window.HEIGHT // 2))
		screen.blit(text, textpos)
		music = pygame.mixer.music
		if not music.get_busy():
			music.load(link)
			music.set_volume(Setting.Sound.DEFAULT_MULTIPLIER)
			music.play()
	def get_index(self, name):
		return self.team_config.players[name]['index']
	def get_player_detection(self, name):
		detect = {}
		owner = self.team_config.players[name]
		for player in self.team_config.players.values():
			if player['team'] == owner['team']:
				detect[player['name']] = True
			else:
				player_tank = self.tanks[player['name']]
				if not player_tank.is_alive():
					detect[player['name']] = True
					continue
				owner_tank = self.tanks[name]
				if not owner_tank.is_alive():
					detect[player['name']] = False
					continue
				if player_tank.exposed_time != None:
					detect[player['name']] = True
					continue
				distance = Utils.distance(owner_tank.body.pos, player_tank.body.pos)
				see_range = Utils.find_mid(abs(player_tank.speed), Setting.Detection.SEE_IDLE, Setting.Detection.SEE_SPEED, Setting.Detection.MAX_SPEED)
				if distance <= see_range and not Utils.have_obstacle(self.server_map, owner_tank.body.pos, player_tank.body.pos):
					detect[player['name']] = True
					continue
				listen_range = Utils.find_mid(abs(player_tank.speed), Setting.Detection.LISTEN_IDLE, Setting.Detection.LISTEN_SPEED, Setting.Detection.MAX_SPEED)
				if distance <= listen_range:
					detect[player['name']] = True
					continue
				detect[player['name']] = False
		return detect
	def get_team_detection(self, name):
		owner = self.team_config.players[name]
		res = {}
		for name in self.tanks:
			res[name] = False
		for player in self.team_config.players.values():
			if player['team'] == owner['team']:
				detect = self.get_player_detection(player['name'])
				for name in res:
					res[name] = (res[name] or detect[name])
		now = time.time() * 1000
		for name in res:
			if res[name]:
				self.last_detect[name] = now
			elif self.last_detect[name] != None and now - self.last_detect[name] <= Setting.Detection.DETECT_TIME:
				res[name] = True
		return res
	def is_same_team(self, name):
		player = self.team_config.players[name]
		owner = self.team_config.players[self.owner]
		return player['team'] == owner['team']
	def optional_drawing(self, screen, detection):
		owner_tank = self.tanks[self.owner]
		reload_time = round(max(owner_tank.tank_gameplay.RELOAD_TIME - (time.time() - owner_tank.last_fire), 0), 1)
		if reload_time == 0:
			color = Setting.Environment.FINISH_COLOR
		else:
			color = Setting.Environment.RELOAD_COLOR
		font = pygame.font.SysFont(Setting.Window.FONT, Setting.Window.RELOAD_FONT_SIZE)
		text = font.render(str(reload_time), True, color)
		textpos = text.get_rect(center=Setting.Tank_Model.Tank.RELOAD_POS)
		screen.blit(text, textpos)
		angle = Setting.Tank_Model.Tank.INIT_ANGLE + owner_tank.turret.angle
		pos = owner_tank.turret.pos
		distance = owner_tank.turret.size[1] // 2
		origin = Utils.mirror(Utils.translate(Utils.mirror(pos), distance, angle))
		self.param = None
		if self.team_config.players[self.owner]['tank'] == self.team_config.TANK_DESTROYER:
			out_vector = Utils.sum_tuple(pos, Utils.mul_tuple(origin, -1))
			devi_dist = Setting.Tank_Model.Tank_Destroyer.SHELL_FIXED_WIDTH // 2
			left_origin = Utils.mirror(Utils.translate(Utils.mirror(origin), devi_dist, angle + 90))
			right_origin = Utils.mirror(Utils.translate(Utils.mirror(origin), devi_dist, angle - 90))
			body_group = pygame.sprite.Group(self.wall_group, self.boundary_group)
			for name in detection:
				if detection[name] and name != self.owner:
					body_group.add(self.tanks[name].body)
			dist = Utils.find_shortest_distance(origin, angle, body_group)
			dist_left = Utils.find_shortest_distance(left_origin, angle, body_group)
			dist_right = Utils.find_shortest_distance(right_origin, angle, body_group)
			final_dist = min(dist, dist_left, dist_right)
			left_end = Utils.mirror(Utils.translate(Utils.mirror(left_origin), final_dist, angle))
			right_end = Utils.mirror(Utils.translate(Utils.mirror(right_origin), final_dist, angle))
			param = (Setting.Gameplay.Tank_Destroyer.AIM_COLOR, Setting.Gameplay.Tank_Destroyer.FULL_SEG, Setting.Gameplay.Tank_Destroyer.MISS_SEG)
			Utils.dotted_line(screen, left_origin, left_end, *param)
			Utils.dotted_line(screen, right_origin, right_end, *param)
		elif self.team_config.players[self.owner]['tank'] == self.team_config.SPG:
			Utils.SPG_blit(screen, owner_tank)
			alpha = math.radians(owner_tank.alpha_angle)
			init_pos = (*origin, owner_tank.tank_model.BASE_HEIGHT + math.sin(alpha) * owner_tank.tank_model.TURRET_LENGTH)
			theta = math.radians(angle)
			v = owner_tank.tank_gameplay.SHELL_SPEED[1]
			g = Setting.Environment.G
			owner_tank.land_origin = Utils.find_land_origin(init_pos, alpha, theta, v, g)
			max_origin = Utils.find_land_origin(init_pos, math.pi / 4, theta, v, g)
			land_range = Utils.distance(owner_tank.land_origin, origin)
			max_range = Utils.distance(max_origin, origin)
			owner_tank.land_radius = Utils.scale(owner_tank.tank_gameplay.MAX_DIPERSION, (max_range, land_range))
			if owner_tank.last_stop == None:
				amplify = owner_tank.tank_gameplay.MAX_MOVE_AMPLI
			else:
				now = time.time() * 1000
				need = max(owner_tank.tank_gameplay.AIM_TIME_MOVE - (now - owner_tank.last_stop), 0)
				amplify = Utils.find_mid(need, 1, owner_tank.tank_gameplay.MAX_MOVE_AMPLI, owner_tank.tank_gameplay.AIM_TIME_MOVE)
				if owner_tank.last_rotate != None:
					need = max(owner_tank.tank_gameplay.AIM_TIME_ROTATE - (now - owner_tank.last_rotate), 0)
					rotate_amplify = Utils.find_mid(need, 1, owner_tank.tank_gameplay.MAX_ROTATE_AMPLI, owner_tank.tank_gameplay.AIM_TIME_ROTATE)
					amplify = max(amplify, rotate_amplify)
			owner_tank.land_radius *= amplify 
			list_height = []
			list_Ps = []
			for wall in self.wall_group.sprites():
				tl = wall.top_left
				dr = wall.down_right
				tr = dr[0], tl[1]
				dl = tl[0], dr[1]
				P = [tl, tr, dr, dl]
				height = wall.height
				list_height.append(height)
				list_Ps.append(P)
			for name in detection:
				if detection[name]:
					tank = self.tanks[name]
					height = owner_tank.tank_model.BASE_HEIGHT
					P = Utils.find_P_of_tank(tank)
					list_height.append(height)
					list_Ps.append(P)
			owner_tank.fire_param = (init_pos, alpha, g, list_height, list_Ps)
			self.param = (screen, owner_tank.tank_gameplay.AIM_COLOR, init_pos, owner_tank.land_origin, owner_tank.land_radius,
				owner_tank.tank_gameplay.CIRCLE_DOTS, alpha, g, list_height, list_Ps)
	def reveal_detection(self, screen):
		self.draw_group = pygame.sprite.LayeredUpdates(self.wall_group)
		detection = self.get_team_detection(self.owner)
		self.optional_drawing(screen, detection)
		pos = self.tanks[self.owner].body.pos
		for name in detection:
			tank = self.tanks[name]
			if detection[name] and tank.is_alive():
				self.draw_group.add(tank.hp_bar, tank.name_bar)
		for name in detection:
			tank = self.tanks[name]
			if detection[name]:
				self.draw_group.add(tank.body, tank.turret)
		self.draw_group.add(self.flame_group)
		for shell in self.shell_group.sprites():
			distance = Utils.distance(pos, shell.pos)
			if distance <= Setting.Detection.SEE_SPEED or self.is_same_team(shell.parent.player):
				self.draw_group.add(shell)
		for arty_shell in self.arty_shell_group.sprites():
			distance = Utils.distance(pos, arty_shell.pos)
			if distance <= Setting.Detection.SEE_SPEED or self.is_same_team(arty_shell.player):
				self.draw_group.add(arty_shell)
		for cannon_explosion in self.cannon_explosion_group.sprites():
			distance = Utils.distance(pos, cannon_explosion.pos)
			if distance <= Setting.Detection.SEE_SPEED or self.is_same_team(cannon_explosion.player):
				self.draw_group.add(cannon_explosion)
		for shell_explosion in self.shell_explosion_group.sprites():
			distance = Utils.distance(pos, shell_explosion.pos)
			if distance <= Setting.Detection.SEE_SPEED or self.is_same_team(shell_explosion.player):
				self.draw_group.add(shell_explosion)
	def check_actions(self, dic_pressed):
		if dic_pressed == None:
			return
		owner_tank = self.tanks[self.owner]
		if network.Server.ARTY in dic_pressed:
			arty_info = dic_pressed[network.Server.ARTY]
			tank_model = Setting.Tank_Model.SPG
			for info in arty_info:

				tank = self.tanks[info[0]]
				si = Utils.sound_intensity_at_distance(Utils.distance(tank.body.pos, owner_tank.body.pos))
				if si:
					sound = pygame.mixer.Sound(tank.tank_sound.CANNON_EXPLOSION)
					sound.set_volume(si)
					self.channels[Utils.channel_cannon(self.get_index(info[0]))].play(sound)

				arty = info[1:]
				shell_size = tank_model.SHELL_FIXED_WIDTH, Utils.scale(tank_model.SHELL_FIXED_WIDTH, (Setting.Tank_Model.Tank.SHELL_RATIO))
				shell = Arty_Shell(shell_size, *info)
				self.arty_shell_group.add(shell)
				explosion_size = tank_model.SHELL_FIXED_WIDTH, Utils.scale(tank_model.SHELL_FIXED_WIDTH, (Setting.Environment.CANNON_EXPLOSION_RATIO))
				explosion_center = arty[0]
				cannon_explosion = Cannon_Explosion(explosion_size, explosion_center, Utils.angle_onscreen_seg(*arty), info[0])
				self.cannon_explosion_group.add(cannon_explosion)
		for tank in self.tanks.values():
			if tank.player in dic_pressed and tank.is_alive():
				tank.check_actions(dic_pressed[tank.player])
	def add_wall(self):
		for server_wall in self.server_map.walls:
			wall = Wall(server_wall[misc.Map.from_], server_wall[misc.Map.to_], server_wall[misc.Map.height_])
			self.wall_group.add(wall)
	def add_boundary(self):
		for boundary in Setting.Environment.BOUNDARY:
			bound = Boundary(*boundary)
			self.boundary_group.add(bound)
	def remove_cannon_explosion(self):
		remove = []
		for cannon_explosion in self.cannon_explosion_group:
			if cannon_explosion.last <= 0:
				remove.append(cannon_explosion)
		for cannon_explosion in remove:
			self.cannon_explosion_group.remove(cannon_explosion)
	def remove_shell_explosion(self):
		remove = []
		for shell_explosion in self.shell_explosion_group:
			if shell_explosion.last <= 0:
				remove.append(shell_explosion)
		for shell_explosion in remove:
			self.shell_explosion_group.remove(shell_explosion)
	def remove_shell(self):
		remove = set()
		remove_arty = set()
		for arty_shell in self.arty_shell_group:
			if arty_shell.pos == arty_shell.land_point:
				remove_arty.add(arty_shell)
				shell_explosion_size = arty_shell.explo_width, Utils.scale(arty_shell.explo_width, Setting.Environment.SHELL_EXPLOSION_RATIO)
				Utils.damagify(arty_shell, arty_shell.pos, self.body_tank_group)
				shell_explosion = Shell_Explosion(shell_explosion_size, arty_shell.pos, arty_shell.player)
				self.shell_explosion_group.add(shell_explosion)

				si = Utils.sound_intensity_at_distance(Utils.distance(self.tanks[self.owner].body.pos, arty_shell.pos))
				link = Sound.Tank.Misc.ARTY_HIT
				sound = pygame.mixer.Sound(link)
				sound.set_volume(si)
				self.channels[Utils.channel_misc(self.channels)].play(sound)
		for shell in self.shell_group:
			shell_tank_collision = Utils.self_remove_tank(shell.body, pygame.sprite.spritecollide(shell, self.body_tank_group, False, False))
			if shell_tank_collision:
				remove.add(shell)
				shell_explosion_size = shell.explo_width, Utils.scale(shell.explo_width, Setting.Environment.SHELL_EXPLOSION_RATIO)
				pos = Utils.find_intersection(shell, shell.pos, shell_tank_collision)
				Utils.damagify(shell, pos, self.body_tank_group)
				shell_explosion = Shell_Explosion(shell_explosion_size, pos, shell.parent.player)
				self.shell_explosion_group.add(shell_explosion)
		shell_wall_collision = pygame.sprite.groupcollide(self.shell_group, self.wall_group, True, False)
		for shell in shell_wall_collision:
			shell_explosion_size = shell.explo_width, Utils.scale(shell.explo_width, Setting.Environment.SHELL_EXPLOSION_RATIO)
			pos = Utils.find_intersection(shell, shell.pos, shell_wall_collision[shell])
			Utils.damagify(shell, pos, self.body_tank_group)
			shell_explosion = Shell_Explosion(shell_explosion_size, pos, shell.parent.player)
			self.shell_explosion_group.add(shell_explosion)

			si = Utils.sound_intensity_at_distance(Utils.distance(self.tanks[self.owner].body.pos, pos))
			link = Sound.Tank.Misc.WALL_HIT
			sound = pygame.mixer.Sound(link)
			sound.set_volume(si)
			self.channels[Utils.channel_misc(self.channels)].play(sound)
		for shell in self.shell_group:
			if shell.is_out_boundary():
				remove.add(shell)
		for shell in remove:
			self.shell_group.remove(shell)
		for shell in remove_arty:
			self.arty_shell_group.remove(shell)
	def update(self):
		self.remove_cannon_explosion()
		self.remove_shell_explosion()
		self.remove_shell()
		for group in self.all_groups:
			group.update()
	def draw(self, screen):
		self.reveal_detection(screen)
		self.draw_group.draw(screen)
		if self.param != None:
			Utils.dotted_circle_blit(*self.param)
	def sound(self):
		owner_tank = self.tanks[self.owner]
		for tank in self.tanks.values():
			index = self.get_index(tank.player)
			si = Utils.sound_intensity_at_distance(Utils.distance(owner_tank.body.pos, tank.body.pos))
			idle_sound = pygame.mixer.Sound(tank.tank_sound.IDLE)
			move_sound = pygame.mixer.Sound(tank.tank_sound.MOVE)
			idle_channel = self.channels[Utils.channel_idle(index)]
			move_channel = self.channels[Utils.channel_move(index)]
			if si:
				if abs(tank.speed) <= 1:
					move_channel.stop()
					if not idle_channel.get_busy():
						idle_channel.play(idle_sound, loops=-1)
					idle_channel.set_volume(si)
				else:
					idle_channel.stop()
					if not move_channel.get_busy():
						move_channel.play(move_sound, loops=-1)
					move_channel.set_volume(si)
			else:
				idle_channel.stop()
				move_channel.stop()