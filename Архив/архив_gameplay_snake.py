import pygame
import constants
import random
import usefull_functions


# GamePlay
    # GamePlaySurface
        # ScoreInterface
        # Field
            # Food
            # Snake (Group)
                # SnakeHead(Sprite)
                # SnakeCell(Group)
                    # CellLine(Sprite)


# Snake:
    # shake_head: SnakeHead(head)
    # snake_body_cells: []
    # snake_tail: ???
class Snake(pygame.sprite.Group):
    def __init__(self,
                 field,
                 body={},
                 head={},
                 tail={}):
        super().__init__()
        self.field = field
        self.direction = random.choice(constants.DIRS_NAMES)
        # Инициализация параметров
        # body_parameters.keys:
            # 'snake_length_inFCcs'
            # 'line_height'
            # 'line_indent'
            # 'colour'
        self.body_parameters = self.init_body_parameters(body)
        self.snake_head = SnakeHead(self, head)
        self.line_images_by_direction = self.get_line_images_by_direction()
        # Части Змеи
        #test< self.snake_body_cells = [] >test
        
        self.snake_tail = None
        # Генерация изображения Змеи
        #test< self.create_snake() >test
        self.draw(self.field)

    # BODY_PARAMETERS
    def init_body_parameters(self, body):
        body_parameters = {}
        body_parameters['snake_length_inFCcs'] = body.get(
            'snake_length_inFCcs', constants.SNAKE_START_LENGTH_IN_CELLS)
        line_height, line_indent = self.get_line_height_and_indent(body.get(
            'line_height_percent',
            constants.SNAKE_CELL_PATTERN_PERCENT_OF_CELL_LENGTH))
        body_parameters['line_height'] = line_height
        body_parameters['line_indent'] = line_indent
        body_parameters['colour'] = body.get(
            'colour', constants.SNAKE_BODY_COLOUR)
        return body_parameters

    # body_parameters['line_height', 'line_indent']
    def get_line_height_and_indent(self, line_height_percent):
        line_height = self.field.cell_length * line_height_percent // 100
        if (self.field.cell_length - line_height) % 2 == 1:
            line_height += 1
        line_indent_height = (self.field.cell_length - line_height) // 2
        return line_height, line_indent_height

    def get_line_images_by_direction(self):
        line_surface_vertical = pygame.Surface((1, self.field.cell_length))
        pygame.draw.line(
            line_surface_vertical, self.body_parameters['colour'],
            (0, self.body_parameters['line_indent']),
            (0, self.body_parameters['line_indent'] +
             self.body_parameters['line_height'] - 1))
        line_surface_horizontal = pygame.Surface((self.field.cell_length, 1))
        pygame.draw.line(
            line_surface_horizontal, self.body_parameters['colour'],
            (self.body_parameters['line_indent'], 0),
            (self.body_parameters['line_indent'] +
             self.body_parameters['line_height'] - 1, 0))
        line_images_by_direction = {constants.LEFT: line_surface_vertical,
                                    constants.RIGHT: line_surface_vertical,
                                    constants.UP: line_surface_horizontal,
                                    constants.DOWN: line_surface_horizontal}
        return line_images_by_direction
    
    # СОЗДАНИЕ ТЕЛА ЗМЕИ
    def create_snake(self):
        for cell_i_from_head in range(self.body_parameters
                                      ['snake_length_inFCcs']):
            self.snake_body_cells.append(SnakeCell(self, cell_i_from_head))
    

