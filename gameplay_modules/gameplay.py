import pygame
import constants
from gameplay_modules import snake as snake_of_player
from gameplay_modules import food
from gameplay_modules import scorelabel
import usefull_functions


# GameApp:
    # AppMenu:
        # MainMenu: Menu
            # SettingsMenu: Menu
                # ChangeResolutionMenu: Menu
                # ChangeCellSizeMenu: Menu
    # GamePlay
        # ScoreInterface (Sprite)
        # Field (Sprite)
            # Food (Group)
            # Snake (Group)
                # SnakeHead(Sprite)
                # SnakeCell(Group)
                    # CellLine(Sprite)

# game_app.current_process
class GamePlay(pygame.sprite.Group):
    def __init__(self, game_app):
        super().__init__()
        self.game_app = game_app
        self.resolution = self.game_app.resolution      # object
        self.cell_length = self.game_app.cell_length
        self.screen = self.game_app.screen
        # keys:
            # 'score':
            # 'field':
        self.surface_parts_rects = self.calc_surface_parts_rects()
        self.surface_parts = {
            'score': ScoreInterface(self, self.surface_parts_rects['score']),
            'field': Field(self, self.surface_parts_rects['field'])}
        self.add(*self.surface_parts.values())
    
    @property
    def food(self):
        return self.surface_parts['field'].field_parts['food']
    
    @property
    def snake_of_player(self):
        return self.surface_parts['field'].field_parts['snake_of_player']
    
    @property
    def score_interface(self):
        return self.surface_parts['score']
    
    @property
    def field(self):
        return self.surface_parts['field']
    
    def calc_surface_parts_rects(self):
        score_rect = pygame.Rect(0, 0, *self.resolution.xy.xy)
        score_rect.w = (self.resolution.xy.to_FCcs(self.cell_length) *
                        constants.SCORE_PERCENT_OF_RESOLUTION // 100).to_FPcs(
                            self.cell_length).x
        field_rect = pygame.Rect(score_rect.w, 0, *self.resolution.xy.xy)
        field_rect.w -= score_rect.w
        return {'score': score_rect,
                'field': field_rect}
 
    # GameApp.main_loop().current_process.draw()
    def draw(self):
        super().update()               # сначала обновление score и field
        super().draw(self.screen)   # затем их прорисовка
    
    def event_handler(self, event):
        if event.type == pygame.KEYDOWN:
            if (event.key in constants.KEYS_DIRS) and event.key not in (
                  self.snake_of_player.direction.key,
                  self.snake_of_player.direction.reverse.key):
                self.snake_of_player.change_direction(
                    constants.Direction(event.key))
        elif event.type == constants.SNAKE_MOVE_EVENT:
            # Вызываем напрямую метод SnakeHead.update(). Если бы нужно было
             # вызвать еще какие-то действия, то нужно было бы прогнать через
             # элементы иерархии структуры программы.
            self.snake_of_player.move()
            # self.snake_of_player.snake_head.move()
        elif event.type in (constants.FOOD_PIECE_NEED_EVENT,
                            constants.FOOD_PIECE_EATEN_EVENT):
            self.surface_parts['field'].event_handler(event)
            self.surface_parts['score'].event_handler(event)
        elif event.type == constants.SNAKE_CRASH_EVENT:
            # Сделать появление исчезающего сообщения о потере жизни
            self.surface_parts['score'].event_handler(event)
            self.surface_parts['field'].event_handler(event)
            if self.score_interface.lifes:
                pygame.time.set_timer(constants.GAME_CONTINUE_AFTER_LIFE_LOSS_EVENT,
                                      millis=1000, loops=1)
            else:
                self.game_over()
        elif event.type == constants.GAME_CONTINUE_AFTER_LIFE_LOSS_EVENT:
            self.surface_parts['score'].event_handler(event)
            self.surface_parts['field'].event_handler(event)
        elif event.type == constants.SPEED_UP_EVENT:
            self.surface_parts['score'].event_handler(event)
            self.surface_parts['field'].event_handler(event)

    def game_over(self):
        pass


