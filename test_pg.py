import pygame
import constants
import usefull_functions


resolution = constants.RESOLUTIONS[1]
# rects = calc_surface_parts_rects()
pygame.init()
FPS = 50
clock = pygame.time.Clock()
running = True
screen = pygame.display.set_mode(resolution.xy.xy)
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            break
    screen.fill('black')
    image = pygame.Surface((1, 32))
    thickness_rect = pygame.Rect(0, )
    
    screen.blit(image, rect)
    pygame.display.flip()
    clock.tick(FPS)
    
pygame.quit()
