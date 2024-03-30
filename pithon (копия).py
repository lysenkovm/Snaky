import pygame
import random
from itertools import product
from functools import partial
import operator
import constants


# Получить значение именованного параметра или значение по-умолчанию
def get_kwarg(kwargs, kwarg_name, else_arg=False):
    if else_arg:
        return kwargs.get(kwarg_name, default=else_arg)
    else:    
        return kwargs[kwarg_name]


# преобразовать иерархию типов list и tuple в иерархию одного из типов
def to_single_type_hierarchy(seq, to_type):
    return to_type(map(lambda x: to_single_type_hierarchy(x, to_type) 
                       if isinstance(x, (list, tuple)) else x, seq))


make_changeable_hierarchy = partial(to_single_type_hierarchy, to_type=list)
make_unchangeable_hierarchy = partial(to_single_type_hierarchy, to_type=tuple)


# изменить направление на обратное - направление роста змеи от головы
def growth_dir(dir_):
    return tuple(reversed(dir_))


def get_coord_n_factor(dir_: tuple) -> tuple:     # ((0, 0), (1, 0))
    coords_ns_factors = tuple(enumerate(dif_points(*reversed(dir_))))    # ((0, 1), (1, 0)) - ((x, 1), (y, 0))
    return tuple(filter(lambda x: x[1], coords_ns_factors))[0]           # вернуть только картеж, который содержит
                                                                          # указание на передвижение: (x, 1)


# Обрезка квадрата на 'val' по 'dir'
# field_rect_LU_RD_inFCcs, snake_dir, snake_length_in_cells - 1
def cut_rect_points(rect: list, dir_: tuple, value: int):
    dir_factorized = tuple(factorize_point(point, value) for point in dir_)
    start_point = sum_points(rect[0], dir_factorized[1])
    end_point = dif_points(rect[1], dir_factorized[0])
    return make_unchangeable_hierarchy((start_point, end_point))


# rect[point_n] - [0, 0], coord_n - 0/1, factor - 0/1, val - 9 (длина змеи - 1)
# (128, 176), 0, -1, 9
def move_coords(point_coords, coord_n, factor, val):
    point_coords = make_changeable_hierarchy(point_coords)
    point_coords[coord_n] += factor * val     # сдвиг на val ячеек координаты с номером coord_n
    return make_unchangeable_hierarchy(point_coords)


# Преобразовать точечные координаты в квадратные с округлением
def points_to_square(coord, sq_size):
    return coord // sq_size, coord % sq_size  # Номер квадрата и !номер! линии


                        #### CLASSES ####
