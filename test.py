import pygame
import time
from scripts.ingame import assets
from assets import Sound
pygame.init()
pygame.mixer.music.load(Sound.Heavy_Tank.CANNON_EXPLOSION)
pygame.mixer.music.stop()
pygame.mixer.music.set_volume(0.05)
time.sleep(2)
# pygame.init()
# print(pygame.mixer.get_num_channels())
# sound= pygame.mixer.Sound("lost_disadv.mp3")
# sound.set_volume(0.2)
# sound.play()
# time.sleep (5)
# sound2.fadeout(2000)
# time.sleep(5)