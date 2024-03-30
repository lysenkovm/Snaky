import pygame
import constants
import random
import usefull_functions


# GamePlay (Group)
    # ScoreInterface (Sprite)
    # Field (Sprite)
        # Food (Group)
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
                 snake={},
                 body={},
                 head={},
                 tail={}):
        super().__init__()
        self.field = field
        self.direction = random.choice(constants.DIRS_NAMES)
        # self.direction = constants.UP
        # Инициализация параметров
        self.speed = snake.get(
            'speed', constants.SNAKE_SPEED_MIN) // constants.FPS
        # body_parameters.keys:
            # 'snake_length_inFCcs'
            # 'visual_line_height'
            # 'line_indent'
            # 'colour'
        self.body_parameters = self.init_body_parameters(body)
        # Части Змеи
        self.line_images_by_direction = self.create_line_images_by_direction()
        self.snake_head = SnakeHead(self, head)
        self.snake_body_lines = []
        #test< self.snake_body_cells = []
        # self.snake_tail = None
        # Генерация изображения Змеи
        self.create_snake()
        #test>
        self.add(*self.snake_body_lines, self.snake_head)  # Потом добавить ячейки тела и хвост

    # BODY_PARAMETERS
    def init_body_parameters(self, body):
        body_parameters = {}
        body_parameters['snake_length_inFCcs'] = body.get(
            'snake_length_inFCcs', constants.SNAKE_START_LENGTH_IN_CELLS)
        visual_line_height, line_indent = self.calc_line_height_and_indent(
            body.get('line_height_percent',
                     constants.SNAKE_CELL_PATTERN_PERCENT_OF_CELL_LENGTH))
        body_parameters['visual_line_height'] = visual_line_height
        body_parameters['line_indent'] = line_indent
        body_parameters['colour'] = body.get(
            'colour', constants.SNAKE_BODY_COLOUR)
        return body_parameters

    # body_parameters['visual_line_height', 'line_indent']
    def calc_line_height_and_indent(self, line_height_percent):
        visual_line_height = self.field.cell_length * line_height_percent // 100
        if (self.field.cell_length - visual_line_height) % 2 == 1:
            visual_line_height += 1
        line_indent_height = (self.field.cell_length - visual_line_height) // 2
        return visual_line_height, line_indent_height

    def create_line_images_by_direction(self):
        line_surface_vertical = pygame.Surface((1, self.field.cell_length))
        pygame.draw.line(
            line_surface_vertical, self.body_parameters['colour'],
            (0, self.body_parameters['line_indent']),
            (0, self.body_parameters['line_indent'] +
             self.body_parameters['visual_line_height'] - 1))
        usefull_functions.set_colorkey(line_surface_vertical)
        line_surface_horizontal = pygame.Surface((self.field.cell_length, 1))
        pygame.draw.line(
            line_surface_horizontal, self.body_parameters['colour'],
            (self.body_parameters['line_indent'], 0),
            (self.body_parameters['line_indent'] +
             self.body_parameters['visual_line_height'] - 1, 0))
        usefull_functions.set_colorkey(line_surface_horizontal)
        line_images_by_direction = {constants.LEFT: line_surface_vertical,
                                    constants.RIGHT: line_surface_vertical,
                                    constants.UP: line_surface_horizontal,
                                    constants.DOWN: line_surface_horizontal}
        return line_images_by_direction
    
    # СОЗДАНИЕ ТЕЛА ЗМЕИ
    def create_snake(self):
        # for cell_i_from_head in range(self.body_parameters
        #                               ['snake_length_inFCcs']):
        #     self.snake_body_cells.append(SnakeCell(self, cell_i_from_head))
        for cell_i_from_head in range(self.body_parameters
                                      ['snake_length_inFCcs'] *
                                      self.field.cell_length):
            self.snake_body_lines.append(CellLine(self, cell_i_from_head))
    
    def change_direction(self, new_direction):
        self.direction = new_direction
    
    def update(self):
        self.snake_head.update()
        for line in self.snake_body_lines[::-1]:
            line.update_()


