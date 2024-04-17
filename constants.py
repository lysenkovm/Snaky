import pygame
import usefull_functions
from pathlib import Path
import random


# FOLDERS
IMAGES_FOLDER = Path(r'./images/')
FONTS_FOLDER = Path(r'./fonts/')
SOUNDS_FOLDER = Path(r'./sounds/')
FOOD_FOLDER = Path(r'./images/Food/')


# GameApp
FPS = 50
MENU_BACKGROUND_IMAGE_PATH = IMAGES_FOLDER / r'menu_background.jpg'

# COORDINATES
DIRS_NAMES = LEFT, RIGHT, UP, DOWN = ("left", "right", "up", "down")
AXES_NAMES = HORIZONTAL, VERTICAL = ('horizontal', 'vertical')
DIRS_SIDES = (((0, 0), (0, 1)),     # направления в сторону стен
              ((1, 0), (1, 1)),
              ((0, 0), (1, 0)),
              ((0, 1), (1, 1)))

# СЛОВАРИ НАПРАВЛЕНИЙ

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
BUTTON_FOCUS_PARAMETERS = {'focus_thickness': 10,
                           'focus_colour': 'red'}

# sounds
BUTTON_SOUNDS_PARAMETERS = {'click_filepath': SOUNDS_FOLDER /
                           r'mixkit-arcade-game-jump-coin-216.wav',
                           'motion_filepath': SOUNDS_FOLDER /
                           r'mixkit-camera-shutter-click-1133.wav'}

# MENU
BUTTONS_INDENT_PERCENT = 50

# GAMEPLAY
# Score interface
SCORE_PERCENT_OF_RESOLUTION = 20
SCORE_FILL_COLOUR = 'yellow'
# Field



# SNAKE
SNAKE_START_INDENT_FOR_MOVING = 3
# Head
SNAKE_HEAD_FILL_COLOUR = 'red'
# Body
BODY_PARAMETERS = {'length_inFCcs': 10,
                   'body_thickness_percent': 60,
                   'colour': 'orange'}
# Moving
SNAKE_SPEED_MIN = 30
SNAKE_MOVE_EVENT = pygame.USEREVENT + 1


# FOOD
FOOD_SPRITES_PARAMETERS = {'filepath': FOOD_FOLDER / 'food-drink-00.png',
                           'piece_length': 72}
FOOD_APPER_SECONDS = 4

# EVENTS
FOOD_PIECE_NEED_EVENT = pygame.USEREVENT + 2
FOOD_PIECE_EATEN_EVENT = pygame.USEREVENT + 3


# Получить координаты ячейки
# Создать ячейку в начиная с этой точки
# Получить угловую точку, если текущая - определённый угол        
class Point:
    def __init__(self, *xy):
        if len(xy) == 1:
            if isinstance(xy[0], Point):
                self._x, self._y = xy[0].xy
            else:
                self._x, self._y = xy[0]
        elif len(xy) == 2:
            self._x, self._y = xy
    
    def __sub__(self, other):
        if isinstance(other, self.__class__):
            return self.__class__(self.x - other.x, self.y - other.y)
        elif isinstance(other, (tuple, list)):
            return self.__class__(self.x - other[0], self.y - other[1])
        elif isinstance(other, int):
            return self.__class__(self.x - other, self.y - other)
        
    def __isub__(self, other):
        return self.__sub__(other)
    
    def __add__(self, other):
        if isinstance(other, self.__class__):
            return self.__class__(self.x + other.x, self.y + other.y)
        elif isinstance(other, (tuple, list)):
            return self.__class__(self.x + other[0], self.y + other[1])
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
        return f'Point{self.xy}'
    
    def __repr__(self):
        return self.__str__()
    
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
        return (self._x, self._y)
    
    @property
    def factors(self):
        return self.__class__(
            1 if self._x > 0 else 0 if self._x == 0 else -1,
            1 if self._y > 0 else 0 if self._y == 0 else -1)
    
    def copy(self):
        return self.__class__(self.xy)
    
    def to_FCcs(self, cell_length, direction=LEFT):
        direction = Direction(direction)
        if direction.is_decreasing():
            return self // cell_length
        else:
            return (self + direction.factors * (cell_length - 1)) // cell_length
    
    def to_FPcs(self, cell_length):
        return self * cell_length


# Возможно создане по:
    # индексу/имени Оси
    # tuple/list/set of xy/Point