# Панель подсчёта очков
class ScoreInterface(pygame.sprite.Sprite):
    def __init__(self,
                 game_play,
                 score_rect,
                 parameters=constants.SCORE_START_PARAMETERS):
        super().__init__()
        self.game_play = game_play
        self.rect = score_rect
        self.image = pygame.Surface(self.rect.size)
        # Сделать через @property
        # self.speed_ = parameters.get('speed')
        self.level = parameters.get('level')
        self.lifes = parameters.get('lifes')
        self.score_value = parameters.get('score_value')
        self.indent_pixels = parameters.get('indent_pixels')
        self.indents_positions = self.calc_indents_positions(
            self.indent_pixels)
        self.score_labels = self.create_labels()
    
    @property
    def field(self):
        return self.game_play.surface_parts['field']
    
    @property
    def snake(self):
        return self.field.field_parts['snake_of_player']
    
    @property
    def food(self):
        return self.field.field_parts['food']
        
    @property
    def cell_length(self):
        return self.game_play.cell_length
    
    # GameApp.main_loop().current_process.draw() ->
    # from GamePlay.draw() -> GamePlay.super().update()
    def update(self):
        self.image.fill(constants.SCORE_FILL_COLOUR)
        for label_name in self.score_labels:
            self.score_labels[label_name].draw(self.image)
    
    def get_score(self):
        return self.score_value

    def get_lifes(self):
        return self.lifes
    
    # Алгоритм вычисления уровня скорости (в единицах) по количеству очков
     # основан на том, что скорость (как и её уровень) увеличивается при достижении
     # количества очков, равного произведению суммы квадратов степеней всех предыдущих
     # уровней скорости на константу очков.
    def calc_speed_level(self):
        score_count = self.score_value / constants.FOOD_PIECE_SCORE
        for speed_level in range(1000):
            if score_count < sum(level ** 2 for level in range(
                  speed_level + 1)):
                return speed_level
    
    def calc_indents_positions(self, indent):
        return {constants.LEFT: indent,
                constants.RIGHT: self.rect.w - indent,
                constants.UP: indent}
    
    def create_labels(self):
        score_labels = {}
        # Label parameters:
            # interface,
            # name, y_position, align, max_length_symbols,
            # font_parametrs:
                # file_path,
                # size,
                # colour
            # start_value='',
            # changeable=False, change_event_type=None,
            # new_value_property=None
        next_y_position = self.indents_positions[constants.UP]
        score_labels['жизни'] = scorelabel.Label(
            interface=self,
            name='жизни', y_position=next_y_position, align=constants.LEFT,
            max_length_symbols=10,
            font_parameters=constants.SCORE_FONT_PARAMETERS,
            start_value='ЖИЗНИ:')
        next_y_position = score_labels['жизни'].rect.bottom + self.indent_pixels
        score_labels['жизни_значение'] = scorelabel.Label(
            interface=self,
            name='жизни_значение', y_position=next_y_position, align=constants.RIGHT,
            max_length_symbols=4,
            font_parameters=constants.SCORE_FONT_PARAMETERS,
            start_value=3,
            changeable=True, change_event_type=constants.SNAKE_CRASH_EVENT,
            update_value_callable=self.get_lifes)
        next_y_position = score_labels['жизни_значение'].rect.bottom + self.indent_pixels
        score_labels['очки'] = scorelabel.Label(
            interface=self,
            name='очки', y_position=next_y_position, align=constants.LEFT,
            max_length_symbols=10,
            font_parameters=constants.SCORE_FONT_PARAMETERS,
            start_value='ОЧКИ: ')
        next_y_position = score_labels['очки'].rect.bottom + self.indent_pixels
        score_labels['очки_значение'] = scorelabel.Label(
            interface=self,
            name='очки_значение', y_position=next_y_position, align=constants.RIGHT,
            max_length_symbols=6,
            font_parameters=constants.SCORE_FONT_PARAMETERS,
            start_value=0,
            changeable=True, change_event_type=constants.FOOD_PIECE_EATEN_EVENT,
            update_value_callable=self.get_score)
        next_y_position = score_labels['очки_значение'].rect.bottom + self.indent_pixels
        score_labels['уровень'] = scorelabel.Label(
            interface=self,
            name='уровень', y_position=next_y_position, align=constants.LEFT,
            max_length_symbols=10,
            font_parameters=constants.SCORE_FONT_PARAMETERS,
            start_value='УРОВЕНЬ: ')
        next_y_position = score_labels['уровень'].rect.bottom + self.indent_pixels
        score_labels['уровень_значение'] = scorelabel.Label(
            interface=self,
            name='уровень_значение', y_position=next_y_position, align=constants.RIGHT,
            max_length_symbols=6,
            font_parameters=constants.SCORE_FONT_PARAMETERS,
            start_value=1)
        next_y_position = score_labels['уровень_значение'].rect.bottom + self.indent_pixels
        score_labels['скорость'] = scorelabel.Label(
            interface=self,
            name='скорость', y_position=next_y_position, align=constants.LEFT,
            max_length_symbols=10,
            font_parameters=constants.SCORE_FONT_PARAMETERS,
            start_value='СКОРОСТЬ: ')
        next_y_position = score_labels['скорость'].rect.bottom + self.indent_pixels
        score_labels['скорость_значение'] = scorelabel.Label(
            interface=self,
            name='скорость_значение', y_position=next_y_position, align=constants.RIGHT,
            max_length_symbols=6,
            font_parameters=constants.SCORE_FONT_PARAMETERS,
            start_value=1,
            changeable=True, change_event_type=constants.SPEED_UP_EVENT,
            update_value_callable=self.calc_speed_level)
        return score_labels
    
    # GamePlay.event_handler() ->
    def event_handler(self, event):
        if event.type == constants.FOOD_PIECE_EATEN_EVENT:
            current_speed_level = self.calc_speed_level()
            self.score_value += constants.FOOD_PIECE_SCORE * self.calc_speed_level()
            self.score_labels['очки_значение'].event_handler(event)
            self.food.event_handler(event)
            if current_speed_level != self.calc_speed_level():
                pygame.event.post(pygame.event.Event(constants.SPEED_UP_EVENT))
        elif event.type == constants.SNAKE_CRASH_EVENT and self.snake.is_moving:
            self.lifes -= 1
            self.score_labels['жизни_значение'].event_handler(event)
        elif event.type == constants.SPEED_UP_EVENT:
            self.score_labels['скорость_значение'].event_handler(event)
        
        
