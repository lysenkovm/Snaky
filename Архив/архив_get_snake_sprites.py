import pygame
import constants
import math
from pprint import pprint


FPS = 60  # comment!
RESOLUTION = (1024, 768)    # comment!
CELL_SIZE = SECTOR_LENGTH = 64  # comment!
SECTOR_POINTS = {'left': (0, 0), 'right': (0, 0)}   # comment!
DIRECTIONS_OPPOSITE = {'left': 'right', 'right': 'left'}    # comment!
ROTATION_FACTORS = {'left': 1, 'right': -1}


def set_colorkey(surface, colorkey=None):
    if colorkey is None:
        colorkey = surface.get_at((0, 0))
    surface.set_colorkey(colorkey)

# 
def get_sprites(path):
    image = pygame.image.load(path)
    sprites = []
    for sprite_i in range(5):
        row = []
        for sprite_j in range(4):
            row.append(image.subsurface(sprite_i * SECTOR_LENGTH,
                                        sprite_j * SECTOR_LENGTH,
                                        SECTOR_LENGTH, SECTOR_LENGTH))
        sprites.append(row)
    return sprites
    

def get_sectors_up_left(sprite):
    
    def multiply_point(point, multiplier):
        return (point[0] * (multiplier - 1), point[1] * (multiplier - 1))
    
    def create_sector(points, sprite):
        sector_surface = sprite.copy()
        pygame.draw.polygon(sector_surface, 'red', points)
        set_colorkey(sector_surface, 'red')
        return sector_surface
    
    sectors_points = [((0, 1), (0, 0), (1, 0), (1, val / (SECTOR_LENGTH // 2)), (0, 1))
                      for val in range(SECTOR_LENGTH // 2 - 1, -1, -1)]
    sectors_points += [((0, 1), (0, 0), (val / (SECTOR_LENGTH // 2), 0), (0, 1))
                       for val in range(SECTOR_LENGTH // 2 - 1, -1, -1)]
    sectors_points = [tuple(multiply_point(point, SECTOR_LENGTH)
                            for point in points)
                      for points in sectors_points]
    print(len(sectors_points))
    sprite_sectors = []
    for sector_points in sectors_points:
        sprite_sectors.append(create_sector(sector_points, sprite))
    return sprite_sectors



if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode(RESOLUTION)
    running = True
    clock = pygame.time.Clock()
    sprites_path = r'/run/media/lysvm/E404923604920C24/Documents and Settings/lysvm/PythonApps/PyGame/Змейка/images/snake-graphics.png'
    sprites = get_sprites(sprites_path)
    
    
    sprite = sprites[2][0]
    sectors = get_sectors_up_left(sprite)
    sector_i = 0

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
        screen.fill('white')
        screen.blit(sectors[sector_i], (0 * SECTOR_LENGTH, 0 * SECTOR_LENGTH))
        if sector_i < len(sectors) - 1:
            sector_i += 1
        else:
            sector_i = 0
            
        
        
        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()
    