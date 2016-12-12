from setting import Setting
from utils import Utils
from assets import Graphic, Sound
from controller import Controller
from sprite import Rotate_Image, Shell, Cannon_Explosion, Progess_Bar, Name_Bar, Flame
import copy, math, pygame, time

class Tank:
	def __init__(self, globe, player, color, init_pos, tank_model, tank_gameplay, tank_graphic, tank_sound):
		self.globe = globe
		self.player = player
		self.color = color
		self.speed = 0
		self.is_ready = False
		self.hp = tank_gameplay.HP
		self.tank_model = tank_model
		self.tank_gameplay = tank_gameplay
		self.tank_graphic = tank_graphic
		self.tank_sound = tank_sound
		self.last_fire = time.time()
		self.exposed_time = None

		if self.globe.is_same_team(player):
			name_color = Setting.Environment.ALLY_COLOR
		else:
			name_color = Setting.Environment.ENEMY_COLOR
			self.color = Setting.Environment.ENEMY_COLOR

		turret_size = self.tank_model.TURRET_FIXED_WIDTH, Utils.scale(self.tank_model.TURRET_FIXED_WIDTH, self.tank_model.TURRET_DIMENSION)
		turret_deviation = 0, Utils.scale(turret_size[1] / 2, self.tank_model.TURRET_VERTICAL_DEVIATION_RATIO) - turret_size[1] / 2
		self.turret = Rotate_Image(self.tank_graphic.TURRET, turret_size, init_pos, turret_deviation, self.color)
		self.globe.turret_tank_group.add(self.turret)
		body_size = self.tank_model.BODY_FIXED_WIDTH, Utils.scale(self.tank_model.BODY_FIXED_WIDTH, self.tank_model.BODY_DIMENSION)
		body_deviation = 0, Utils.scale(body_size[1] / 2, self.tank_model.BODY_VERTICAL_DEVIATION_RATIO) - body_size[1] / 2
		self.body = Rotate_Image(self.tank_graphic.BODY, body_size, init_pos, body_deviation, self.color, parent=self)
		self.globe.body_tank_group.add(self.body)

		self.hp_bar = Progess_Bar(Setting.Environment.HP_FULL_COLOR, Setting.Environment.HP_MISS_COLOR, (self.tank_model.BODY_FIXED_WIDTH, Setting.Environment.HP_BAR_HEIGHT))
		self.globe.hp_bar_group.add(self.hp_bar)
		self.name_bar = Name_Bar(player, Setting.Window.NAME_FONT_SIZE, name_color)
		self.globe.name_bar_group.add(self.name_bar)
	def is_alive(self):
		return self.hp > 0
	def damagify(self, damage, player):
		if self.hp < 0:
			return
		if self.hp < damage:
			link = None
			if self.globe.owner == self.player:
				link = Sound.Tank.Destroyed.SELF
			elif not self.globe.is_same_team(self.player):
				link = Sound.Tank.Destroyed.ENEMY
			if link != None and not self.globe.channels[Setting.Sound.DESTROYED].get_busy():
				si = Utils.sound_intensity_at_distance(0)
				sound = pygame.mixer.Sound(link)
				self.globe.channels[Setting.Sound.DESTROYED].play(sound)
				self.globe.channels[Setting.Sound.DESTROYED].set_volume(si)
		else:
			sound = Utils.damage_sound(damage, self.hp)
			owner_tank = self.globe.tanks[self.globe.owner]
			si = Utils.sound_intensity_at_distance(Utils.distance(self.body.pos, owner_tank.body.pos))
			if si:
				self.globe.channels[Setting.Sound.BEING_HIT].play(sound)
				self.globe.channels[Setting.Sound.BEING_HIT].set_volume(si)
			if not self.globe.is_same_team(self.player) and player == self.globe.owner:
				if Utils.proc_chance(Setting.Sound.HIT_CHANCE):
					si = Utils.sound_intensity_at_distance(0)
					link = Sound.Tank.Hit.get_hit()
					sound = pygame.mixer.Sound(link)
					self.globe.channels[Setting.Sound.HIT].play(sound)
					self.globe.channels[Setting.Sound.HIT].set_volume(si)
		self.hp -= damage
		if self.hp < 0:
			self.turret.change_color(Setting.Environment.BURNED_COLOR)
			self.body.change_color(Setting.Environment.BURNED_COLOR)
			flame = Flame(self.body.size, self.body.pos)
			self.globe.flame_group.add(flame)
	def move_body(self, is_forward=True):
		backward_friction = Setting.Environment.FRICTION_ACCELERATION
		forward_friction = 2 * Utils.scale(backward_friction, (self.tank_gameplay.TANK_BACKWARD_SPEED[1], self.tank_gameplay.TANK_FORWARD_SPEED[1]))
		if is_forward == True:
			total_angle = self.body.angle + Setting.Tank_Model.Tank.INIT_ANGLE
			if self.speed >= self.tank_gameplay.TANK_FORWARD_SPEED[1]:
				self.speed = self.tank_gameplay.TANK_FORWARD_SPEED[1]
			else:
				acceleration = Utils.acceleration(self.tank_gameplay.TANK_FORWARD_SPEED)
				if self.speed < 0:
					acceleration += backward_friction
				self.speed = Utils.next_speed(self.speed, acceleration)
			distance = Utils.scale(self.speed, (1000, Setting.Window.MSPF))
		elif is_forward == False:
			total_angle = self.body.angle - Setting.Tank_Model.Tank.INIT_ANGLE
			if self.speed <= -self.tank_gameplay.TANK_BACKWARD_SPEED[1]:
				self.speed = -self.tank_gameplay.TANK_BACKWARD_SPEED[1]
			else:
				acceleration = Utils.acceleration(self.tank_gameplay.TANK_BACKWARD_SPEED)
				if self.speed > 0:
					acceleration += forward_friction
				self.speed = Utils.next_speed(self.speed, -acceleration)
			distance = Utils.scale(-self.speed, (1000, Setting.Window.MSPF))
		else:
			if abs(self.speed) <= Setting.Environment.INF_VEL:
				total_angle = self.body.angle
				distance = 0
			elif self.speed > 0:
				total_angle = self.body.angle - Setting.Tank_Model.Tank.INIT_ANGLE
				self.speed = Utils.next_speed(self.speed, -forward_friction)
				distance = Utils.scale(-self.speed, (1000, Setting.Window.MSPF))
			elif self.speed < 0:
				total_angle = self.body.angle + Setting.Tank_Model.Tank.INIT_ANGLE
				self.speed = Utils.next_speed(self.speed, backward_friction)
				distance = Utils.scale(self.speed, (1000, Setting.Window.MSPF))
		next_body = copy.copy(self.body)
		next_body.pos = Utils.mirror(Utils.translate(Utils.mirror(self.body.pos), distance, total_angle))
		next_body.update()
		predicted_walls = pygame.sprite.spritecollide(next_body, self.globe.wall_group, False, False)
		predicted_boundary = pygame.sprite.spritecollide(next_body, self.globe.boundary_group, False, False)
		predicted_tanks = Utils.self_remove_tank(self.body, pygame.sprite.spritecollide(next_body, self.globe.body_tank_group, False, False))
		if predicted_walls or predicted_boundary or predicted_tanks:
			search_distance = 0
			while True:
				search_distance += (Setting.Environment.SEARCH_DISTANCE * 2)
				out_body = copy.copy(self.body)
				out_body.pos = Utils.mirror(Utils.translate(Utils.mirror(self.body.pos), Utils.same_sign(distance, search_distance), total_angle))
				out_body.update()
				predicted_walls = pygame.sprite.spritecollide(out_body, self.globe.wall_group, False, False)
				predicted_boundary = pygame.sprite.spritecollide(out_body, self.globe.boundary_group, False, False)
				predicted_tanks = Utils.self_remove_tank(self.body, pygame.sprite.spritecollide(out_body, self.globe.body_tank_group, False, False))
				if not predicted_walls and not predicted_boundary and not predicted_tanks:
					self.body.pos = next_body.pos
					self.turret.pos = next_body.pos
					break
				elif search_distance > Setting.Environment.THRESHOLD_DISTANCE:
					self.speed = 0
					break
		else:
			self.body.pos = next_body.pos
			self.turret.pos = next_body.pos
	def is_reloaded(self):
		return time.time() - self.last_fire >= self.tank_gameplay.RELOAD_TIME
	def fire(self, pressed):
		if pressed[Controller.FIRE] and self.is_reloaded():
			owner = self.globe.team_config.players[self.player]
			for player in self.globe.team_config.players.values():
				player_tank = self.globe.tanks[player['name']]
				if player['team'] != owner['team'] and player_tank.is_alive():
					distance = Utils.distance(self.body.pos, player_tank.body.pos)
					if distance <= Setting.Detection.SEE_SPEED:
						self.exposed_time = time.time() * 1000

			owner_tank = self.globe.tanks[self.globe.owner]
			si = Utils.sound_intensity_at_distance(Utils.distance(owner_tank.body.pos, self.body.pos))
			if si:
				sound = pygame.mixer.Sound(self.tank_sound.CANNON_EXPLOSION)
				sound.set_volume(si)
				self.globe.channels[Utils.channel_cannon(self.globe.get_index(self.player))].play(sound)

			self.last_fire = time.time()
			self.is_ready = False
			shell_size = self.tank_model.SHELL_FIXED_WIDTH, Utils.scale(self.tank_model.SHELL_FIXED_WIDTH, (Setting.Tank_Model.Tank.SHELL_RATIO))
			shell_center = 0, -(self.turret.size[1] + shell_size[1]) / 2
			shell_center = Utils.rotate(Utils.sum_tuple(shell_center, Utils.mul_tuple(self.turret.deviation, -1)), self.turret.angle)
			shell_center = Utils.int_tuple(Utils.sum_tuple(shell_center, self.turret.pos))
			shell = Shell(shell_size, shell_center, self.turret.angle, self)
			self.globe.shell_group.add(shell)
			explosion_size = self.tank_model.SHELL_FIXED_WIDTH, Utils.scale(self.tank_model.SHELL_FIXED_WIDTH, (Setting.Environment.CANNON_EXPLOSION_RATIO))
			explosion_center = 0, -(self.turret.size[1] + explosion_size[1]) / 2
			explosion_center = Utils.rotate(Utils.sum_tuple(explosion_center, Utils.mul_tuple(self.turret.deviation, -1)), self.turret.angle)
			explosion_center = Utils.int_tuple(Utils.sum_tuple(explosion_center, self.turret.pos))
			cannon_explosion = Cannon_Explosion(explosion_size, explosion_center, self.turret.angle, self.player)
			self.globe.cannon_explosion_group.add(cannon_explosion)
	def ready(self):
		if self.player == self.globe.owner and self.is_reloaded() and not self.is_ready:
			self.is_ready = True
			chance = self.tank_gameplay.RELOAD_TIME / Setting.Gameplay.SPG.RELOAD_TIME
			if Utils.proc_chance(chance):
				si = Utils.sound_intensity_at_distance(0)
				link = Sound.Tank.Misc.READY_FIRE
				sound = pygame.mixer.Sound(link)
				sound.set_volume(si)
				self.globe.channels[Setting.Sound.READY].play(sound)
	def update_hp(self):
		self.hp_bar.percent = max(self.hp / self.tank_gameplay.HP, 0)
		distance = Utils.center_boundary_distance(self.body.size, self.body.angle)
		x, y = self.body.pos
		self.hp_bar.pos = Utils.int_tuple((x, y + distance + Setting.Environment.HP_BAR_HEIGHT))
	def update_name(self):
		distance = Utils.center_boundary_distance(self.body.size, self.body.angle)
		x, y = self.body.pos
		self.name_bar.pos = Utils.int_tuple((x, y - distance - 2 * Setting.Environment.HP_BAR_HEIGHT))
	def check_actions(self, pressed):
		if self.exposed_time != None:
			now = time.time() * 1000
			if now - self.exposed_time > Setting.Detection.SHELL_EXPOSED_TIME:
				self.exposed_time = None
		if pressed[Controller.BODY_TURN_LEFT]:
			if pressed[Controller.BODY_BACKWARD]:
				self.turn_body(False)
			else:
				self.turn_body()
		if pressed[Controller.BODY_TURN_RIGHT]:
			if pressed[Controller.BODY_BACKWARD]:
				self.turn_body()
			else:
				self.turn_body(False)
		if pressed[Controller.BODY_FORWARD]:
			self.move_body()
		if pressed[Controller.BODY_BACKWARD]:
			self.move_body(False)
		if not pressed[Controller.BODY_FORWARD] and not pressed[Controller.BODY_FORWARD]:
			self.move_body(None)
		self.fire(pressed)
		self.ready()
		self.update_hp()
		self.update_name()
		if pressed[pygame.K_y]:
			self.globe.game_quit = True