class SnakePiece:
    # head_parameters.keys:
        # 'head_coords_inFCcs'
        # 'form' = {'circle', 'image'}
        # 'fill' = {'colour', 'image'}
        # 'filename' (if 'form' == 'fill' == 'image')
        # 'fill_colour' (if 'fill' == 'colour')
    def __init__(self, snake, piece_i_from_head):
        super().__init__()
        self.snake = snake
        self.direction = self.snake.direction
        self.piece_i_from_head = piece_i_from_head
        # Координаты ячейки без сдвига
        self.image = self.create_image()
        # Координаты ячейки со сдвигом на половину ячейки
        self.rect = self.calc_rect()
        self.previous_move_rest = 0
        
    # IMAGE
    def create_image(self):
        return self.snake.line_images_by_direction[self.direction]

    def calc_rect(self):
        rect = self.image.get_rect()
        # Если Голова, то координаты головы
        if self.piece_i_from_head == 0:
            # half_cell_shift_factors = usefull_functions.get_factors(
            #     shift=self.snake.field.cell_length // 2 - 1, direction=self.direction)
            # rect.x, rect.y = usefull_functions.sum_points(
            #     self.head_coords_inFPcs, half_cell_shift_factors)
            rect.x, rect.y = self.head_coords_inFPcs
        # Если Линия, то сдвинуть относительно ЛевВерхн точки центральной линии
        else:
            rect.x, rect.y = usefull_functions.point_plus_factors(
                self.snake.snake_head.head_center_line_rect_xy,
                self.line_i_from_head_center, self.direction)
        return rect
    
    def update(self):
        self.move()
        # Пересчитать координаты центральной точки для первой Линии
        self.rect = self.calc_rect()
    
    # Двигает координаты головы без сдвига на половину ячейки
    # Определить текущую ячейку через крайнюю точку ячейки Головы
    def move(self):
        # Сразу определяем и записываем координаты текущей ячейки на поле (в ячейках)
        # Находим точку конца ячейки по направлению движения
        edge_point_current_head_coords_inFPcs = self.get_edge_point_head_coords_inFPcs(
            self.head_coords_inFPcs)
        # По крайней точке Головы по направлению движ-я находим текущую ячейку Головы
        self.head_coords_inFCcs = usefull_functions.calc_FCcs_from_FPcs(
            edge_point_current_head_coords_inFPcs, self.snake.field.cell_length)
        
        # Определить возможное положение данного шага
        # Определяем длину данного Шага
        current_step = self.snake.speed + self.previous_move_rest
        # current_step = self.snake.speed // constants.FPS
        self.previous_move_rest = 0
        # Определить возможное положение данного шага
        possible_head_coords_inFPcs = usefull_functions.point_plus_factors(
            self.head_coords_inFPcs, current_step, self.direction)
        
        # Если направление Змеи изменилось
        if self.direction != self.snake.direction:
            # Если следующее движение заходит в другую ячейку
            # Проверка через последнюю точку направления
            edge_point_possible_head_coords_inFPcs = self.get_edge_point_head_coords_inFPcs(
                possible_head_coords_inFPcs)
            possible_head_coords_inFCcs = self.calc_head_coords_inFCcs_from_FPcs(
                edge_point_possible_head_coords_inFPcs)
            
            if possible_head_coords_inFCcs != self.head_coords_inFCcs:
                # Сделать точечные координаты по границам текущей ячейки
                self.head_coords_inFPcs = usefull_functions.calc_rect_xy_from_FCcs(
                    self.head_coords_inFCcs, self.snake.field.cell_length)
                # Сохранить разницу между предполагаемым шагом и шагом до границ ячейки
                self.previous_move_rest = abs(sum(usefull_functions.dif_points(
                    possible_head_coords_inFPcs, self.head_coords_inFPcs)))
                # self.previous_move_rest <- 
                self.direction = self.snake.direction
            else:
                self.head_coords_inFPcs = possible_head_coords_inFPcs
        else:
            self.head_coords_inFPcs = possible_head_coords_inFPcs
        print('current_step', current_step)
    
    def calc_head_center_line_rect_xy(self):
        # Получить координаты Линии
        edge_point_head_coords_inFPcs = \
            self.get_edge_point_head_coords_inFPcs(self.head_coords_inFPcs)
        edge_point_shift_direction = constants.DIRS_NAMES_OPPOSITES[
            self.direction]
        edge_point_xy = usefull_functions.point_plus_factors(
            edge_point_head_coords_inFPcs, self.snake.field.cell_length // 2,
            edge_point_shift_direction)
        return edge_point_xy
        

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
        self.direction = self.snake.direction
        self.parameters = head_parameters
        # Координаты ячейки без сдвига
        self.head_coords_inFCcs = self.parameters.get(
            'head_coords_inFCcs', self.calc_head_coords_inFCcs())
        self.head_coords_inFPcs = self.calc_head_coords_inFPcs_from_FCcs(
            self.head_coords_inFCcs)
        self.image = self.create_image()
        # Координаты ячейки со сдвигом на половину ячейки
        self.rect = self.calc_rect()
        self.head_center_line_rect_xy = \
            self.calc_head_center_line_rect_xy()
        self.previous_move_rest = 0
    
    def calc_head_coords_inFCcs(self):
        head_coords_ranges_inFCcs = self.calc_head_coords_ranges_inFCcs()
        x_range, y_range = zip(*head_coords_ranges_inFCcs)
        head_x_inFCcs = random.randint(*x_range)
        head_y_inFCcs = random.randint(*y_range)
        return (head_x_inFCcs, head_y_inFCcs)
    
    # Сдвинуть границы на 4, чтобы у Игрока была возможность манёвра
    def calc_head_coords_ranges_inFCcs(self):
        # Длина Змеи в ячейках
        snake_length_inFCcs = self.snake.body_parameters['snake_length_inFCcs']
        # Размер Змеи в ячейках
        field_size_inFCcs = (self.snake.field.field_size['inFCcs'])
        field_rect_points = [(0, 0), usefull_functions.point_sub(
            field_size_inFCcs, operand=1)]
        dir_points = constants.DIRS_NAMES_TO_POINTS[self.direction]
        factors = usefull_functions.dif_points(*reversed(dir_points))
        # Отстут на (длину Змеи - 1) от стороны, противоположной направлению
        shift = usefull_functions.point_multiply(
            factors, operand=snake_length_inFCcs - 1)
        if self.direction in ('right', 'down'):
            cell_coords_1, cell_coords_2 = usefull_functions.sum_points(
                field_rect_points[0], shift), field_rect_points[1]
        else:
            cell_coords_1, cell_coords_2 = (
                field_rect_points[0], usefull_functions.sum_points(
                    field_rect_points[1], shift))
        cell_coords_1 = usefull_functions.point_add(cell_coords_1, operand=4)
        cell_coords_2 = usefull_functions.point_add(cell_coords_2, operand=-4)
        return (cell_coords_1, cell_coords_2)
    
    # COORDS
    def calc_head_coords_inFCcs_from_FPcs(self, head_coords_inFPcs):
        head_coords_inFCcs = usefull_functions.point_floor_div(
            head_coords_inFPcs, operand=self.snake.field.cell_length)
        return head_coords_inFCcs
    
    def calc_head_coords_inFPcs_from_FCcs(self, head_coords_inFCcs):
        # Координаты ячейки в точках
        head_coords_inFPcs = usefull_functions.point_multiply(
            head_coords_inFCcs, operand=self.snake.field.cell_length)
        return head_coords_inFPcs
        
    # IMAGE
    def create_image(self):
        form = self.parameters.get('form', 'circle')
        fill = self.parameters.get('fill', 'colour')
        if form == 'circle' and fill == 'colour':
            fill_colour = self.parameters.get('fill_colour', 'red')
            image = usefull_functions.get_circle_image(
                fill_colour, self.snake.field.cell_length)
        usefull_functions.set_colorkey(image)
        return image

    def calc_rect(self):
        rect = self.image.get_rect()
        # half_cell_shift_factors = usefull_functions.get_factors(
        #     shift=self.snake.field.cell_length // 2 - 1, direction=self.direction)
        # rect.x, rect.y = usefull_functions.sum_points(
        #     self.head_coords_inFPcs, half_cell_shift_factors)
        rect.x, rect.y = self.head_coords_inFPcs
        return rect
    
    def update(self):
        print('head_FPcs_before', self.head_coords_inFPcs)
        self.move()
        # Пересчитать координаты центральной точки для первой Линии
        self.head_center_line_rect_xy = \
            self.calc_head_center_line_rect_xy()
        self.rect = self.calc_rect()
        print('head_FPcs_after', self.head_coords_inFPcs)
        # super().update()
    
    # Двигает координаты головы без сдвига на половину ячейки
    def move(self):
        # Сразу определяем и записываем координаты текущей ячейки на поле (в ячейках)
        # Находим точку конца ячейки по направлению движения
        edge_point_current_head_coords_inFPcs = self.get_edge_point_head_coords_inFPcs(
            self.head_coords_inFPcs)
        # По крайней точке Головы по направлению движ-я находим текущую ячейку Головы
        self.head_coords_inFCcs = self.calc_head_coords_inFCcs_from_FPcs(
            edge_point_current_head_coords_inFPcs)
        
        # Определить возможное положение данного шага
        # Определяем длину данного Шага
        current_step = self.snake.speed + self.previous_move_rest
        # current_step = self.snake.speed // constants.FPS
        self.previous_move_rest = 0
        # Определить возможное положение данного шага
        possible_head_coords_inFPcs = usefull_functions.point_plus_factors(
            self.head_coords_inFPcs, current_step, self.direction)
        
        # Если направление Змеи изменилось
        if self.direction != self.snake.direction:
            # Если следующее движение заходит в другую ячейку
            # Проверка через последнюю точку направления
            edge_point_possible_head_coords_inFPcs = self.get_edge_point_head_coords_inFPcs(
                possible_head_coords_inFPcs)
            possible_head_coords_inFCcs = self.calc_head_coords_inFCcs_from_FPcs(
                edge_point_possible_head_coords_inFPcs)
            
            if possible_head_coords_inFCcs != self.head_coords_inFCcs:
                # Сделать точечные координаты по границам текущей ячейки
                self.head_coords_inFPcs = self.calc_head_coords_inFPcs_from_FCcs(
                    self.head_coords_inFCcs)
                # Сохранить разницу между предполагаемым шагом и шагом до границ ячейки
                self.previous_move_rest = abs(sum(usefull_functions.dif_points(
                    possible_head_coords_inFPcs, self.head_coords_inFPcs)))
                # self.previous_move_rest <- 
                self.direction = self.snake.direction
            else:
                self.head_coords_inFPcs = possible_head_coords_inFPcs
        else:
            self.head_coords_inFPcs = possible_head_coords_inFPcs
        print('current_step', current_step)
    
    def calc_head_center_line_rect_xy(self):
        # Получить координаты Линии
        edge_point_head_coords_inFPcs = \
            self.get_edge_point_head_coords_inFPcs(self.head_coords_inFPcs)
        edge_point_shift_direction = constants.DIRS_NAMES_OPPOSITES[
            self.direction]
        edge_point_xy = usefull_functions.point_plus_factors(
            edge_point_head_coords_inFPcs, self.snake.field.cell_length // 2,
            edge_point_shift_direction)
        return edge_point_xy
    
    # Получить координаты крайней по направлению точки головы
    def get_edge_point_head_coords_inFPcs(self, head_coords_inFPcs):
        # Если направление - на уменьшение, то это - координата ЛевВерхн (кв-та Головы)
        if self.direction in (constants.LEFT, constants.UP):
            return head_coords_inFPcs
        # Если же направление - на увеличение, то
        else:
            # Сдвинуть координаты ЛевВерх точки Головы к концу ячейки Головы по направлению движения
            return usefull_functions.point_plus_factors(
                head_coords_inFPcs, self.snake.field.cell_length - 1,
                self.direction)
    
        
