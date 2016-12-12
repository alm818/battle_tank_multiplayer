import pygame, time
from utils import Utils
from setting import Setting
from assets import Graphic

class Sprite_Pixel(pygame.sprite.Sprite):
	def __init__(self, pos, size=(1, 1)):
		super().__init__()
		self.size = size
		self.image = pygame.Surface(size)
		self.rect = self.image.get_rect(center=pos)

class Rotate_Image(pygame.sprite.Sprite):
	def __init__(self, image_filename, size, pos, deviation=(0, 0), color=None, parent=None):
		super().__init__()
		self.size = Utils.int_tuple(size)
		self.pos = pos
		self.deviation = deviation
		self.angle = 0
		self.speed = 0
		self.parent = parent
		self.original_image = pygame.image.load(image_filename)
		self.original_image = pygame.transform.scale(self.original_image, self.size)
		self.transition = self.original_image.copy()
		self.image = self.transition
		self.rect = self.image.get_rect(center=Setting.Environment.NULL_POINT)
		if color != None:
			self.change_color(color)
	def change_color(self, color):
		coloredSurface = self.original_image.copy()
		Utils.color_surface(coloredSurface, color)
		self.transition = coloredSurface
	def update(self):
		self.image = pygame.transform.rotozoom(self.transition, self.angle, 1)
		center = Utils.rotate(Utils.mul_tuple(self.deviation, -1), self.angle)
		center = Utils.int_tuple(Utils.sum_tuple(center, self.pos))
		self.rect = self.image.get_rect(center=center)
	def turn(self, angle):
		self.angle += angle
		self.angle %= 360

class Shell_Explosion(Rotate_Image):
	def __init__(self, size, pos, player):
		super().__init__(Graphic.Tank.SHELL_EXPLOSION, size, pos)
		self.player = player
		self.last = round(Setting.Environment.SHELL_EXPLOSION_LAST / Setting.Window.MSPF)
	def update(self):
		super().update()
		self.last -= 1

class Cannon_Explosion(Rotate_Image):
	def __init__(self, size, pos, angle, player):
		super().__init__(Graphic.Tank.CANNON_EXPLOSION, size, pos)
		self.player = player
		self.angle = angle
		self.last = round(Setting.Environment.CANNON_EXPLOSION_LAST / Setting.Window.MSPF)
	def update(self):
		super().update()
		self.last -= 1

class Shell(Rotate_Image):
	def __init__(self, size, pos, angle, tank):
		super().__init__(Graphic.Tank.TANK_SHELL, size, pos, parent=tank)
		self.angle = angle
		self.init_pos = pos
		self.body = tank.body
		self.player = tank.player
		self.explo_width = tank.tank_gameplay.SHELL_EXPLOSION_WIDTH
		self.damage = tank.tank_gameplay.SHELL_DAMAGE
		self.acceleration = tank.tank_gameplay.SHELL_SPEED
	def update(self):
		super().update()
		total_angle = self.angle + Setting.Tank_Model.Tank.INIT_ANGLE
		self.speed = Utils.next_speed(self.speed, Utils.acceleration(self.acceleration))
		distance = Utils.scale(self.speed, (1000, Setting.Window.MSPF))
		self.pos = Utils.mirror(Utils.translate(Utils.mirror(self.pos), distance, total_angle))
	def is_out_boundary(self):
		max_dim = max(self.size)
		width, height = Setting.Window.WIDTH, Setting.Window.HEIGHT
		if self.pos[0] - max_dim / 2 >= width or self.pos[0] + max_dim / 2 <= 0:
			return True
		if self.pos[1] - max_dim / 2 >= height or self.pos[1] + max_dim / 2 <= 0:
			return True
		return False