class Tank_Turret_Turnable(Tank):
	def __init__(self, globe, player, color, init_pos, tank_model, tank_gameplay, tank_graphic, tank_sound):
		super().__init__(globe, player, color, init_pos, tank_model, tank_gameplay, tank_graphic, tank_sound)
	def turn_body(self, is_anti=True):
		angle = Utils.scale(self.tank_gameplay.BODY_TURN_DEG, (1000, Setting.Window.MSPF))
		if is_anti:
			self.body.turn(angle)
		else:
			self.body.turn(-angle)
	def turn_turret(self, is_anti=True):
		angle = Utils.scale(self.tank_gameplay.TURRET_TURN_DEG, (1000, Setting.Window.MSPF))
		if is_anti:
			self.turret.turn(angle)
		else:
			self.turret.turn(-angle)
	def check_actions(self, pressed):
		if pressed[Controller.TURRET_TURN_LEFT]:
			self.turn_turret()
		if pressed[Controller.TURRET_TURN_RIGHT]:
			self.turn_turret(False)
		super().check_actions(pressed)

class Heavy_Tank(Tank_Turret_Turnable):
	def __init__(self, globe, player, color, init_pos):
		super().__init__(globe, player, color, init_pos, Setting.Tank_Model.Heavy_Tank, Setting.Gameplay.Heavy_Tank, Graphic.Heavy_Tank, Sound.Heavy_Tank)

