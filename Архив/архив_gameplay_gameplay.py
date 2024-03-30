import pygame
import random
from itertools import product
from functools import partial
import operator
import constants
import usefull_functions
import gameplay_snake


# GameApp:
    # AppMenu:
        # MainMenu: Menu
            # SettingsMenu: Menu
                # ChangeResolutionMenu: Menu
                # ChangeCellSizeMenu: Menu
    # GamePlay:
        # GamePlaySurface:
            # ScoreInterface
            # Field:
                # Food: Group
                # Snake:
                    # SnakeCell: Group
                        # CellLine: Sprite
            

# game_app.current_process
class GamePlay:
    def __init__(self, game_app):
        self.game_app = game_app
        self.resolution = self.game_app.resolution
        self.cell_length = self.game_app.cell_size
        self.screen = self.game_app.screen
        self.gameplay_surface = GamePlaySurface(self)
    
    # Вызывается из GameApp.main_loop()
    def draw(self):
        self.gameplay_surface.draw()


# Окно (поверхность) игрового процесса
class GamePlaySurface:
    def __init__(self, game_play):
        self.game_play = game_play
        # keys:
            # 'score_size':
                        # 'inFPcs'
            # 'field_size':
                        # 'inFPcs'
                        # 'inFCcs'
        self.interface_parts_sizes = self.get_surface_parts_sizes()
        self.score_interface = ScoreInterface(self)     # Панель подсчёта очков
        self.field = Field(self)                        # Игровое поле Змейки
    
    def get_surface_parts_sizes(self):
        part = constants.SCORE_TO_FIELD_PART
        score_size_inFPcs = usefull_functions.point_floor_div(
            point=self.game_play.resolution,
            operand=part, coords_indices=(0, ))
        field_size_inFPcs = usefull_functions.point_multiply(
            point=usefull_functions.point_floor_div(
                point=self.game_play.resolution,
                operand=part, coords_indices=(0, )),
            operand=part - 1, coords_indices=(0, ))
        field_size_inFCcs = usefull_functions.point_floor_div(
            point=field_size_inFPcs, operand=self.game_play.cell_length)
        surface_parts_sizes = {
            'score_size': {'inFPcs': score_size_inFPcs},
            'field_size': {'inFPcs': field_size_inFPcs,
                           'inFCcs': field_size_inFCcs}}
        return surface_parts_sizes

    def draw(self):
        self.game_play.screen.blit(self.score_interface, (0, 0))
        self.game_play.screen.blit(self.field, (
            self.interface_parts_sizes['score_size']['inFPcs'][0], 0))
        
        
# Панель подсчёта очков
class ScoreInterface:
    def __init__(self, game_play_surface):
        self.game_play_surface = game_play_surface
        self.score_image = pygame.Surface(
            self.game_play_surface.interface_parts_sizes['score_size']['inFPcs'])
        
    def update(self):
        self.score_image.fill('yellow')
        
        
class Field:
    def __init__(self, game_play_surface):
        self.game_play_surface = game_play_surface
        self.field_image = pygame.Surface(
            self.game_play_surface.interface_parts_sizes[
                'field_size']['inFPcs'])
        self.cell_length = self.game_play_surface.game_play.cell_length
        self.food = Food(self)
        self.snake_of_player = gameplay_snake.Snake(self)   # Змейка

    def update(self):
        self.field_image.fill('green')
        


class Food(pygame.sprite.Group):
    def __init__(self, field):
        super().__init__()
        self.field = field