class Axis:
    
    # Словарие - только для внутреннего использования
    NAMES_INDICES = {HORIZONTAL: 0, VERTICAL: 1}
    INDICES_NAMES = usefull_functions.reverse_dict(NAMES_INDICES)
    DIRS_NAMES_AXES = {LEFT: HORIZONTAL,
                       RIGHT: HORIZONTAL,
                       UP: VERTICAL,
                       DOWN: VERTICAL}
    AXES_DIRS_NAMES = {HORIZONTAL: (LEFT, RIGHT),
                       VERTICAL: (UP, DOWN)}
    AXES_OPPOSITES = {HORIZONTAL: VERTICAL,
                      VERTICAL: HORIZONTAL}
    
    def __init__(self, axis_source):
        # Если задана коллекция Точек (координат)
        if isinstance(axis_source, (tuple, list, set)):
            self._name = self.INDICES_NAMES[self.calc_axis_index(axis_source)]
        # Если задано имя Оси или Направления
        elif isinstance(axis_source, str):
            if axis_source in AXES_NAMES:
                self._name = axis_source
            elif axis_source in DIRS_NAMES:
                self._name = self.DIRS_NAMES_AXES[axis_source]
        # Если задан индекс Оси
        elif isinstance(axis_source, int):
            self._name = self.INDICES_NAMES[axis_source]
        elif isinstance(axis_source, Direction):
            self._name = self.DIRS_NAMES_AXES[axis_source.name]
        self._points = {Point((0, 0)), Point((0, 1) if self.index else (1, 0))}

    def calc_axis_index(self, points):
        point1, point2 = [Point(xy) for xy in points]
        points_dif = point1 - point2
        for index in range(2):
            if points_dif.xy[index] != 0:
                return index

    @property
    def index(self):
        return self.NAMES_INDICES[self._name]

    @property
    def name(self):
        return self._name

    @property
    def points(self):
        return self._points
    
    @property
    def reverse(self):
        return self.__class__(self.AXES_OPPOSITES[self.name])
    
    @property
    def direction_increase(self):
        return Direction(sorted(self.points, key=lambda point: point.xy))
    
    @property
    def direction_decrease(self):
        return Direction(
            sorted(self.points, key=lambda point: point.xy, reverse=True))
    
    @property
    def directions(self):
        return {self.direction_increase, self.direction_decrease}
    
    @property
    def reverse(self):
        return self.__class__(self.AXES_OPPOSITES[self.name])

    def __str__(self):
        return f'Axis({self.name.upper()} == {self.points})'


# Используется в Axis
# Возможно создание по
    # tuple/list of xy/Point
    # str
class Direction:
    DIRS_NAMES_OPPOSITES = {LEFT: RIGHT,    # словарь противоположных направлений по именам
                            RIGHT: LEFT,
                            UP: DOWN,
                            DOWN: UP}
    DIRS_POINTS = (((1, 0), (0, 0)),
                   ((0, 0), (1, 0)),
                   ((0, 1), (0, 0)),
                   ((0, 0), (0, 1)))
    DIRS_NAMES_TO_POINTS = dict(zip(DIRS_NAMES, DIRS_POINTS))   # словарь ИМЯ:ТОЧКА-ТОЧКА
    DIRS_POINTS_TO_NAMES = dict(zip(DIRS_POINTS, DIRS_NAMES))   # словарь ТОЧКА-ТОЧКА:ИМЯ
    DIRS_POINTS_TO_FACTORS = {(xy1, xy2): (xy2[0] - xy1[0], xy2[1] - xy1[1])
                              for xy1, xy2 in DIRS_POINTS}
    DIRS_FACTORS_TO_POINTS = usefull_functions.reverse_dict(DIRS_POINTS_TO_FACTORS)
    
    # direction_source - list or tuple of 2 int or Point
    def __init__(self, direction_source):
        if isinstance(direction_source, (tuple, list)):
            self._name = self.DIRS_POINTS_TO_NAMES[self.DIRS_FACTORS_TO_POINTS[
                (Point(direction_source[1]) - Point(direction_source[0])).factors.xy]]
        elif isinstance(direction_source, str):
            self._name = direction_source
        elif isinstance(direction_source, Direction):
            self._name = direction_source.name
        elif direction_source in KEYS_DIRS:
            self._name = KEYS_DIRS[direction_source]
        self._points = tuple(Point(xy) for xy in self.DIRS_NAMES_TO_POINTS[self._name])
        self._axis = Axis(self._points)
    
    @property
    def points(self):
        return self._points

    @property
    def name(self):
        return self._name
    
    @property
    def key(self):
        return DIRS_KEYS[self._name]

    @property
    def reverse(self):
        return self.__class__(self.DIRS_NAMES_OPPOSITES[self._name])

    @property
    def axis(self):
        return self._axis
    
    @property
    def factors(self):
        return (self._points[1] - self._points[0])
    
    def __call__(self, index):
        return self._points[index]
    
    def __getitem__(self, index):
        return self.__call__(index)

    def __str__(self):
        return f'Direction({self.name.upper()} == {self.points})'
    
    def copy(self):
        return self.__class__(self._name)
    
    def is_increasing(self):
        point1, point2 = self._points
        if sum((point2 - point1).xy) > 0:
            return True
        return False
    
    def is_decreasing(self):
        return not self.is_increasing()


# Resolutions[i] == Resolutions(i) ->
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
        return Resolution(*sorted(self.RESOLUTIONS_CELL_LENGTH.items())[index],
                          index)

    def __getitem__(self, index):
        return self.__call__(index)


class Resolution:
    
    def __init__(self, wh, cell_lengths, index):
        self._x, self._y = wh
        self.cell_lengths = cell_lengths
        self.index = index  # индекс в списке разрешений

    # Field POINTS Coords
    @property
    def xy(self):
        return Point(self._x, self._y)
    
    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y
    
    # Common methods
    def __str__(self):
        return f'{self.x} x {self.y}'
    
    def __repr__(self):
        return f'Resolution{self.xy}'
        

RESOLUTIONS = Resolutions()


# Спрайт, который хранит свои элементы в атрибуте-группе
class Block(pygame.sprite.Sprite):
    def __init__(self, image, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.image = image
        self.rect = self.image.get_rect()
        self.group = pygame.sprite.Group()
        
    def draw(self):
        self.group.draw(self.image)
    
    def add(self, sprite):
        self.group.add(sprite)
    
    # Копирование Спрайта
    def copy(self):
        image = self.image.copy()
        rect = self.rect.copy()
        group = self.group.copy()
        block = self.__class__(image)
        block.rect = rect
        block.group = group
        return block
