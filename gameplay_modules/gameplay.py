import pygame
import constants
from gameplay_modules import snake as snake_of_player
from gameplay_modules import food


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
    
    def calc_surface_parts_rects(self):
        score_rect = pygame.Rect(0, 0, *self.resolution.xy.xy)
        score_rect.w = (self.resolution.xy.x *
                        constants.SCORE_PERCENT_OF_RESOLUTION // 100)
        field_rect = pygame.Rect(score_rect.w, 0, *self.resolution.xy.xy)
        field_rect.w -= score_rect.w
        return {'score': score_rect,
                'field': field_rect}
 
    def draw(self):     # GameApp.current_process.draw()
        self.update()               # сначала обновление score и field
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
            self.snake_of_player.snake_head.move()
        elif event.type in (constants.FOOD_PIECE_NEED_EVENT,
                            constants.FOOD_PIECE_EATEN_EVENT):
            self.surface_parts['field'].event_handler(event)


# Панель подсчёта очков
class ScoreInterface(pygame.sprite.Sprite):
    def __init__(self, game_play, score_rect):
        super().__init__()
        self.game_play = game_play
        self.rect = score_rect
        self.image = pygame.Surface(self.rect.size)
    
    # from GamePlay.draw()
    def update(self):
        super().update()
        self.image.fill(constants.SCORE_FILL_COLOUR)
        
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

    @property
    def cell_length(self):
        return self.game_play.cell_length
    
    @property
    def field_size_inFPcs(self):
        return constants.Point(self.rect.size)
    
    # Нарисовать сетку для тестирования движения
    def test_net_points(self):
        field_size_inFCcs = self.field_size_inFPcs.to_FCcs(self.cell_length)
        for x in range(field_size_inFCcs.x):
            for y in range(field_size_inFCcs.y):
                pygame.draw.rect(self.image, 'black',
                                 (x * self.cell_length,
                                  y * self.cell_length, 1, 1))

    # from GamePlay.draw()
    def update(self):
        self.image.fill('green')
        self.test_net_points()
        # Обновление настоящего спрайта через рисование его частей
        for field_part in self.field_parts.values():
            field_part.update()
            field_part.draw(self.image)
        # Проверка на столкновение Головы с Едой и генерация события съедания
        if collisions := pygame.sprite.groupcollide(
                self.field_parts['snake_of_player'],
                self.field_parts['food'], False, True):
            pygame.event.post(constants.FOOD_PIECE_EATEN_EVENT)
    
    def action_on_food_collision(self, collisions):
        self.field_parts['snake_of_player'].change_parameters_on_eating(100, 1)
        self.field_parts['food'].to_feed()
    
    def event_handler(self, event):
        if event.type == constants.FOOD_PIECE_NEED_EVENT:
            self.field_parts['food'].event_handler(event)
        elif event.type == constants.FOOD_PIECE_EATEN_EVENT:
            self.field_parts['food'].event_handler(event)
            self.field_parts['snake_of_player'].event_handler(event)