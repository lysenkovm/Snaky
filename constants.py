import pygame
import usefull_functions
from pathlib import Path


# FOLDERS
IMAGES_FOLDER = Path(r'./images/')
FONTS_FOLDER = Path(r'./fonts/')
SOUNDS_FOLDER = Path(r'./sounds/')
FOOD_FOLDER = Path(r'./images/Food/')



# GameApp
FPS = 50
MENU_BACKGROUND_IMAGE_PATH = IMAGES_FOLDER / r'menu_background.jpg'

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


# IMAGE_BUTTON
# surface
BUTTON_SURFACE_PARAMETERS = {'size': (400, 60),
                             'thickness_percent': 10,
                             'form': 'oval',
                             'image_filepath': None}
# colours
BUTTON_COLOURS = {'fill': 'blue',
                  'border': 'red',
                  'thickness': (10, 10, 10)}
# font
BUTTON_FONT_PARAMETERS = {'filepath': FONTS_FOLDER / r'SerpensRegular-7MGE.ttf',
                          'size': 40,
                          'colour': 'yellow'}

# focus
BUTTON_FOCUS_PARAMETERS = {'border': 10,
                           'indent': BUTTON_SURFACE_PARAMETERS['size'][1] // 2}
# sounds
BUTTON_SOUNDS_PARAMETERS = {'click_filepath': SOUNDS_FOLDER /
                           r'mixkit-arcade-game-jump-coin-216.wav',
                           'motion_filepath': SOUNDS_FOLDER /
                           r'mixkit-camera-shutter-click-1133.wav'}

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



# EVENTS
FOOD_PIECE_EATEN = pygame.USEREVENT + 1


# Точки по возрастанию, убыванию
# Противоположная ось
class Axis:
    def __init__(self, axis):
        if isinstance(axis, (tuple, list, set)):
            self._points = set(axis)
            self._name = DIRS_NAMES_AXES[
                DIRS_POINTS_TO_NAMES[tuple(self._points)]]
        elif isinstance(axis, str):
            self._name = axis
            self._points = set(DIRS_NAMES_TO_POINTS[AXES_DIRS_NAMES[axis][0]])

    @property
    def name(self):
        return self._name

    @property
    def points(self):
        return self._points
    
    @property
    def opposite(self):
        return self.__class__(AXES_OPPOSITES[self.name])
    
    @property
    def direction_increase(self):
        return Direction(sorted(self.points))
    
    @property
    def direction_decrease(self):
        return Direction(sorted(self.points, reverse=True))
    
    @property
    def directions(self):
        return AXES_DIRS_NAMES

    def __str__(self):
        return f'Axis({self.name.upper()} == {self.points.__repr__()})'


class Direction:
    def __init__(self, direction):
        if isinstance(direction, (tuple, list)):
            self._points = direction
            self._name = DIRS_POINTS_TO_NAMES[tuple(self.points)]
        elif isinstance(direction, str):
            self._name = direction
            self._points = DIRS_NAMES_TO_POINTS[self.name]
        self._axis = Axis(self._points)

    @property
    def points(self):
        return self._points

    @property
    def name(self):
        return self._name

    @property
    def opposite(self):
        return self.__class__(tuple(reversed(self.points)))

    @property
    def axis(self):
        return self._axis

    def __str__(self):
        return f'Direction({self.name.upper()} == {self.points})'


class Resolutions:

    RESOLUTIONS_CELL_LENGTH = {(1024, 768): (16, 32), 
                               (1280, 800): (16, 20, 32, 40), 
                               (1280, 1024): (16, 32), 
                               (1440, 900): (15, 18, 20, 30, 36), 
                               (1600, 900): (20, 25), 
                               (1680, 1050): (15, 21, 30, 35), 
                               (1920, 1080): (15, 20, 24, 30, 40)}

    def __init__(self):
        self.resolutions = sorted(self.RESOLUTIONS_CELL_LENGTH.keys())

    def __len__(self):
        return len(self.resolutions)

    def __call__(self, index):
        return Resolution(
            *sorted(self.RESOLUTIONS_CELL_LENGTH.items())[index], index)

    def __getitem__(self, index):
        return self.__call__(index)


class Resolution:
    
    def __init__(self, resolution, cell_lengths, index):
        self._xy = self._x, self._y = resolution
        self.cell_lengths = cell_lengths
        self.index = index

    # Field POINTS Coords
    @property
    def xy(self):
        return self._xy
    
    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y
    
    def cell_length(self, key):
        return self.cell_lengths[key]

    # Common methods
    def __str__(self):
        return f'{self.x} x {self.y}'
    
    def __repr__(self):
        return f'Resolution{self.xy}'
    

# Получить угловые точки
class FCcs:
    def __init__(self, xy_inFCcs, resolution):
        self.xy = self.x, self.y = xy_inFCcs
        self.resolution = resolution
        

# Получить координаты ячейки
# Создать ячейку в начиная с этой точки
# Получить угловую точку, если текущая - определённый угол        
class FPcs:
    def __init__(self, *xy):
        if len(xy) == 1:
            self._x, self._y = xy[0]
        elif len(xy) == 2:
            self._x, self._y = xy
        
    def __sub__(self, other):
        if isinstance(other, self.__class__):
            return self.__class__(self.x - other.x, self.y - other.y)
        elif isinstance(other, int):
            return self.__class__(self.x - other, self.y - other)
        
    def __isub__(self, other):
        return self.__sub__(other)
    
    def __add__(self, other):
        if isinstance(other, self.__class__):
            return self.__class__(self.x + other.x, self.y + other.y)
        elif isinstance(other, int):
            return self.__class__(self.x + other, self.y + other)
    
    def __iadd__(self, other):
        return self.__add__(other)
    
    def __mul__(self, value):
        return self.__class__(self.x * value, self.y * value)
    
    def __imul__(self, value):
        return self.__mul__(value)
    
    def __floordiv__(self, value):
        return self.__class__(self.x // value, self.y // value)
    
    def __ifloordiv__(self, value):
        return self.__floordiv__(value)
    
    def __truediv__(self, value):
        return self.__floordiv__(value)

    def __itruediv__(self, value):
        return self.__truediv__(value)

    def __str__(self):
        return f'FPcs{self.xy}'
    
    @property
    def x(self):
        return self._x
    
    @x.setter
    def x(self, new_x):
        self._x = new_x
    
    @property
    def y(self):
        return self._y
    
    @y.setter
    def y(self, new_y):
        self._y = new_y
    
    @property
    def xy(self):
        return (self.x, self.y)
        

RESOLUTIONS = Resolutions()