# Игровое Поле
class Field(pygame.sprite.Sprite):
    def __init__(self, game_play, field_rect):
        super().__init__()
        self.game_play = game_play
        self.rect = field_rect
        self.image = pygame.Surface(self.rect.size)
        # Изменения и генерация новых элементов Snake и Food только на update
        self.field_parts = {'snake_of_player': snake_of_player.Snake(self),
                            'food': food.Food(self)}
        # @properties
            # cell_length
            # field_size_inFPcs
            # snake
            # food
            # snake_head

    @property
    def cell_length(self):
        return self.game_play.cell_length
    
    @property
    def field_size_inFPcs(self):
        return constants.Point(self.rect.size)
    
    @property
    def snake(self):
        return self.field_parts['snake_of_player']
    
    @property
    def food(self):
        return self.field_parts['food']
    
    @property
    def snake_head(self):
        return self.snake.snake_head
    
    @property
    def score_interface(self):
        return self.game_play.surface_parts['score']
    
    # Нарисовать сетку для тестирования движения
    def test_net_points(self):
        field_size_inFCcs = self.field_size_inFPcs.to_FCcs(self.cell_length)
        for x in range(field_size_inFCcs.x):
            for y in range(field_size_inFCcs.y):
                pygame.draw.rect(self.image, 'black',
                                 (x * self.cell_length,
                                  y * self.cell_length, 1, 1))

    # GameApp.main_loop().current_process.draw() ->
    # from GamePlay.draw() -> GamePlay.super().update()
    def update(self):
        self.image.fill('green')
        self.test_net_points()
        # Обновление настоящего спрайта через рисование его частей
        for field_part in self.field_parts.values():
            field_part.update()
            field_part.draw(self.image)
        # Проверка на столкновение Головы с Едой и генерация события съедания
        if pygame.sprite.groupcollide(
              [self.snake_head], self.field_parts['food'], False, True):
            pygame.event.post(pygame.event.Event(
                constants.FOOD_PIECE_EATEN_EVENT))
        elif (pygame.sprite.groupcollide(
              [self.snake_head], self.snake.snake_body_lines[
                  self.cell_length * 2:], False, False) or
              self.borders_collide()) and self.snake.is_moving:
            pygame.event.post(pygame.event.Event(
                constants.SNAKE_CRASH_EVENT))

    def borders_collide(self):
        return any(((self.snake_head.rect.left < 0),
                    (self.snake_head.rect.right > self.rect.w - 1),
                    (self.snake_head.rect.top < 0),
                    (self.snake_head.rect.bottom > self.rect.h - 1)))
    
    def recreate_snake(self):
        length_inFCcs = self.snake.length_inFCcs
        speed = self.snake.speed
        self.field_parts['snake_of_player'] = snake_of_player.Snake(
            self, snake_parameters={'speed': speed,
                                    'length_inFCcs': length_inFCcs})
    
    def event_handler(self, event):
        if event.type == constants.FOOD_PIECE_NEED_EVENT:
            self.field_parts['food'].event_handler(event)
        elif event.type == constants.FOOD_PIECE_EATEN_EVENT:
            self.field_parts['food'].event_handler(event)
            self.field_parts['snake_of_player'].event_handler(event)
        elif event.type == constants.SNAKE_CRASH_EVENT:
            self.snake.event_handler(event)
            self.food.event_handler(event)
        elif event.type == constants.GAME_CONTINUE_AFTER_LIFE_LOSS_EVENT:
            self.recreate_snake()
            self.food.event_handler(event)
        elif event.type == constants.SPEED_UP_EVENT:
            self.snake.event_handler(event)
    