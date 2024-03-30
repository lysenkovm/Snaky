import pygame


# GameApp
FPS = 50

RESOLUTIONS_SIDE_LENGTH = {(1024, 768): (16, 32), 
                           (1280, 800): (16, 20, 32, 40), 
                           (1280, 1024): (16, 32), 
                           (1440, 900): (15, 18, 20, 30, 36), 
                           (1600, 900): (20, 25), 
                           (1680, 1050): (15, 21, 30, 35), 
                           (1920, 1080): (15, 20, 24, 30, 40)}
RESOLUTIONS = sorted(RESOLUTIONS_SIDE_LENGTH.keys())

# НАПРАВЛЕНИЯ ДВИЖЕНИЯ: влево, вправо, вверх, вниз
## ЗАДАЧА: направления, оси и т.п. сделать объектами с аттрибутами: name, points и т.п.!!!

DIRS_NAMES = LEFT, RIGHT, UP, DOWN = ("left", "right", "up", "down")
AXES = HORIZONTAL, VERTICAL = ('horizontal', 'vertical')
DIRS_POINTS = (((1, 0), (0, 0)),    # направления от точки до точки
               ((0, 0), (1, 0)),
               ((0, 1), (0, 0)),
               ((0, 0), (0, 1)))
DIRS_SIDES = (((0, 0), (0, 1)),     # направления в сторону стен
              ((1, 0), (1, 1)),
              ((0, 0), (1, 0)),
              ((0, 1), (1, 1)))

# СЛОВАРИ НАПРАВЛЕНИЙ
DIRS_NAMES_OPPOSITES = {LEFT: RIGHT,    # словарь противоположных направлений по именам
                        RIGHT: LEFT,
                        UP: DOWN,
                        DOWN: UP}
DIRS_NAMES_AXES = {LEFT: HORIZONTAL,
                   RIGHT: HORIZONTAL,
                   UP: VERTICAL,
                   DOWN: VERTICAL}
AXES_DIRS_NAMES = {HORIZONTAL: (LEFT, RIGHT),
                   VERTICAL: (UP, DOWN)}
AXES_OPPOSITES = {HORIZONTAL: VERTICAL,
                  VERTICAL: HORIZONTAL}
DIRS_NAMES_TO_POINTS = dict(zip(DIRS_NAMES, DIRS_POINTS))   # словарь ИМЯ:ТОЧКА-ТОЧКА
DIRS_POINTS_TO_NAMES = dict(zip(DIRS_POINTS, DIRS_NAMES))   # словарь ТОЧКА-ТОЧКА:ИМЯ
DIRS_NAMES_TO_SIDES = dict(zip(DIRS_NAMES, DIRS_SIDES))     # словарь ИМЯ:СТОРОНА
DIRS_POINTS_SIDES = dict(zip(DIRS_POINTS, DIRS_SIDES))  # словарь ТОЧКА-ТОЧКА:СТОРОНА
DIRS_SIDES_POINTS = dict(zip(DIRS_SIDES, DIRS_POINTS))  # словарь СТОРОНА:ТОЧКА-ТОЧКА
# словарь ТОЧКА-ТОЧКА:СОБЫТИЕ-PYGAME
DIRS_KEYS = dict(zip(DIRS_NAMES, (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN)))
# словарь СОБЫТИЕ-PYGAME:ТОЧКА-ТОЧКА
KEYS_DIRS = dict(map(reversed, DIRS_KEYS.items()))
# словарь ИМЯ_НАПР:НОМЕР_КООРД



# GAMEPLAY
GAMEPLAY_SCORE_INTERFACE_PART_PERCENT = 25
GAMEPLAY_FIELD_PART_PERCENT = 100 - GAMEPLAY_SCORE_INTERFACE_PART_PERCENT
SCORE_TO_FIELD_PART = 4


# SNAKE
SNAKE_START_LENGTH_IN_CELLS = 10
SNAKE_CELL_PATTERN_PERCENT_OF_CELL_LENGTH = 60
SNAKE_BODY_COLOUR = 'orange'
SNAKE_SPEED_MIN = 50


# FOOD
FOOD_FOLDER = r'./images/Food/'


# EVENTS
FOOD_PEICE_EATEN = pygame.USEREVENT + 1



# class AXIS:
#     def __init__(self, ):
        

class Direction:
    def __init__(self, direction):
        if isinstance(direction, (tuple, list)):
            self._points = direction
            self._name = DIRS_POINTS_TO_NAMES[self.points]
        elif isinstance(direction, str):
            self._name = direction
            self._points = DIRS_NAMES_TO_POINTS[self.name]
        self._axis = DIRS_NAMES_AXES[self.name]
    
    @property
    def points(self):
        return self._points
    
    @property
    def name(self):
        return self._name
    
    @property
    def opposite(self):
        return Direction(tuple(reversed(self.points)))



# class FPcs:
#     def __init__(self, field, xy):
#         self.field = field
#         self.x, self.y = self.xy = tuple(xy)
    
#     def calc_resolution_last_coords(self, axes=(0, 1)):
#         return tuple(self.field.resolution[axis] - 1 for axis in axes)
    
#     def reverse(self, axes=(0, 1)):
#         reversed_coords = tuple( for self.calc_resolution_last_coords(axes))