class Light_Tank(Tank_Turret_Turnable):
	def __init__(self, globe, player, color, init_pos):
		super().__init__(globe, player, color, init_pos, Setting.Tank_Model.Light_Tank, Setting.Gameplay.Light_Tank, Graphic.Light_Tank, Sound.Light_Tank)

class Tank_Turret_Nonturnable(Tank):
	def __init__(self, globe, player, color, init_pos, tank_model, tank_gameplay, tank_graphic, tank_sound):
		super().__init__(globe, player, color, init_pos, tank_model, tank_gameplay, tank_graphic, tank_sound)
	def turn_body(self, is_anti=True):
		angle = Utils.scale(self.tank_gameplay.BODY_TURN_DEG, (1000, Setting.Window.MSPF))
		if is_anti:
			self.body.turn(angle)
			self.turret.turn(angle)
		else:
			self.body.turn(-angle)
			self.turret.turn(-angle)

class SPG(Tank_Turret_Nonturnable):
	def __init__(self, globe, player, color, init_pos):
		super().__init__(globe, player, color, init_pos, Setting.Tank_Model.SPG, Setting.Gameplay.SPG, Graphic.SPG, Sound.SPG)
		self.alpha_angle = 0
		self.protractor = pygame.image.load(self.tank_graphic.PROTRACTOR)
		self.protractor_size = Utils.int_tuple((self.tank_model.PROTRACTOR_FIXED_WIDTH, 
			Utils.scale(self.tank_model.PROTRACTOR_FIXED_WIDTH, self.tank_model.PROTRACTOR_DIMENSION)))
		self.protractor = pygame.transform.scale(self.protractor, self.protractor_size)
		self.protractor_rect = self.protractor.get_rect(center=self.tank_model.PROTRACTOR_POS)
		self.last_stop = None
		self.last_rotate = None
		self.fire_param = None
		self.land_origin = None
		self.land_radius = None
	def elevate_turret(self, is_up=True):
		angle = Utils.scale(self.tank_gameplay.TURRET_ELEVATION_DEG, (1000, Setting.Window.MSPF))
		if is_up:
			self.alpha_angle += angle
		else:
			self.alpha_angle -= angle
		self.alpha_angle = min(self.tank_gameplay.MAX_ANGLE_ELEVATION, self.alpha_angle)
		self.alpha_angle = max(self.tank_gameplay.MIN_ANGLE_ELEVATION, self.alpha_angle)
	def check_actions(self, pressed):
		if pressed[Controller.TURRET_ELEVATE]:
			self.last_rotate = time.time() * 1000
			self.elevate_turret()
		if pressed[Controller.TURRET_DEELEVATE]:
			self.last_rotate = time.time() * 1000
			self.elevate_turret(False)
		if pressed[Controller.BODY_TURN_LEFT] or pressed[Controller.BODY_TURN_RIGHT]:
			self.last_rotate = time.time() * 1000
		if pressed[Controller.BODY_FORWARD] or pressed[Controller.BODY_BACKWARD]:
			self.last_stop = None
		super().check_actions(pressed)
		if abs(self.speed) <= Setting.Environment.INF_VEL and self.last_stop == None:
			self.last_stop = time.time() * 1000
	def fire(self, pressed):
		if self.player == self.globe.owner and pressed[Controller.FIRE] and self.is_reloaded():
			owner = self.globe.team_config.players[self.player]
			for player in self.globe.team_config.players.values():
				player_tank = self.globe.tanks[player['name']]
				if player['team'] != owner['team'] and player_tank.is_alive():
					distance = Utils.distance(self.body.pos, player_tank.body.pos)
					if distance <= Setting.Detection.SEE_SPEED:
						self.exposed_time = time.time() * 1000
			self.last_fire = time.time()
			end_point = Utils.random_circle_point(self.land_origin, self.land_radius)
			land_point = Utils.dotted_point(end_point, *self.fire_param)
			self.globe.arty = self.player, self.fire_param[0][:2], land_point
class Tank_Destroyer(Tank_Turret_Nonturnable):
	def __init__(self, globe, player, color, init_pos):
		super().__init__(globe, player, color, init_pos, Setting.Tank_Model.Tank_Destroyer, Setting.Gameplay.Tank_Destroyer, Graphic.Tank_Destroyer, Sound.Tank_Destroyer)
		