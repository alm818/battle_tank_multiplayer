from setting import Setting
from scripts.outgame import misc
from assets import Sound
import pygame, math, random

class Utils:
	# GLOBAL_METHOD
	def damagify(shell, pos, tank_body_group):
		from sprite import Sprite_Pixel
		total_points = int(shell.explo_width ** 2 / 2)
		devi = shell.explo_width / 2
		top_left = tuple(int(x - devi) for x in pos)
		dic = {}
		for x in range(top_left[0], top_left[0] + shell.explo_width):
			for y in range(top_left[1], top_left[1] + shell.explo_width):
				pixel = Sprite_Pixel((x, y))
				for body in pygame.sprite.spritecollide(pixel, tank_body_group, False):
					if body not in dic:
						dic[body] = 0
					dic[body] += 1
		sum_points = sum(dic.values())
		if sum_points >= total_points:
			damage = shell.damage
		else:
			damage = shell.damage * (sum_points / total_points)
		for body in dic:
			body.parent.damagify(damage * (dic[body] / sum_points), shell.player)
	def find_intersection(shell, pos, bodies, center=True):
		from sprite import Sprite_Pixel
		body_group = pygame.sprite.Group()
		for body in bodies:
			body_group.add(body)
		pixel_init = Sprite_Pixel(shell.init_pos)
		if pygame.sprite.spritecollide(pixel_init, body_group, False):
			return shell.init_pos
		if shell.speed / (Setting.Window.MSPF * Utils.acceleration(shell.acceleration)) <= Setting.Environment.THRESHOLD_FRAME_SHELL:
			return pos
		d = Utils.sum_tuple(pos, Utils.mul_tuple(shell.init_pos, -1))
		disect = sum(abs(x) for x in d)
		t = 0
		previous = pos[0], pos[1]
		while True:
			t += 1
			now = Utils.sum_tuple(pos, Utils.mul_tuple(d, -t / disect))
			pixel_now = Sprite_Pixel(now)
			pixel_previous = Sprite_Pixel(previous)
			if not pygame.sprite.spritecollide(pixel_now, body_group, False) and pygame.sprite.spritecollide(pixel_previous, body_group, False):
				return previous
			elif t > disect:
				if center:
					minus_d = Utils.mul_tuple(d, -1)
					r, alpha = Utils.carte_to_polar(minus_d)
					threshold_radius = math.sqrt(5 / 4 * (shell.size[0] ** 2))
					threshold_forward = shell.speed / 1000 * Setting.Window.MSPF
					forward = 0
					radius = 0
					while True:
						radius += Setting.Environment.SEARCH_DISTANCE
						up_pos = radius, alpha + math.radians(90)
						up_pos = Utils.sum_tuple(pos, Utils.polar_to_carte(*up_pos))
						up = Utils.find_intersection(shell, up_pos, bodies, False)
						if up != None:
							return up
						down_pos = radius, alpha - math.radians(90)
						down_pos = Utils.sum_tuple(pos, Utils.polar_to_carte(*down_pos))
						down = Utils.find_intersection(shell, down_pos, bodies, False)
						if down != None:
							return down
						if radius > threshold_radius:
							radius = 0
							forward += Setting.Environment.SEARCH_DISTANCE
						if forward > threshold_forward:
							return pos
				else:
					return None
			else:
				previous = now
	def self_remove_tank(body, predicted_tanks):
		new = []
		for tank in predicted_tanks:
			if body.pos != tank.pos:
				new.append(tank)
		return new
	def channel_idle(index):
		return index
	def channel_move(index):
		return 10 + index
	def channel_cannon(index):
		return 20 + index
	def channel_misc(channels):
		index = Setting.Sound.MISC
		while True:
			if not channels[index].get_busy():
				return index
			else:
				index += 1
	def damage_sound(damage, full_hp):
		percent = damage / full_hp
		if percent <= Setting.Gameplay.Tank.LOW_DAMAGE:
			link = Sound.Tank.Being_Hit.LOW_DAMAGE
		elif percent <= Setting.Gameplay.Tank.MEDIUM_DAMAGE:
			link = Sound.Tank.Being_Hit.MEDIUM_DAMAGE
		else:
			link = Sound.Tank.Being_Hit.HIGH_DAMAGE
		sound = pygame.mixer.Sound(link)
		sound.set_volume(Setting.Sound.DEFAULT_MULTIPLIER)
		return sound
	def proc_chance(chance):
		value = random.random()
		return value < chance
	# TUPLE METHOD
	def sum_tuple(t1, t2):
		return tuple(sum(x) for x in zip(t1, t2))
	def mul_tuple(t, c):
		return tuple(c * x for x in t)
	def int_tuple(t):
		return tuple(int(x) for x in t)

	# MATH AND GEOMETRY METHOD
	def same_sign(sign, value):
		if sign < 0:
			return -abs(value)
		else:
			return abs(value)
	def acceleration(speed):
		return speed[1] / speed[0]
	def next_speed(init_speed, acceleration):
		return init_speed + acceleration * Setting.Window.MSPF
	def distance(pos, pos2=(0, 0)):
		return math.sqrt((pos[0] - pos2[0]) ** 2 + (pos[1] - pos2[1]) ** 2)
	def carte_to_polar(pos):
		r = Utils.distance(pos)
		alpha = math.atan2(pos[1], pos[0])
		return r, alpha
	def polar_to_carte(r, alpha):
		return r * math.cos(alpha), r * math.sin(alpha)
	def scale(fixed, ratio):
		return fixed / ratio[0] * ratio[1]
	def rotate(pos, degree_angle):
		r, alpha = Utils.carte_to_polar(pos)
		alpha -= math.radians(degree_angle)
		return Utils.polar_to_carte(r, alpha)
	def translate(pos, distance, angle):
		trans_vec = Utils.polar_to_carte(distance, math.radians(angle))
		return Utils.sum_tuple(trans_vec, pos)
	def mirror(pos):
		return (pos[0], -pos[1], *pos[2:])
	def center_boundary_distance(size, angle):
		angle %= 360
		half_h, half_v = Utils.mul_tuple(size, 1 / 2) 
		if angle < 90:
			alpha = math.radians(angle)
		elif 90 <= angle < 180:
			alpha = math.radians(180 - angle)
		elif 180 <= angle < 270:
			alpha = math.radians(angle - 180)
		else:
			alpha = math.radians(360 - angle)
		beta = math.pi / 2 - alpha
		if alpha == math.pi:
			return half_h
		if beta == math.pi:
			return half_v
		v = half_v / math.cos(alpha)
		h = half_h / math.cos(beta)
		return min(v, h)
	def ccw(A, B, C):
		return (C[1] - A[1]) * (B[0] - A[0]) > (B[1] - A[1]) * (C[0] - A[0])
	def line_intersect(A, B, C, D):
		# Return true if line segments AB and CD intersect
		return Utils.ccw(A,C,D) != Utils.ccw(B,C,D) and Utils.ccw(A,B,C) != Utils.ccw(A,B,D)
	def rec_intersect(A, B, M, N):
		# Return true if line segment AB intersects rectangle formed by M, N as 2 opposite corners
		top_left  = tuple(min(tuple(x)) for x in zip(M, N))
		down_right = tuple(max(tuple(x)) for x in zip(M, N))
		top_right = down_right[0], top_left[1]
		down_left = top_left[0], down_right[1]
		return Utils.line_intersect(A, B, top_left, top_right) or Utils.line_intersect(A, B, top_right, down_right) \
			or Utils.line_intersect(A, B, down_right, down_left) or Utils.line_intersect(A, B, down_left, top_left)
	def have_obstacle(server_map, pos1, pos2):
		for wall in server_map.walls:
			if Utils.rec_intersect(pos1, pos2, wall[misc.Map.from_], wall[misc.Map.to_]):
				return True
		return False
	def find_mid(x, first, last, totalx):
		return x * (last - first) / totalx + first
	def find_shortest_distance(origin, angle, body_group):
		from sprite import Sprite_Pixel
		distance = 0
		while True:
			check_point = Utils.mirror(Utils.translate(Utils.mirror(origin), distance, angle))
			pixel = Sprite_Pixel(check_point)
			if pygame.sprite.spritecollide(pixel, body_group, False):
				return distance
			distance += Setting.Environment.INF_WALL
	def line(p1, p2):
		A = p1[1] - p2[1]
		B = p2[0] - p1[0]
		C = p1[0] * p2[1] - p2[0] * p1[1]
		return A, B, -C
	def is_between(A, B, M):
		# Return True if M is between AB, False otherwise
		# Assuming M is on line AB
		return min(A[0], B[0]) <= M[0] <= max(A[0], B[0]) and min(A[1], B[1]) <= M[1] <= max(A[1], B[1])
	def line_intersection(A, B, P, Q):
		# Return intersection point if line segments AB and PQ intersect, None otherwise
		L1 = Utils.line(A, B)
		L2 = Utils.line(P, Q)
		D  = L1[0] * L2[1] - L1[1] * L2[0]
		Dx = L1[2] * L2[1] - L1[1] * L2[2]
		Dy = L1[0] * L2[2] - L1[2] * L2[0]
		if D != 0:
			x = Dx / D
			y = Dy / D
			M = (x, y)
			if Utils.is_between(A, B, M) and Utils.is_between(P, Q, M):
				return M
		return None
	def convex_polygon_intersection(A, B, P):
		res = set()
		for i in range(len(P)):
			intersection = Utils.line_intersection(A, B, P[i], P[(i + 1) % len(P)])
			if intersection != None:
				res.add(intersection)
		return res
	def find_y(x, init_pos, theta, alpha, v):
		t = (x - init_pos[0]) / (v * math.cos(theta) * math.cos(alpha))
		return v * math.sin(theta) * math.cos(alpha) * t + init_pos[1]
	def find_x(y, init_pos, theta, alpha, v):
		t = (y - init_pos[1]) / (v * math.sin(theta) * math.cos(alpha))
		return v * math.cos(theta) * math.cos(alpha) * t + init_pos[0]
	def find_bound_point(init_pos, theta, alpha, v):
		theta %= (2 * math.pi)
		if 0 <= theta < math.pi / 2:
			x = Setting.Window.WIDTH
			y = Utils.find_y(x, init_pos, theta, alpha, v)
		elif math.pi / 2 <= theta < math.pi:
			y = Setting.Window.HEIGHT
			x = Utils.find_x(y, init_pos, theta, alpha, v)
		elif math.pi <= theta < 3 / 2 * math.pi:
			x = 0
			y = Utils.find_y(x, init_pos, theta, alpha, v)
		else:
			y = 0
			x = Utils.find_x(y, init_pos, theta, alpha, v)
		return (x, y)
	def find_t_in_xy_plane(init_pos, theta, alpha, v, g, P):
		A = (init_pos[0], init_pos[1])
		B = Utils.find_bound_point(init_pos, theta, alpha, v)
		intersection = list(Utils.convex_polygon_intersection(A, B, P))
		if intersection:
			first = intersection[0]
			if len(intersection) == 1:
				second = intersection[0]
			else:
				second = intersection[1]
			t_first = (first[0] - init_pos[0]) / (v * math.cos(theta) * math.cos(alpha))
			t_second = (second[0] - init_pos[0]) / (v * math.cos(theta) * math.cos(alpha))
			t_st = min(t_first, t_second)
			t_fn = max(t_first, t_second)
			return t_st, t_fn
		else:
			return None
	def find_t_same_side(init_pos, alpha, v, g, height, t_st, t_fn):
		max_t = v * math.sin(alpha) / g
		z_st = Utils.find_height_at_t(t_st, init_pos, alpha, v, g)
		z_fn = Utils.find_height_at_t(t_fn, init_pos, alpha, v, g)
		land_t = Utils.find_land_t(init_pos, alpha, v, g)
		if t_st <= max_t and t_fn <= max_t:
			if z_st >= height:
				return land_t
			else:
				return t_st
		elif t_st >= max_t and t_fn >= max_t:
			if z_fn >= height:
				return land_t
			elif z_fn <= height <= z_st:
				c = height - init_pos[2]
				delta = (v * math.sin(alpha)) ** 2 - 2 * g * c
				return (v * math.sin(alpha) + math.sqrt(delta)) / g
			else:
				return t_st
	def find_land_t(init_pos, alpha, v, g):
		delta = (v * math.sin(alpha)) ** 2 + 2 * g * init_pos[2]
		return (v * math.sin(alpha) + math.sqrt(delta)) / g
	def find_t_in_space(init_pos, alpha, theta, R, g, height, P):
		v = Utils.find_init_v_of_range(init_pos, R, alpha, g)
		max_t = v * math.sin(alpha) / g
		res = Utils.find_t_in_xy_plane(init_pos, theta, alpha, v, g, P)
		land_t = Utils.find_land_t(init_pos, alpha, v, g)
		if res != None:
			t_st, t_fn = res
			if t_st < max_t and t_fn > max_t:
				return min(Utils.find_t_same_side(init_pos, alpha, v, g, height, t_st, max_t),
					Utils.find_t_same_side(init_pos, alpha, v, g, height, max_t, t_fn))
			else:
				return Utils.find_t_same_side(init_pos, alpha, v, g, height, t_st, t_fn)
		else:
			return land_t
	def find_init_v_of_range(init_pos, R, alpha, g):
		h = init_pos[2]
		return math.sqrt(g * R * R / (2 * h * (math.cos(alpha) ** 2) + R * math.sin(2 * alpha)))
	def find_height_at_t(t, init_pos, alpha, v, g):
		return init_pos[2] + v * math.sin(alpha) * t - g / 2 * t * t
	def find_xy_point_at_t(t, init_pos, alpha, theta, v):
		x = v * math.cos(theta) * math.cos(alpha) * t + init_pos[0]
		y = v * math.sin(theta) * math.cos(alpha) * t + init_pos[1]
		return x, y
	def find_land_origin(init_pos, alpha, theta, v, g):
		land_t = Utils.find_land_t(init_pos, alpha, v, g)
		return Utils.find_xy_point_at_t(land_t, init_pos, alpha, theta, v)
	def find_P_of_tank(tank):
		center = tank.body.pos
		width = tank.body.size[0]
		height = tank.body.size[1]
		angle = tank.body.angle
		tl = Utils.sum_tuple(center, (-width / 2, -height / 2))
		tr = Utils.sum_tuple(center, (width / 2, -height / 2))
		dr = Utils.sum_tuple(center, (width / 2, height / 2))
		dl = Utils.sum_tuple(center, (-width / 2, height / 2))
		tl = Utils.rotate_about_point(center, tl, angle)
		tr = Utils.rotate_about_point(center, tr, angle)
		dr = Utils.rotate_about_point(center, dr, angle)
		dl = Utils.rotate_about_point(center, dl, angle)
		return [tl, tr, dr, dl]
	def rotate_about_point(origin, pos, angle):
		out_pos = Utils.sum_tuple(pos, Utils.mul_tuple(origin, - 1))
		rotated = Utils.rotate(out_pos, angle)
		return Utils.sum_tuple(origin, rotated)
	def random_circle_point(origin, radius):
		ran_radius = random.uniform(0, radius)
		ran_angle = random.uniform(0, 360)
		point = Utils.translate(origin, ran_radius, ran_angle)
		return point
	def angle_onscreen_seg(origin, end):
		out_vector = Utils.sum_tuple(Utils.mirror(end), Utils.mul_tuple(Utils.mirror(origin), -1))
		r, theta = Utils.carte_to_polar(out_vector)
		return math.degrees(theta)
	def sound_intensity_at_distance(x):
		res = (math.log10(Setting.Detection.SEE_SPEED / (x + Setting.Sound.K)) ** 2) * Setting.Sound.HEARABLE * Setting.Sound.DEFAULT_MULTIPLIER
		if res < Setting.Sound.HEARABLE * Setting.Sound.DEFAULT_MULTIPLIER:
			return 0
		else:
			return res
	#GRAPHIC METHOD
	def is_green(color):
		return color.g > color.r and color.g > color.b
	def color_surface(surface, color):
		for x in range(surface.get_size()[0]):
			for y in range(surface.get_size()[1]):
				if Utils.is_green(surface.get_at([x, y])):
					surface.set_at([x, y], color)
	def dotted_line(screen, A, B, color, full_seg, miss_seg):
		total_seg = full_seg + miss_seg
		distance = Utils.distance(A, B)
		full_count = int(distance // total_seg)
		for i in range(full_count):
			miss = i * total_seg + miss_seg
			miss_x = Utils.find_mid(miss, A[0], B[0], distance)
			miss_y = Utils.find_mid(miss, A[1], B[1], distance)
			full = (i + 1) * total_seg
			full_x = Utils.find_mid(full, A[0], B[0], distance)
			full_y = Utils.find_mid(full, A[1], B[1], distance)
			pygame.draw.aaline(screen, color, (miss_x, miss_y), (full_x, full_y))
	def SPG_blit(screen, owner_tank):
		screen.blit(owner_tank.protractor, owner_tank.protractor_rect)
		tank_model = owner_tank.tank_model
		width = tank_model.PROTRACTOR_FIXED_WIDTH
		origin = Utils.sum_tuple(tank_model.PROTRACTOR_POS, (-width / 2, width / 2))
		end = Utils.mirror(Utils.translate(Utils.mirror(origin), width, owner_tank.alpha_angle))
		pygame.draw.line(screen, tank_model.PROTRACTOR_INDICATOR_COLOR, origin, end, tank_model.PROTRACTOR_INDICATOR_WIDTH)
		font = pygame.font.SysFont(Setting.Window.FONT, Setting.Window.DEGREE_FONT_SIZE)
		text = font.render(str(round(owner_tank.alpha_angle, 1)) + '°', True, tank_model.PROTRACTOR_DEGREE_COLOR)
		center = Utils.mirror(Utils.translate(Utils.mirror(origin), width + 10, owner_tank.alpha_angle))
		textpos = text.get_rect(center=center)
		screen.blit(text, textpos)
	def dotted_point(point, init_pos, alpha, g, list_height, list_Ps):
		min_t = 10 ** 9
		origin = init_pos[0], init_pos[1]
		out_vector = Utils.sum_tuple(point, Utils.mul_tuple(origin, -1))
		r, theta = Utils.carte_to_polar(out_vector)
		R = Utils.distance(origin, point)
		v = Utils.find_init_v_of_range(init_pos, R, alpha, g)
		for i in range(len(list_height)):
			height = list_height[i]
			P = list_Ps[i]
			t = Utils.find_t_in_space(init_pos, alpha, -theta, R, g, height, P)
			min_t = min(t, min_t)
		land_point = Utils.int_tuple(Utils.mirror(Utils.find_xy_point_at_t(min_t, Utils.mirror(init_pos), alpha, theta, v)))
		return land_point
	def dotted_circle_blit(screen, color, init_pos, land_origin, land_radius, dots, alpha, g, list_height, list_Ps):
		devi_angle = 360 / dots
		angle = -devi_angle
		for i in range(dots):
			angle += devi_angle
			dot = Utils.translate(land_origin, land_radius, angle)
			land_point = Utils.dotted_point(dot, init_pos, alpha, g, list_height, list_Ps)
			pygame.draw.circle(screen, color, land_point, 1)