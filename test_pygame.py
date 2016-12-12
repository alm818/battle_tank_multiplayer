import pygame
from scripts.ingame import assets, global_, setting, tank
from assets import Assets
from global_ import Global
from setting import Setting
from tank import Heavy_Tank, Light_Tank, SPG, Tank_Destroyer

def init():
	pygame.init()
	Global.init()
	Setting.init()

if __name__ == '__main__':
	init()

	screen = pygame.display.set_mode(Setting.Window.SCREEN_SIZE)

	tank = Light_Tank('Tank 1', pygame.Color('BLUE'), (100, 100))
	tank2 = Heavy_Tank('Tank 2', pygame.Color('RED'), (200, 100))
	Global.add_wall(Assets.Map.MAP1)
	Global.add_boundary()
	Global.game_quit = False

	while True:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				Global.game_quit = True
				break
		if Global.game_quit:
			break
		screen.fill(Setting.Environment.BACKGROUND_COLOR)
		pressed = pygame.key.get_pressed()
		tank.check_actions(pressed)
		Global.update()
		Global.draw(screen)
		pygame.display.flip()
		pygame.time.wait(Setting.Window.MSPF)
	pygame.display.quit()
