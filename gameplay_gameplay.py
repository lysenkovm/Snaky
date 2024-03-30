import pygame
import constants
import usefull_functions
import gameplay_snake
import gameplay_food


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
        self.resolution = self.game_app.resolution
        self.cell_length = self.game_app.cell_size
        self.screen = self.game_app.screen
        # keys:
            # 'score_size':
                        # 'inFPcs'
            # 'field_size':
                        # 'inFPcs'
                        # 'inFCcs'
        self.interface_parts_sizes = self.calc_surface_parts_sizes()
        self.interface_parts = {
            'score': ScoreInterface(self,
                                    self.interface_parts_sizes['score_size']),
            'field': Field(self,
                           self.interface_parts_sizes['field_size'])}
        self.add(*self.interface_parts.values())
    
    def calc_surface_parts_sizes(self):
        part = constants.SCORE_TO_FIELD_PART
        score_size_inFPcs = usefull_functions.point_floor_div(
            point=self.resolution, operand=part, coords_indices=(0, ))
        field_size_inFPcs = usefull_functions.point_multiply(
            point=usefull_functions.point_floor_div(
                point=self.resolution, operand=part, coords_indices=(0, )),
            operand=part - 1, coords_indices=(0, ))
        field_size_inFCcs = usefull_functions.point_floor_div(
            point=field_size_inFPcs, operand=self.cell_length)
        surface_parts_sizes = {
            'score_size': {'inFPcs': score_size_inFPcs},
            'field_size': {'inFPcs': field_size_inFPcs,
                           'inFCcs': field_size_inFCcs}}
        return surface_parts_sizes
    
    def draw(self):
        self.update()               # сначала обновление score и field
        super().draw(self.screen)   # затем их прорисовка
    
    def event_handler(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in constants.KEYS_DIRS:
                key_dir = constants.KEYS_DIRS[event.key]
                current_dir = self.get_current_dir()
                if key_dir not in (current_dir,
                                   constants.DIRS_NAMES_OPPOSITES[current_dir]):
                    self.interface_parts['field'].field_parts[
                        'snake_of_player'].change_direction(key_dir)
            
    def get_current_dir(self):
        return self.interface_parts['field'].field_parts[
            'snake_of_player'].direction


# Панель подсчёта очков
class ScoreInterface(pygame.sprite.Sprite):
    def __init__(self, game_play, score_size):
        super().__init__()
        self.game_play = game_play
        self.score_size = score_size
        self.image = pygame.Surface(self.score_size['inFPcs'])
        self.rect = self.calc_rect()
    
    def calc_rect(self):
        rect = self.image.get_rect()
        rect.x, rect.y = (0, 0)
        return rect
        
    def update(self):
        super().update()
        self.image.fill('yellow')
        
        
class Field(pygame.sprite.Sprite):
    def __init__(self, game_play, field_size):
        super().__init__()
        self.game_play = game_play
        self.field_size = field_size
        self.image = pygame.Surface(self.field_size['inFPcs'])
        self.cell_length = self.game_play.cell_length
        self.field_parts = {'snake_of_player': gameplay_snake.Snake(self)}
        self.field_parts['food'] = gameplay_food.Food(self)
        self.rect = self.calc_rect()

    def test_net_points(self):
        for x in range(self.field_size['inFCcs'][0]):
            for y in range(self.field_size['inFCcs'][1]):
                pygame.draw.rect(self.image, 'black', (x * self.cell_length,
                                                       y * self.cell_length, 1, 1))

    def calc_rect(self):
        rect = self.image.get_rect()
        rect.x = self.game_play.interface_parts_sizes['score_size']['inFPcs'][0]
        rect.y = 0
        return rect

    def update(self):       # runs from GamePlay.update()
        self.image.fill('green')
        self.test_net_points()
        # Обновление настоящего спрайта через рисование его частей
        for field_part in self.field_parts.values():
            field_part.update()
            field_part.draw(self.image)
        # Проверка на столкновение Головы с Едой
        if collisions := pygame.sprite.groupcollide(
                self.field_parts['snake_of_player'],
                self.field_parts['food'], False, True):
            self.action_on_food_collision(collisions)
    
    def action_on_food_collision(self, collisions):
        self.field_parts['snake_of_player'].change_parameters_on_eating(100, 1)
        self.field_parts['food'].to_feed()