import pygame
import usefull_functions
import constants


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


# Разрешение в ячейках
class Resolution:
    def __init__(self, size_inFPcs, cell_length):
        self._xy_inFPcs = self._x_inFPcs, self._y_inFPcs = size_inFPcs
        self._cell_length = cell_length
        self._size_inFCcs = self._xy_inFCcs = \
            self._x_inFCcs, self._y_inFCcs = self.inFCcs

    @property
    def cell_length(self):
        return self._cell_length

    # Field POINTS Coords
    @property
    def inFPcs(self):
        return self._xy_inFPcs
    
    @property
    def x_inFPcs(self):
        return self._x_inFPcs

    @property
    def y_inFPcs(self):
        return self._y_inFPcs

    # Field CELLS Coords
    @property
    def inFCcs(self):
        return usefull_functions.calc_FCcs_from_FPcs(
            self._xy_inFPcs, self._cell_length)
    
    @property
    def x_inFCcs(self):
        return self._x_inFCcs

    @property
    def y_inFCcs(self):
        return self._y_inFCcs

    # Common methods
    def __str__(self):
        return f'Resolution(FPcs{self.inFPcs} == FCcs{self.inFCcs})'
    

# Получить угловые точки
class FCcs:
    def __init__(self, xy_inFCcs, resolution):
        self.xy = self.x, self.y = xy_inFCcs
        self.resolution = resolution
        

# Получить координаты ячейки
# Создать ячейку в начиная с этой точки
# Получить угловую точку, если текущая - определённый угол        
class FPcs:
    def __init__(self, xy, resolution):
        self.xy = self.x, self.y = xy
        self.resolution = resolution


res = Resolution(constants.RESOLUTIONS[0],
                 constants.RESOLUTIONS_SIDE_LENGTH[constants.RESOLUTIONS[0]][0])
print(res.y_inFPcs)