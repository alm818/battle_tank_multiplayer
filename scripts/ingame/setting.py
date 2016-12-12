import pygame, math

class Setting:
	def init():
		info = pygame.display.Info()
		width, height = Setting.Window.WIDTH, Setting.Window.HEIGHT
		inf_bound = Setting.Environment.INF_WALL * 2
		Setting.Environment.BOUNDARY = [
			[(-inf_bound, -inf_bound), (width + inf_bound, 0)],
			[(width, -inf_bound), (width + inf_bound, height + inf_bound)],
			[(-inf_bound, height), (width + inf_bound, height + inf_bound)],
			[(-inf_bound, -inf_bound), (0, height + inf_bound)]
		]
		from utils import Utils
		ht_model = Setting.Tank_Model.Heavy_Tank
		ht_model.SHELL_FIXED_WIDTH = Utils.scale(ht_model.TURRET_FIXED_WIDTH, ht_model.TURRET_SHELL_RATIO)
		lt_model = Setting.Tank_Model.Light_Tank
		lt_model.SHELL_FIXED_WIDTH = Utils.scale(lt_model.TURRET_FIXED_WIDTH, lt_model.TURRET_SHELL_RATIO)
		spg_model = Setting.Tank_Model.SPG
		spg_model.SHELL_FIXED_WIDTH = Utils.scale(spg_model.TURRET_FIXED_WIDTH, spg_model.TURRET_SHELL_RATIO)
		td_model = Setting.Tank_Model.Tank_Destroyer
		td_model.SHELL_FIXED_WIDTH = Utils.scale(td_model.TURRET_FIXED_WIDTH, td_model.TURRET_SHELL_RATIO)
		Setting.Detection.MAX_SPEED = Setting.Gameplay.Light_Tank.TANK_FORWARD_SPEED[1]
		v = Setting.Gameplay.SPG.SHELL_SPEED[1]
		h = Setting.Tank_Model.SPG.BASE_HEIGHT
		alpha = math.radians(45)
		R = Setting.Gameplay.SPG.MAX_RANGE
		Setting.Environment.G = v * v * (h / R + 1) / R
		power = math.sqrt(1 / Setting.Sound.HEARABLE)
		Setting.Sound.K = Setting.Detection.SEE_SPEED / (10 ** power)
	def scale(fixed, ratio):
		return fixed / ratio[0] * ratio[1]
	class Window:
		WIDTH = 1366
		HEIGHT = 768
		MSPF = 40
		FONT = 'Sans'
		NAME_FONT_SIZE = 11
		DEGREE_FONT_SIZE = 12
		RELOAD_FONT_SIZE = 30
		END_FONT_SIZE = 80
	class Tank_Model:
		class Tank:
			RELOAD_POS = (683, 10)
			SHELL_RATIO = (80, 68)
			INIT_ANGLE = 90
			FLAME_DIMENSION = (512, 512)
			FLAME_ACTUAL = (206, 307)
		class Heavy_Tank:
			TURRET_DIMENSION = (232, 456)
			TURRET_FIXED_WIDTH = 15
			TURRET_VERTICAL_DEVIATION_RATIO = (228, 360)
			TURRET_SHELL_RATIO = (232, 91)
			BODY_DIMENSION = (618, 642)
			BODY_FIXED_WIDTH = 25
			BODY_VERTICAL_DEVIATION_RATIO = (1, 1)
		class Light_Tank:
			TURRET_DIMENSION = (107, 300)
			TURRET_FIXED_WIDTH = 11
			TURRET_VERTICAL_DEVIATION_RATIO = (186, 290)
			TURRET_SHELL_RATIO = (107, 42)
			BODY_DIMENSION = (305, 414)
			BODY_FIXED_WIDTH = 18
			BODY_VERTICAL_DEVIATION_RATIO = (207, 268)
		class SPG:
			TURRET_DIMENSION = (220, 609)
			TURRET_FIXED_WIDTH = 15
			TURRET_VERTICAL_DEVIATION_RATIO = (305, 518)
			TURRET_SHELL_RATIO = (220, 73)
			BODY_DIMENSION = (478, 610)
			BODY_FIXED_WIDTH = 23
			BODY_VERTICAL_DEVIATION_RATIO = (305, 550)
			PROTRACTOR_DIMENSION = (454, 456)
			PROTRACTOR_FIXED_WIDTH = 50
			PROTRACTOR_POS = (500, 500)
			PROTRACTOR_INDICATOR_WIDTH = 2
			PROTRACTOR_INDICATOR_COLOR = pygame.Color('RED')
			PROTRACTOR_DEGREE_COLOR = pygame.Color('BLACK')
			BASE_HEIGHT = 25 / 3
			TURRET_LENGTH = 30
		class Tank_Destroyer:
			TURRET_DIMENSION = (220, 609)
			TURRET_FIXED_WIDTH = 15
			TURRET_VERTICAL_DEVIATION_RATIO = (305, 492)
			TURRET_SHELL_RATIO = (220, 73)
			BODY_DIMENSION = (478, 610)
			BODY_FIXED_WIDTH = 23
			BODY_VERTICAL_DEVIATION_RATIO = (305, 190)
	class Environment:
		INF_VEL = 1
		INF_WALL = 10
		VICTORY_COLOR = pygame.Color('GOLD')
		DEFEAT_COLOR = pygame.Color('RED')
		BURNED_COLOR = pygame.Color('BLACK')
		RELOAD_COLOR = pygame.Color('RED')
		FINISH_COLOR = pygame.Color('GREEN')
		ENEMY_COLOR = pygame.Color('RED')
		ALLY_COLOR = pygame.Color('BLUE')
		WALL_COLOR = pygame.Color('BLACK')
		BACKGROUND_COLOR = pygame.Color('WHITE')
		HP_FULL_COLOR = pygame.Color('GREEN')
		HP_MISS_COLOR = pygame.Color('RED')
		HP_BAR_HEIGHT = 5
		CANNON_EXPLOSION_RATIO = (46, 64)
		CANNON_EXPLOSION_LAST = 100
		SHELL_EXPLOSION_RATIO = (440, 435)
		SHELL_EXPLOSION_LAST = 140
		THRESHOLD_DISTANCE = 20
		THRESHOLD_FRAME_SHELL = 3
		SEARCH_DISTANCE = 1 / 2
		NULL_POINT = (-10 ** 3, -10 ** 3)
		FRICTION_ACCELERATION = 20 / 1000
	class Gameplay:
		class Tank:
			LOW_DAMAGE = 0.1
			MEDIUM_DAMAGE = 0.35
			HIGH_DAMAGE = 0.6
		class Heavy_Tank:
			HP = 2100
			TURRET_TURN_DEG = 40
			BODY_TURN_DEG = 35
			TANK_FORWARD_SPEED = (2000, 50)
			TANK_BACKWARD_SPEED = (1000, 30)	
			SHELL_DAMAGE = 350
			SHELL_EXPLOSION_WIDTH = 15
			SHELL_SPEED = (500, 800)
			RELOAD_TIME = 8
		class Light_Tank:
			HP = 1000
			TURRET_TURN_DEG = 56
			BODY_TURN_DEG = 48
			TANK_FORWARD_SPEED = (2000, 90)
			TANK_BACKWARD_SPEED = (800, 35)
			SHELL_DAMAGE = 230
			SHELL_EXPLOSION_WIDTH = 10
			SHELL_SPEED = (500, 650)
			RELOAD_TIME = 4.5
		class SPG:
			HP = 880
			BODY_TURN_DEG = 25
			TANK_FORWARD_SPEED = (1500, 40)
			TANK_BACKWARD_SPEED = (750, 20)
			SHELL_DAMAGE = 900
			SHELL_EXPLOSION_WIDTH = 30
			SHELL_SPEED = (600, 1200)
			RELOAD_TIME = 16
			MAX_MOVE_AMPLI = 2.0
			MAX_ROTATE_AMPLI = 1.5
			MAX_DIPERSION = 35
			MAX_ANGLE_ELEVATION = 60
			MIN_ANGLE_ELEVATION = 0
			TURRET_ELEVATION_DEG = 15
			MAX_RANGE = 1166
			CIRCLE_DOTS = 12
			AIM_TIME_MOVE = 4000
			AIM_TIME_ROTATE = 2000
			AIM_COLOR = pygame.Color('BLUE')
		class Tank_Destroyer:
			HP = 1500
			BODY_TURN_DEG = 24
			TANK_FORWARD_SPEED = (2000, 45)
			TANK_BACKWARD_SPEED = (1000, 25)
			SHELL_DAMAGE = 600
			SHELL_EXPLOSION_WIDTH = 15
			SHELL_SPEED = (600, 1000)
			RELOAD_TIME = 12
			AIM_COLOR = pygame.Color('BLUE')
			FULL_SEG = 1
			MISS_SEG = 5
	class Detection:
		DETECT_TIME = 1000
		SHELL_EXPOSED_TIME = 3000
		LISTEN_IDLE = 125
		LISTEN_SPEED = 250
		SEE_IDLE = 400
		SEE_SPEED = 550
	class Sound:
		HEARABLE = 0.05
		DEFAULT_MULTIPLIER = 0.5
		CHANNEL = 45
		BEING_HIT = 30
		DESTROYED = 31
		HIT = 32
		READY = 33
		MISC = 35
		HIT_CHANCE = 2 / 3