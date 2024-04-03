import pygame
import operator
from functools import partial
import constants


# Операция между координатами 2-х точек
def points_operation(point1, point2, operation):
    return tuple(operation(*coord_values) for coord_values 
                 in zip(point1, point2))


sum_points = partial(points_operation, operation=operator.add)
dif_points = partial(points_operation, operation=operator.sub)


# Операция над координатами точки
def point_operation(point,
                           operation,   # add: +, sub: -, mul: *,
                                        # truediv: /, mod: %, floordiv: //
                           operand,
                           coords_indices=(0, 1)):
    return tuple(operation(point[coord_i], operand)
                 if coord_i in coords_indices else point[coord_i]
                 for coord_i in range(2))


point_floor_div = partial(point_operation, operation=operator.floordiv)
point_multiply = partial(point_operation, operation=operator.mul)
point_sub = partial(point_operation, operation=operator.sub)
point_add = partial(point_operation, operation=operator.add)


def factorize_point(point, factor, decrement=0):
    return (point[0] * (factor - decrement),
            point[1] * (factor - decrement))


factors_to_coords = partial(factorize_point, decrement=1)


# DRAWING
def set_colorkey(surface, colorkey=None):
    if colorkey is None:
        colorkey = surface.get_at((0, 0))
    surface.set_colorkey(colorkey)


def get_circle_image(colour, cell_length):
    circle_image = pygame.Surface((cell_length, cell_length))
    radius = cell_length // 2
    center_point = (radius + bool(cell_length % 2), ) * 2
    pygame.draw.circle(circle_image, colour, center_point, radius)
    return circle_image


def get_factors(shift, direction):
    # Для положительного движения - положительные факторы
    factors = dif_points(*reversed(constants.DIRS_NAMES_TO_POINTS[direction]))
    factors = point_multiply(factors, operand=shift)
    return factors


def point_plus_factors(point, shift, direction):
    factors = get_factors(shift, direction)
    return sum_points(point, factors)


# COORDS
def calc_FCcs_from_FPcs(coords_inFPcs, cell_length):
    return point_floor_div(coords_inFPcs, operand=cell_length)


def calc_rect_xy_from_FCcs(coords_inFCcs, cell_length):
    return point_multiply(coords_inFCcs, operand=cell_length)


def invert_colour(colour):
    if isinstance(colour, (tuple, str)):
        pygame_colour = pygame.color.Color(colour)
    else:
        pygame_colour = colour
    for i in range(3):
        pygame_colour[i] = 255 - pygame_colour[i]
    return pygame_colour
