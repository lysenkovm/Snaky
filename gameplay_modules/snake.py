import pygame
import random
import constants
import usefull_functions


# GamePlay (Group)
    # ScoreInterface (Sprite)
    # Field (Sprite)
        # Food (Group)
        # Snake (Group)
            # SnakeHead(Sprite)
            # SnakeCell(Group)
                # BodyLine(Sprite)


# Snake:
    # shake_head: SnakeHead(head_parameters)
    # snake_body_cells: []
    # snake_tail: ???
class Snake(pygame.sprite.Group):
    def __init__(self,
                 field,
                 snake_parameters={},
                 head_parameters={},
                 body_parameters=constants.BODY_PARAMETERS,
                 tail_parameters={}):
        super().__init__()
        self.field = field
        self.direction = constants.Direction(random.choice(constants.DIRS_NAMES))
        # self.direction = constants.UP
        # Скорость делить на FPS только во время прорисовки!!!!!!!!!!
        # snake_parameters
            # 'speed'
        self.speed = snake_parameters.get('speed', constants.SNAKE_SPEED_MIN)
        
        # BODY_PARAMETERS:
            # 'length_inFCcs'
            # 'snake_thickness_percent'
            # 'colour'
        self.length_inFCcs = body_parameters.get('length_inFCcs')
        self.body_thickness_percent = body_parameters.get(
            'body_thickness_percent')
        self.body_colour = body_parameters.get('colour')
        # Части Змеи
        # self.body_parts_images: 'on_bend', LEFT, RIGHT, UP, DOWN
        self.body_parts_images = self.create_body_parts_images()

        # СОЗДАНИЕ ГОЛОВЫ (длина Змеи должна быть уже задана)
        # Здесь!!!
        self.snake_head = SnakeHead(self, head_parameters)
        # СОЗДАНИЕ ТЕЛА
        self.snake_body_lines = []
        self.growing_body(self.length_inFCcs)
        self.body_bends = []
        # Скорость движения Змеи не должна зависеть от скорости прорисовки Змеи
        pygame.time.set_timer(constants.SNAKE_MOVE_EVENT, 1000 // self.speed)
        # self.add(*self.body_bends, self.snake_head)  # Потом добавить ячейки тела и хвост
        # @properties
            # body_thickness
            # indent_before_thickness

    @property
    def body_thickness(self):
        # Если длина ячейки минус толщина тела Змеи - нечётное число (т.е. отступы
         # окажутся не равны или дробным числом), то увеличить толщину на 1
        body_thickness = self.cell_length * self.body_thickness_percent // 100
        if (self.cell_length - body_thickness) % 2:
            return body_thickness + 1
        else:
            return body_thickness
    
    @property
    def indent_before_thickness(self):
        return (self.cell_length - self.body_thickness) // 2

    @property
    def field_size_inFPcs(self):
        return self.field.field_size_inFPcs
    
    @property
    def cell_length(self):
        return self.field.cell_length
    
    # from Field.update()
    def update(self):
        self.snake_head.update()
        # Обновление - в обратном порядке
        for line in self.snake_body_lines[::-1]:
            line.update()
        self.update_body_bends()

    def draw(self, surface):
        for bend in self.body_bends:
            surface.blit(bend.image, bend.rect)
        # print(self.snake_body_lines)
        for line in self.snake_body_lines:
            # print(line.image, line.rect)
            surface.blit(line.image, line.rect)
        surface.blit(self.snake_head.image, self.snake_head.rect)
    
    # Создание словаря изображений: гор. и верт. линий и сгибов
    def create_body_parts_images(self):
        # Вертикальная Линия
        line_vertical_image = pygame.Surface((1, self.cell_length))
        thickness_vertical_rect = pygame.Rect(
            0, self.indent_before_thickness, 1, self.body_thickness)
        pygame.draw.line(
            line_vertical_image, self.body_colour,
            thickness_vertical_rect.topleft, thickness_vertical_rect.size)
        usefull_functions.set_colorkey(line_vertical_image)
        # Горизонтальная Линия
        line_horizontal_image = pygame.Surface((self.cell_length, 1))
        thickness_horizontal_rect = pygame.Rect(
            self.indent_before_thickness, 0, self.body_thickness, 1)
        pygame.draw.line(
            line_horizontal_image, self.body_colour,
            thickness_horizontal_rect.topleft, thickness_horizontal_rect.size)
        usefull_functions.set_colorkey(line_horizontal_image)
        # Круг на сгибе
        on_bend_image = pygame.Surface((self.cell_length,
                                        self.cell_length))
        pygame.draw.ellipse(on_bend_image, self.body_colour,
                            on_bend_image.get_rect())
        usefull_functions.set_colorkey(on_bend_image)
        # Полный словарь изображений
        body_parts_images = {constants.LEFT: line_vertical_image,
                             constants.RIGHT: line_vertical_image,
                             constants.UP: line_horizontal_image,
                             constants.DOWN: line_horizontal_image,
                             'on_bend': on_bend_image}
        return body_parts_images
    
    # СОЗДАНИЕ ТЕЛА ЗМЕИ
    def growing_body(self, cells_quantity_inFCcs=1):
        # Линии создаются в порядке возрастания отдаления от Головы
        if not self.snake_body_lines:           # Если список Линий пуст,
            next_line_i_from_head_center = 0    # Следующий номер Линии - 0.
            previous_direction = self.snake_head.direction.copy()  # Направление предыдущего объекта - направлени Головы.
        else:
            next_line_i_from_head_center = self.snake_body_lines[  # Следующий номер Линии -
                -1].line_i_from_head_center + 1     # номер последней Линии в списке (наибольший) + 1
            previous_direction = self.snake_body_lines[-1].direction.copy()  # Направление предыдущего объекта - направление предыдущей Линии
        for line_i_from_head_center in range(next_line_i_from_head_center,
                                             next_line_i_from_head_center +
                                             cells_quantity_inFCcs *
                                             self.cell_length):
            new_line = BodyLine(self, line_i_from_head_center,
                                previous_direction)
            self.snake_body_lines.append(new_line)
            # self.add(new_line)
    
    # Обновление поворотов Тела Змеи
    def update_body_bends(self):
        self.body_bends = []   # Очистить список поворотов
        for line1, line2 in zip(self.snake_body_lines[:-1],     # Перебрать Линии
                                self.snake_body_lines[1:]):      # попарно
            # если направления отличаются и 
            if line1.direction.name != line2.direction.name:
                self.body_bends.append(BodyBend(self, line2))
        # self.add(*self.body_bends)
    
    def change_direction(self, new_direction):
        self.direction = new_direction.copy()
    
    # Eating
    def change_parameters_on_eating(self, speed_growth_percents,
                                    body_growth_inFCcs):
        self.speed += 1
        self.growing_body(body_growth_inFCcs)
    
    def event_handler(self, event):
        if event.type == constants.FOOD_PIECE_EATEN_EVENT:
            self.growing_body()
    

class SnakeHead(pygame.sprite.Sprite):
    # head_parameters.keys:
        # 'head_coords_inFCcs'
        # 'form' = 'circle'/'image'
         # 'filename' (if 'form' == 'image')
        # 'fill' = 'colour'/'image'
         # 'fill_colour' (if 'fill' == 'colour')
    def __init__(self, snake, head_parameters={}):
        super().__init__()
        self.snake = snake
        self.direction = self.snake.direction.copy()
        # Координаты ячейки без сдвига
        self.head_coords_inFCcs = head_parameters.get(
            'head_coords_inFCcs', self.calc_head_coords_inFCcs())
        self.head_coords_inFPcs = self.head_coords_inFCcs.to_FPcs(
            self.cell_length)
        # Изображение Головы
        self.image = self.create_image(head_parameters)
        # Координаты ячейки со сдвигом на половину ячейки
        self.rect = self.calc_rect()
        # @properties
            # self.head_center_line_rect_xy
            # 
    
    @property
    def field_size_inFPcs(self):
        return self.snake.field_size_inFPcs
    
    @property
    def cell_length(self):
        return self.snake.cell_length
    
    @property
    def head_center_line_rect_xy(self):
        line_rect_by_direction = self.snake.body_parts_images[
            self.direction.name].get_rect()
        return constants.Point(line_rect_by_direction.topleft) + \
            self.direction.axis.direction_increase.factors * \
                self.cell_length // 2
    
    # 1.
    # Инициализация объекта
    def calc_head_coords_inFCcs(self):
        
        def calc_rect_Points_inFCcs():
            rect_Points = [constants.Point(0, 0),
                           self.field_size_inFPcs.to_FCcs(
                               self.cell_length).copy()]
            body_length_indent_Point = self.direction.reverse.factors * \
                self.snake.length_inFCcs
            indent_Point = self.direction.factors * \
                constants.SNAKE_START_INDENT_FOR_MOVING
            if self.direction.is_increasing():
                rect_Points[0] -= body_length_indent_Point
                rect_Points[1] -= indent_Point
            else:
                rect_Points[0] -= indent_Point
                rect_Points[1] -= body_length_indent_Point
            return rect_Points
        
        rect_Points_inFCcs = calc_rect_Points_inFCcs()
        head_x_inFCcs = random.randint(rect_Points_inFCcs[0].x,
                                       rect_Points_inFCcs[1].x)
        head_y_inFCcs = random.randint(rect_Points_inFCcs[0].y,
                                       rect_Points_inFCcs[1].y)
        return constants.Point(head_x_inFCcs, head_y_inFCcs)
            
    # IMAGE
    def create_image(self, head_parameters):
        form = head_parameters.get('form', 'circle')
        fill = head_parameters.get('fill', 'colour')
        if form == 'circle' and fill == 'colour':
            fill_colour = head_parameters.get(
                'fill_colour', constants.SNAKE_HEAD_FILL_COLOUR)
            image = usefull_functions.get_circle_image(
                fill_colour, self.cell_length)
        usefull_functions.set_colorkey(image)
        return image
    
    def calc_rect(self):
        rect = self.image.get_rect()
        rect.topleft = self.head_coords_inFPcs.xy
        return rect
    
    # 2.
    # Изменение объекта
    # Обновление (движение) через обработчик событий Змеи
    # from Field.update() -> Snake.update()
    def update(self):
        self.rect = self.calc_rect()
        
    # Двигает координаты головы без сдвига на половину ячейки
    # from GamePlay.event_handler()
    def move(self):
        # Сразу определяем и записываем координаты текущей ячейки на поле (в ячейках)
        # По крайней точке Головы по направлению движ-я находим текущую ячейку Головы
        self.head_coords_inFCcs = self.head_coords_inFPcs.to_FCcs(
            self.cell_length, self.direction)
        # Определить возможное положение данного шага
        # Определяем длину данного Шага
        current_step = 1
        # Определить возможное положение данного шага
        possible_head_coords_inFPcs = self.head_coords_inFPcs + \
            self.direction.factors * current_step
        # Если направление Змеи изменилось
        if self.direction != self.snake.direction:
            # Если следующее движение заходит в другую ячейку
            # Проверка через последнюю точку направления
            possible_head_coords_inFCcs = possible_head_coords_inFPcs.to_FCcs(
                self.cell_length, self.direction)
            if possible_head_coords_inFCcs != self.head_coords_inFCcs:
                # Сделать точечные координаты по границам текущей ячейки
                self.direction = self.snake.direction.copy()
                self.head_coords_inFPcs = self.head_coords_inFPcs + \
                    self.direction.factors * current_step
            else:
                self.head_coords_inFPcs = possible_head_coords_inFPcs
        else:
            self.head_coords_inFPcs = possible_head_coords_inFPcs


class BodyLine(pygame.sprite.Sprite):
    # def __init__(self, snake_cell, line_i_from_head_center):
    def __init__(self,
                 snake,
                 line_i_from_head_center,
                 previous_direction):
        super().__init__()
        self.snake = snake
        self.line_i_from_head_center = line_i_from_head_center
        self.direction = previous_direction.copy()
        self.image = self.snake.body_parts_images[self.direction.name]
        self.rect = self.calc_rect()

    @property
    def head_coords_inFPcs(self):
        return self.snake.snake_head.head_coords_inFPcs.copy()
    
    @property
    def head_direction(self):
        return self.snake.snake_head.direction.copy()
    
    @property
    def head_center_line_rect_xy(self):
        return self.snake.snake_head.head_center_line_rect_xy

    def calc_rect(self):
        rect = self.image.get_rect()
        print(self.line_i_from_head_center)
        print(rect)
        rect.x, rect.y = (self.head_coords_inFPcs +
                          self.direction.reverse.factors *
                          self.line_i_from_head_center).xy
        print(rect)
        print()
        return rect
    
    def set_parameters(self, **parameters):
        self.direction = parameters.get('direction', self.direction)
        self.image = parameters.get('image', self.image)
        self.rect = parameters.get('rect', self.rect)
    
    # from Field.update() -> Snake.update()
    def update(self):
        # Если это первая Линия
        if self.line_i_from_head_center == 0:
            new_line_image = self.snake.body_parts_images[
                self.head_direction.name]
            new_line_rect = new_line_image.get_rect()
            new_line_rect.x, new_line_rect.y = self.head_center_line_rect_xy.xy
            new_line_direction = self.direction.copy()
        else:
            previous_line = self.snake.snake_body_lines[
                self.line_i_from_head_center - 1]
            new_line_image = previous_line.image
            new_line_rect = previous_line.rect
            new_line_direction = previous_line.direction.copy()
        self.set_parameters(direction=new_line_direction,
                            image=new_line_image, rect=new_line_rect)
        

# Лучше сделать просто Surface и рисовтаь первым
class BodyBend(pygame.sprite.Sprite):
    def __init__(self, snake, line):
        super().__init__()
        self.snake = snake
        self.line = line
        self.image = self.snake.body_parts_images['on_bend']
        self.rect = self.image.get_rect()
        self.rect.center = self.line.rect.center