class Arty_Shell(Rotate_Image):
	def __init__(self, size, player, origin, land_point):
		super().__init__(Graphic.Tank.TANK_SHELL, size, origin)
		self.angle = Utils.angle_onscreen_seg(origin, land_point)
		self.init_pos = origin
		self.land_point = land_point
		self.player = player
		gameplay = Setting.Gameplay.SPG
		self.explo_width = gameplay.SHELL_EXPLOSION_WIDTH
		self.damage = gameplay.SHELL_DAMAGE
		self.acceleration = gameplay.SHELL_SPEED
	def update(self):
		super().update()
		self.speed = Utils.next_speed(self.speed, Utils.acceleration(self.acceleration))
		distance = Utils.scale(self.speed, (1000, Setting.Window.MSPF))
		new_pos = Utils.mirror(Utils.translate(Utils.mirror(self.pos), distance, self.angle))
		if Utils.is_between(self.pos, new_pos, self.land_point):
			self.pos = self.land_point
		else:
			self.pos = new_pos

class Flame(pygame.sprite.Sprite):
	CHANGE = 100
	def __init__(self, size, pos):
		super().__init__()
		self.images = []
		self.pos = pos
		mul = max(size) / max(Setting.Tank_Model.Tank.FLAME_ACTUAL)
		scale = Utils.int_tuple(Utils.mul_tuple(Setting.Tank_Model.Tank.FLAME_DIMENSION, mul))
		for i in range(Graphic.Tank.Flame.NUMBER):
			image = pygame.image.load(Graphic.Tank.Flame.get_flame(i))
			image = pygame.transform.scale(image, scale)
			self.images.append(image)
		self.index = 0
		self.last_change = time.time() * 1000
	def update(self):
		now = time.time() * 1000
		if now - self.last_change > Flame.CHANGE:
			self.index += 1
			self.index %= Graphic.Tank.Flame.NUMBER
		self.image = self.images[self.index]
		self.rect = self.image.get_rect(center=self.pos)

class Wall(pygame.sprite.Sprite):
	def __init__(self, wall_from, wall_to, wall_height):
		super().__init__()
		min_tuple = tuple(min(tuple(x)) for x in zip(wall_from, wall_to))
		max_tuple = tuple(max(tuple(x)) for x in zip(wall_from, wall_to))
		self.top_left = min_tuple
		self.down_right = max_tuple
		self.height = wall_height
		self.size = Utils.sum_tuple(max_tuple, Utils.mul_tuple(min_tuple, -1))
		self.size = tuple(max(Setting.Environment.INF_WALL, x) for x in self.size)
		self.image = pygame.Surface(self.size)
		self.image.fill(Setting.Environment.WALL_COLOR)
		self.rect = pygame.Rect(min_tuple, self.size)

class Boundary(pygame.sprite.Sprite):
	def __init__(self, b_from, b_to):
		super().__init__()
		min_tuple = tuple(min(tuple(x)) for x in zip(b_from, b_to))
		max_tuple = tuple(max(tuple(x)) for x in zip(b_from, b_to))
		self.size = Utils.sum_tuple(max_tuple, Utils.mul_tuple(min_tuple, -1))
		self.image = pygame.Surface(self.size)
		self.rect = pygame.Rect(min_tuple, self.size)
		
class Progess_Bar(pygame.sprite.Sprite):
	def __init__(self, color_full, color_miss, size):
		super().__init__()
		self.color_full = color_full
		self.color_miss = color_miss
		self.size = size
		self.percent = 1
		self.image = pygame.Surface(self.size)
		self.pos = Setting.Environment.NULL_POINT
		self.rect = self.image.get_rect(center=self.pos)

	def update(self):
		full_width = int(self.percent * self.image.get_size()[0])
		for x in range(full_width):
			for y in range(self.image.get_size()[1]):
				self.image.set_at([x, y], self.color_full)
		for x in range(full_width, self.image.get_size()[0]):
			for y in range(self.image.get_size()[1]):
				self.image.set_at([x, y], self.color_miss)
		self.rect = self.image.get_rect(center=self.pos)

class Name_Bar(pygame.sprite.Sprite):
	def __init__(self, name, font_size, color):
		super().__init__()
		self.name = name
		self.font_size = font_size
		self.color = color
		self.font = pygame.font.SysFont(Setting.Window.FONT, font_size)
		self.image = self.font.render(name, True, color)
		self.pos = Setting.Environment.NULL_POINT
		self.rect = self.image.get_rect(center=self.pos)

	def update(self):
		self.rect = self.image.get_rect(center=self.pos)