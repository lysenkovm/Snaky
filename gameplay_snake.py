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
        self.growing_body(self.body_parameters['snake_length_inFCcs'])
        #test>
        self.body_bends = []
        self.add(*self.body_bends, self.snake_head)  # Потом добавить ячейки тела и хвост
        
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
        # Круг на сгибе
        line_surface_on_bend = pygame.Surface((self.field.cell_length,
                                               self.field.cell_length))
        circle_center = (self.field.cell_length // 2, ) * 2
        pygame.draw.circle(
            line_surface_on_bend, self.body_parameters['colour'],
            circle_center, self.body_parameters['visual_line_height'] // 2)
        usefull_functions.set_colorkey(line_surface_on_bend)
        
        line_images_by_direction = {constants.LEFT: line_surface_vertical,
                                    constants.RIGHT: line_surface_vertical,
                                    constants.UP: line_surface_horizontal,
                                    constants.DOWN: line_surface_horizontal,
                                    'on_bend': line_surface_on_bend}
        return line_images_by_direction
    
    # СОЗДАНИЕ ТЕЛА ЗМЕИ
    def growing_body(self, cells_quantity_inFCcs):
        # Линии создаются в порядке возрастания отдаления от Головы
        last_line_i_from_head_center = (
            -1 if not self.snake_body_lines else
            self.snake_body_lines[-1].line_i_from_head_center)
        previous_direction = (self.snake_head.direction
                              if not self.snake_body_lines else
                              self.snake_body_lines[-1].direction)
        for line_i_from_head_center in range(last_line_i_from_head_center + 1,
                                             last_line_i_from_head_center + 1 +
                                             cells_quantity_inFCcs *
                                             self.field.cell_length):
            new_line = CellLine(self, line_i_from_head_center,
                                previous_direction)
            self.snake_body_lines.append(new_line)
            self.add(new_line)
        # for line in self.
    
    def update_body_bends(self):
        self.remove(*self.body_bends)
        self.body_bends = []
        for line1, line2 in zip(self.snake_body_lines[:-1],
                                self.snake_body_lines[1:]):
            if (line1.direction != line2.direction and
                line1.line_i_from_head_center > self.field.cell_length // 2):
                self.body_bends.append(CellBend(self, line2))
        self.add(*self.body_bends)
    
    def change_direction(self, new_direction):
        self.direction = new_direction
    
    def update(self):
        for move_i in range(self.speed):
            self.snake_head.update()
            # Обновление - в обратном порядке
            for line in self.snake_body_lines[::-1]:
                line.update_()
        self.update_body_bends()
    
    # Eating
    def change_parameters_on_eating(self, speed_growth_percents,
                                    body_growth_inFCcs):
        self.speed += 1
        self.growing_body(body_growth_inFCcs)
    

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
        self.head_center_line_rect_xy = self.calc_head_center_line_rect_xy()
    
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
        rect.x, rect.y = self.head_coords_inFPcs
        return rect
    
    def update(self):
        self.move()
        # Пересчитать координаты центральной точки для первой Линии
        self.head_center_line_rect_xy = \
            self.calc_head_center_line_rect_xy()
        self.rect = self.calc_rect()
        
    
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
        current_step = 1
        # current_step = self.snake.speed // constants.FPS
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
                self.direction = self.snake.direction
            else:
                self.head_coords_inFPcs = possible_head_coords_inFPcs
        else:
            self.head_coords_inFPcs = possible_head_coords_inFPcs
    
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
    

class CellLine(pygame.sprite.Sprite):
    # def __init__(self, snake_cell, line_i_from_head_center):
    def __init__(self, snake, line_i_from_head_center, previous_direction):
        super().__init__()
        self.snake = snake
        self.line_i_from_head_center = line_i_from_head_center
        # self.direction = self.snake_cell.snake.direction
        self.direction = previous_direction
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
    
    def set_parameters(self, **parameters):
        self.direction = parameters.get('direction', self.direction)
        self.image = parameters.get('image', self.image)
        self.rect = parameters.get('rect', self.rect)
    
    def update_(self):
        # TOPLEFT, BOTTOMLEFT !!!!!!
        # Если это первая Линия
        if self.line_i_from_head_center == 0:
            new_line_direction = self.snake.snake_head.direction
            new_line_image = self.snake.line_images_by_direction[
                new_line_direction]
            new_line_rect = new_line_image.get_rect()
            new_line_rect.x, new_line_rect.y = \
                self.snake.snake_head.head_center_line_rect_xy
        else:
            previous_line = self.snake.snake_body_lines[
                self.line_i_from_head_center - 1]
            new_line_direction = previous_line.direction
            new_line_image = previous_line.image
            new_line_rect = previous_line.rect
        self.set_parameters(direction=new_line_direction,
                            image=new_line_image, rect=new_line_rect)
        

class CellBend(pygame.sprite.Sprite):
    def __init__(self, snake, line):
        super().__init__()
        self.snake = snake
        self.line = line
        self.image = self.snake.line_images_by_direction['on_bend']
        self.rect = self.calc_rect()
    
    def calc_rect(self):
        rect = self.image.get_rect()
        if constants.DIRS_NAMES_AXES[self.line.direction] == constants.VERTICAL:
            shift_direction = constants.UP
        else:
            shift_direction = constants.LEFT
        rect.topleft = usefull_functions.point_plus_factors(
            self.line.rect.topleft, self.snake.field.cell_length // 2,
            shift_direction)
        return rect