# class SnakeCell(pygame.sprite.Group):
#     def __init__(self, snake, cell_i_from_head):
#         super().__init__()
#         self.snake = snake
#         self.cell_i_from_head = cell_i_from_head
#         self.cell_length = self.snake.field.cell_length
#         for line_i_from_head_center in range(self.cell_length):
#             self.add(CellLine(self, line_i_from_head_center))
#         # ЗДЕСЬ 20.03.2024


class CellLine(pygame.sprite.Sprite):
    # def __init__(self, snake_cell, line_i_from_head_center):
    def __init__(self, snake, line_i_from_head_center):
        super().__init__()
        self.snake = snake
        self.line_i_from_head_center = line_i_from_head_center
        # self.direction = self.snake_cell.snake.direction
        self.direction = self.snake.direction
        self.image = self.snake.line_images_by_direction[self.direction]
        self.rect = self.calc_rect()

    def calc_rect(self):
        rect = self.image.get_rect()
        factors_for_shift_from_head = usefull_functions.get_factors(
            shift=self.line_i_from_head_center,
            direction=constants.DIRS_NAMES_OPPOSITES[self.direction])
        rect.x, rect.y = usefull_functions.sum_points(
            self.snake.snake_head.head_center_line_rect_xy,
            factors_for_shift_from_head)
        return rect
    
    def get_parameters(self):
        return {'direction': self.direction,
                'image': self.image,
                'rect': self.rect}
    
    def set_parameters(self, **parameters):
        self.direction = parameters.get('direction', self.direction)
        self.image = parameters.get('image', self.image)
        self.rect = parameters.get('rect', self.rect)
    
    def update_(self):
        # Если это не первая Линия
        if self.line_i_from_head_center != 0:
            previous_line = self.snake.snake_body_lines[
                self.line_i_from_head_center - 1]       # -1 - предыдущая Линия в сторону Головы
            self.set_parameters(**previous_line.get_parameters())
        else:
            # Получить параметры Линии из параметров Головы
            new_line_direction = self.snake.snake_head.direction
            new_line_image = self.snake.line_images_by_direction[
                new_line_direction]
            new_rect = new_line_image.get_rect()
            # Получить новые координаты Линии
            new_rect.x, new_rect.y = \
                self.snake.snake_head.head_center_line_rect_xy
            self.set_parameters(direction=new_line_direction,
                                image=new_line_image,
                                rect=new_rect)
            