class SnakeHead(pygame.sprite.Sprite):
    # head_parameters.keys:
        # 'head_coords_inFCcs'
        # 'form' = {'circle', 'image'}
        # 'fill' = {'colour', 'image'}
        # 'filename' (if 'form' == 'fill' == 'image')
        # 'fill_colour' (if 'fill' == 'colour')
    def __init__(self, snake, head_parameters={}):
        super().__init__()
        self.snake = snake
        self.snake.add(self)
        self.direction = self.snake.direction
        self.parameters = head_parameters
        self.head_coords_inFCcs = self.parameters.get(
            'head_coords_inFCcs', self.get_head_coords_inFCcs())
        self.head_coords_inFPcs = self.get_head_coords_inFPcs()
        self.image = self.get_image()
        self.rect = self.get_rect()
    
    # COORDS
    def get_head_coords_inFCcs(self):
        head_coords_ranges_inFCcs = self.get_head_coords_ranges_inFCcs()
        x_range, y_range = zip(*head_coords_ranges_inFCcs)
        head_x_inFCcs = random.randint(*x_range)
        head_y_inFCcs = random.randint(*y_range)
        return (head_x_inFCcs, head_y_inFCcs)
    
    # Сдвинуть границы на 4, чтобы у Игрока была возможность манёвра
    def get_head_coords_ranges_inFCcs(self):
        snake_length_inFCcs = self.snake.body_parameters['snake_length_inFCcs']
        field_size_inFCcs = (self.snake.field.game_play_surface.
                             interface_parts_sizes['field_size']['inFCcs'])
        field_coords_ranges = [(0, 0), usefull_functions.point_sub(
            field_size_inFCcs, operand=1)]
        dir_points = constants.DIRS_NAMES_TO_POINTS[self.direction]
        factors = usefull_functions.dif_points(*reversed(dir_points))
        shift = usefull_functions.point_multiply(
            factors, operand=snake_length_inFCcs - 1)
        if self.direction in ('right', 'down'):
            cell_coords_1, cell_coords_2 = usefull_functions.sum_points(
                field_coords_ranges[0], shift), field_coords_ranges[1]
        else:
            cell_coords_1, cell_coords_2 = (
                field_coords_ranges[0], usefull_functions.sum_points(
                    field_coords_ranges[1], shift))
        cell_coords_1 = usefull_functions.point_add(cell_coords_1, operand=4)
        cell_coords_2 = usefull_functions.point_add(cell_coords_2, operand=-4)
        return (cell_coords_1, cell_coords_2)
    
    def get_head_coords_inFPcs(self):
        head_coords_inFPcs = usefull_functions.point_multiply(
            self.head_coords_inFCcs, operand=self.snake.field.cell_length)
        factors = usefull_functions.dif_points(*reversed(
            constants.DIRS_NAMES_TO_POINTS[self.direction]))
        factors = usefull_functions.point_multiply(
            factors, operand=self.snake.field.cell_length // 2)
        head_coords_inFPcs = usefull_functions.sum_points(
            head_coords_inFPcs, factors)
        return head_coords_inFPcs
        
    # IMAGE
    def get_image(self):
        form = self.parameters.get('form', 'circle')
        fill = self.parameters.get('fill', 'colour')
        if form == 'circle' and fill == 'colour':
            fill_colour = self.parameters.get('fill_colour', 'red')
            image = usefull_functions.get_circle_image(
                fill_colour, self.snake.field.cell_length)
        usefull_functions.set_colorkey(image)
        return image

    def get_rect(self):
        rect = self.image.get_rect()
        rect.x, rect.y = self.head_coords_inFPcs
        return rect    

        
class SnakeCell(pygame.sprite.Group):
    def __init__(self, snake, cell_i_from_head):
        super().__init__()
        self.snake = snake
        self.cell_i_from_head = cell_i_from_head
        self.cell_length = self.snake.field.cell_length
        for line_i_from_cell_start in range(self.cell_length):
            self.add(CellLine(self, line_i_from_cell_start))
        # ЗДЕСЬ 20.03.2024


class CellLine(pygame.sprite.Sprite):
    def __init__(self, snake_cell, line_i_from_cell_start):
        super().__init__()
        self.snake_cell = snake_cell
        self.line_i_from_cell_start = line_i_from_cell_start
        self.direction = self.snake_cell.snake.direction
        self.image = self.snake_cell.snake.line_images_by_direction[
            self.direction]
        self.rect = self.get_rect_()

    def get_rect_(self):
        rect = self.image.get_rect()
        
        # self.snake_cell.snake.snake_head.head_coords_inFPcs
        # direction_factor = usefull_functions.dif_points(*reversed(
        #     constants.DIRS_NAMES_TO_POINTS[self.direction]))
        # position_from_head = self
        # direction_factor = usefull_functions.point_multiply(
        #     direction_factor, operand=)
        # rect.x = self.snake_cell.snake.he
        # self.snake_cell.cell_i_from_head