# создано 17.02.24 в 10:55
class Field:
    def __init__(self, game_play, resolution, cell_length):
        self.game_play = game_play
        self.resolution = resolution
        self.cell_length = cell_length      # 16
        self.size_in_cells = (self.size[0] // self.cell_length,     # (1024 // 16, 768 // 16) -> (64, 48)
                              self.size[1] // self.cell_length)
        # self.rect_LU_RD_inFCcs = ((0, 0), (self.size_in_cells[0] - 1,   # ((0, 0), (63, 47))
        #                                    self.size_in_cells[1] - 1))


class GamePlay:
    def __init__(self, game_app):
        self.game_app = game_app
        self.field = Field(self, self.game_app.resolution,
                           self.game_app.cell_size)
        # Определить направление и длину Змеи в ячейках
        # snake_dir = DIRS_NAMES_TO_POINTS[random.choice(DIRS_NAMES)]  # Случайное направление Змеи
        snake_dir = DIRS_NAMES_TO_POINTS[RIGHT]     # Test - uncomment prev.
        snake_length_in_cells = START_SNAKE_LENGTH_IN_CELLS  # Длина в ячейках
        # Создать и перенести координаты 2-х ячеек - границ игрового поля
        # для выбора головного квадрата
        field_rect_cut = cut_rect_points(
            self.field.rect_LU_RD_inFCcs, snake_dir,
            snake_length_in_cells - 1)
        # Выбрать квадрат (координаты) Головн.Яч.
        # (x1, y1), (x2, y2) = field_rect_cut
        # head_square = (random.randint(x1, x2),
        #                random.randint(y1, y2))
        head_cell_xy_coords_inCellsField = (10, 4)  # Test - uncomment 2 prev.instr.
        self.snake = Snake(self, snake_dir, snake_length_in_cells,
                           head_cell_xy_coords_inCellsField)
        # Создать группу спрайтов Яблок
        # self.apples = pygame.sprite.Group()

    def check_snake_dir_changed(self, event):
        if set(self.snake.dir_) != set(KEYS_DIRS[event.key]):      # <clas 'Game'>
            return KEYS_DIRS[event.key]

    def gen_apple(self):
        pass

# Snake(self: Game, snake_dir, snake_length_in_cells, head_square)
class Snake(pygame.sprite.Group):
    def __init__(self, game: Game,
                 snake_dir,
                 snake_length_in_cells,
                 head_cell_xy_coords_inCellsField):
        super().__init__()
        self.color = "black"
        self.head_color = "red"

        self.game = game
        self.field = self.game.field
        self.dir_ = snake_dir
        self.lines = []

        # Генерация Линий в Ячейках
        for cell_n in range(snake_length_in_cells):  # Для каждого номера ячейки в Змее
            coord_n, factor = get_coord_n_factor(growth_dir(self.dir_))
            cell_coords = move_coords(head_cell_xy_coords_inCellsField,  # Определить ячейку генерации
                                      coord_n, factor, cell_n)            # сдвигом на № ячейки от головы
            for line_n in range(self.game.field.cell_length):  # (0-15) Для кажд. номера линии (в ячейке) (0,1,...,15)
                line = Line(self, self.game.field.cell_length, cell_coords, self.dir_, line_n)
                # Поместить в 'self.lines' в начало (стек) Линию с направлением,
                # координатами ячейки, номером линии
                self.lines.append(line)

        # print(self.dir_, head_coords_sq)
        # for line in self.lines:
        #     print(line.square, line.line_n, line.rect)
        # print(self.lines[0].line_n)

    def move_forward(self):
        tail_line = self.lines.pop(-1)
        square, line_n = self.lines[0].cell_coords, self.lines[0].line_n
        dir_ = self.lines[0].dir_
        tail_line.update_args(square=square, line_n=line_n - 1, dir_=dir_)
        self.lines.insert(0, tail_line)

    def change_head_dir(self, new_dir):
        self.dir_ = new_dir
        for line in self.lines[: self.game.field.cell_length]:
            line.update_args(dir_=self.dir_)

    def update_lines(self):
        for line_i in range(len(self.lines)):
            if line_i < self.game.field.cell_length:
                self.lines[line_i].update_args(color=self.head_color)
            else:
                self.lines[line_i].update_args(color=self.color)


class Line(pygame.sprite.Sprite):
    def __init__(self, snake, cell_length, cell_coords, dir_, line_n):
        super().__init__(snake)
        self.snake = snake
        self.length = self.snake.field.cell_length
        self.cell_coords = cell_coords
        self.dir_ = dir_
        self.line_n = line_n
        self.color = self.snake.color
        # add attributes:
         # self.rect
         # self.image
        self.update_rect_image()

    # inFPcs - inFieldPoints_coords - точечные координаты внутри поля
    # inFCcs - inFieldCells_coords - ячеичные координаты внутри поля
    # inCPcs - inCellPoints_coords - точечные координаты внутри ячейки
    def gen_rect(self):
        # координаты первой точки ячейки: (128, 176)
        first_point_of_cell_coords_inFPcs = factorize_point(self.cell_coords,
                                                            self.length)
        # координаты первой точки линии в точечных координатах ячейки:
        # right - ((1, 0), (1, 1))[0], length=16 -> (15, 0)
        first_point_of_line_inCPcs = factors_to_coords(DIRS_POINTS_SIDES[self.dir_][0],
                                                       self.length)
        # номер изменяемой координаты линии (по положению в ячейке) и фактор изменения:
        # (0/1, 1/-1): (0, -1)
        coord_n, factor = get_coord_n_factor(growth_dir(self.dir_))
        ## Сдвинуть координаты первой точки линии на номер линии (line_n) в ячейке
        ## Например: (134, 176)
        first_point_of_line_inCPcs = move_coords(first_point_of_line_inCPcs,
                                                 coord_n, factor, self.line_n)
        first_point_of_line_inFPcs = sum_points(first_point_of_cell_coords_inFPcs,
                                                first_point_of_line_inCPcs)
        width, height = (1, self.length) if coord_n == 0 else (self.length, 1)
        return pygame.Rect(*first_point_of_line_inFPcs, width, height)

    def update_rect_image(self):
        self.rect = self.gen_rect()
        self.image = pygame.Surface(self.rect.size)
        self.image.fill(self.color)

    def update_args(self, **kwargs):
        if "dir_" in kwargs:
            dir_ = get_kwarg(kwargs, "dir_")
            self.dir_ = dir_

        if "square" in kwargs:
            square = get_kwarg(kwargs, "square")
            self.cell_coords = square

        if "line_n" in kwargs:
            line_n = get_kwarg(kwargs, "line_n")
            self.line_n = line_n
            if self.line_n < 0:
                self.line_n %= self.length
                coord_n, factor = get_coord_n_factor(self.dir_)
                self.cell_coords = move_coords(self.cell_coords, coord_n, factor, 1)

        if "color" in kwargs:
            color = get_kwarg(kwargs, "color")
            self.color = color

        self.update_rect_image()  # => global code


class Apple(pygame.sprite.Sprite):
    def __init__(self, apples, square, length):
        super().__init__(apples)
        self.square = square
        self.length = length
        self.update_rect_image()

    def gen_rect(self):
        return (
            (self.square[0] * self.length, self.square[1] * self.length),
            ((self.square[0] + 1) * self.length, (self.square[1] + 1) * self.length),
        )

    def gen_image(self):
        x = self.rect[1][0] - self.rect[0][0]
        y = self.rect[1][1] - self.rect[0][1]
        x += 1 if not x else 0
        y += 1 if not y else 0
        return x, y

    def update_rect_image(self):
        self.rect = self.gen_rect()
        self.image = self.gen_image()

