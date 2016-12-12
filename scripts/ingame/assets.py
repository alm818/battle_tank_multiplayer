from random import randint

class Graphic:
	class Tank:
		class Flame:
			NUMBER = 6
			def get_flame(number):
				return 'assets/graphic/tank/flame/flame{number}.png'.format(number=number)
		TANK_SHELL = 'assets/graphic/tank/tank_shell.png'
		CANNON_EXPLOSION = 'assets/graphic/tank/cannon_explosion.png'
		SHELL_EXPLOSION = 'assets/graphic/tank/shell_explosion.png'
	class Heavy_Tank:
		BODY = 'assets/graphic/heavy_tank/body.png'
		TURRET = 'assets/graphic/heavy_tank/turret.png'
	class Light_Tank:
		BODY = 'assets/graphic/light_tank/body.png'
		TURRET = 'assets/graphic/light_tank/turret.png'
	class SPG:
		BODY = 'assets/graphic/spg/body.png'
		TURRET = 'assets/graphic/spg/turret.png'
		PROTRACTOR = 'assets/graphic/spg/protractor.png'
	class Tank_Destroyer:
		BODY = 'assets/graphic/tank_destroyer/body.png'
		TURRET = 'assets/graphic/tank_destroyer/turret.png'
class Sound:
	class Tank:
		class Being_Hit:
			HIGH_DAMAGE = 'assets/sound/tank/being_hit/high_damage.wav'
			MEDIUM_DAMAGE = 'assets/sound/tank/being_hit/medium_damage.wav'
			LOW_DAMAGE = 'assets/sound/tank/being_hit/low_damage.wav'
		class Destroyed:
			ENEMY = 'assets/sound/tank/destroyed/enemy.wav'
			SELF = 'assets/sound/tank/destroyed/self.wav'
		class Hit:
			NUMBER = 4
			def get_hit():
				number = randint(0, Sound.Tank.Hit.NUMBER - 1)
				return 'assets/sound/tank/hit/hit{number}.wav'.format(number=number)
		class Misc:
			ARTY_HIT = 'assets/sound/tank/misc/arty_hit.wav'
			READY_FIRE = 'assets/sound/tank/misc/ready-to-fire.wav'
			WALL_HIT = 'assets/sound/tank/misc/wall_hit.wav'
			VICTORY = 'assets/sound/tank/misc/victory.wav'
			DEFEAT = 'assets/sound/tank/misc/defeat.wav'
	class Heavy_Tank:
		CANNON_EXPLOSION = 'assets/sound/heavy_tank/cannon_explosion.wav'
		IDLE = 'assets/sound/heavy_tank/idle.wav'
		MOVE = 'assets/sound/heavy_tank/move.wav'
	class Light_Tank:
		CANNON_EXPLOSION = 'assets/sound/light_tank/cannon_explosion.wav'
		IDLE = 'assets/sound/light_tank/idle.wav'
		MOVE = 'assets/sound/light_tank/move.wav'
	class SPG:
		CANNON_EXPLOSION = 'assets/sound/spg/cannon_explosion.wav'
		IDLE = 'assets/sound/spg/idle.wav'
		MOVE = 'assets/sound/spg/move.wav'
	class Tank_Destroyer:
		CANNON_EXPLOSION = 'assets/sound/tank_destroyer/cannon_explosion.wav'
		IDLE = 'assets/sound/tank_destroyer/idle.wav'
		MOVE = 'assets/sound/tank_destroyer/move.wav'