import pygame
from functools import partial
import constants
import image_button as image_button_module
from gameplay_modules import gameplay
# import gameplay_modules.gameplay as gameplay
#test<
import sys
file = open('./debugging.txt', 'wt')
sys.stdout = file
# def tracefunc(frame, event, arg, indent=[0]):
#     if event == "call":
#         indent[0] += 2
#         print("-" * indent[0] + "> call function", frame.f_code.co_name)
#     elif event == "return":
#         print("<" + "-" * indent[0], "exit function", frame.f_code.co_name)
#         indent[0] -= 2
#     return tracefunc

# sys.setprofile(tracefunc)
#test>


# GameApp:
    # self.current_process = AppMenu:
        # MainMenu(Menu)
            # SettingsMenu(Menu)
                # ChangeResolutionMenu(Menu)
                # ChangeCellSizeMenu(Menu)
            # gameplay_gameplay.GamePlay


class GameApp:
    def __init__(self, resolution):
        pygame.init()
        self.resolution = resolution  # object
        self.cell_length = self.resolution.cell_lengths[0]
        # self.developer_events_counter = pygame.USEREVENT
        self.processes_stack = []
        self.screen = pygame.display.set_mode(self.resolution.xy.xy)
        self.running = True          # Программа работает
        self.clock = pygame.time.Clock()
        self.current_process = AppMenu(self)
        self.main_loop()
    
    def main_loop(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    break
                else:
                    self.current_process.event_handler(event)
            self.screen.fill('black')
            self.current_process.draw()
            self.clock.tick(constants.FPS)
            pygame.display.flip()
        #test<
        file.close()
        #test>
        pygame.quit()
    
    # Используется для начала игры из меню
    def set_current_process(self, next_process, kill_previous=False):
        if not kill_previous:
            self.processes_stack.append(self.current_process)
        self.current_process = next_process
    
    # Используется для смены разрешения из меню
    def change_resolution(self, resolution):
        self.resolution = resolution
        self.cell_length = self.resolution.cell_length(0)
        self.screen = pygame.display.set_mode(self.resolution.xy.xy)
        self.current_process = AppMenu(self)
        main_menu = MainMenu(self.current_process, self.current_process)
        settings_menu = SettingsMenu(self.current_process, main_menu)
        self.current_process.set_current_menu(ChangeResolutionMenu(
            self.current_process, settings_menu))
    
    # Используется для смены длины ячейки
    def set_cell_size(self, cell_length):
        self.cell_length = cell_length
        self.current_process = AppMenu(self)
        main_menu = MainMenu(self.current_process, self.current_process)
        settings_menu = SettingsMenu(self.current_process, main_menu)
        self.current_process.set_current_menu(ChangeCellSizeMenu(
            self.current_process, settings_menu))
    
    # Используется для выхода из приложения из меню
    def quit_app(self):
        self.running = False
        
# GameApp
    # AppMenu
        # Menu
# Управление Меню Приложения
class AppMenu:  # GameApp.current_process
    def __init__(self, game_app):
        self.game_app = game_app
        self.background_image = self.load_background_image(
            constants.MENU_BACKGROUND_IMAGE_PATH)
        self.current_menu = MainMenu(self, self)

    # ИНИЦИАЛИЗАЦИЯ
    # Загрузка изображения фона Меню
    def load_background_image(self, filepath):
        background_image = pygame.image.load(filepath)
        width, height = background_image.get_size()
        if width < self.game_app.resolution.x or height < self.game_app.resolution.y:
            return pygame.transform.scale_by(
                background_image, 1.3).subsurface(
                    0, 0, *self.game_app.resolution.xy.xy)
        else:
            return background_image.subsurface(
                0, 0, *self.game_app.resolution.xy.xy)

    # Рисование
    def draw(self):  # GameApp.main_loop()
        self.game_app.screen.blit(self.background_image, (0, 0))
        self.current_menu.draw(self.game_app.screen)
    
    # События
    def event_handler(self, event):
        self.current_menu.event_handler(event)
    
    # Изменения
    def set_current_menu(self, menu):
        self.current_menu = menu


# Набор кнопок одного меню
class Menu(pygame.sprite.Group):
    def __init__(self, app_menu, parent,
                 focus_parameters=constants.BUTTON_FOCUS_PARAMETERS):
        super().__init__()
        self.app_menu = app_menu
        self.parent = parent
        self.focus_thickness = focus_parameters['focus_thickness']
        self.focus_colour = focus_parameters['focus_colour']
        self.buttons_indent_percent = constants.BUTTONS_INDENT_PERCENT
        # @properties
            # buttons_group_y
    
    @property
    def buttons_group_y(self):
        group_h = 0
        for button_i in range(len(self.sprites())):
            button = self.sprites()[button_i]
            group_h += button.size.y
            if button_i != len(self.sprites()) - 1:
                group_h += button.size.y * self.buttons_indent_percent // 100
        group_y = (self.app_menu.game_app.resolution.y - group_h) // 2
        return group_y
    
    def set_button_rect(self, button, button_order_i):
        center_point = constants.Point(
            self.app_menu.game_app.screen.get_rect().center)
        # Topleft кнопки
        button.xy.x = center_point.x - button.size.x // 2
        button.xy.y = self.buttons_group_y + button_order_i * (
            button.size.y + button.button_indent)
    
    def draw(self, surface):
        # Обновляет спрайты (кнопки)
        super().update()   # from super-class.update()
        for button in self.sprites():
            if button.status['focused']:
                focus_wh = button.size.copy()   # Point
                focus_wh.x += 2 * self.focus_thickness
                focus_wh.y += self.focus_thickness
                focus_xy = constants.Point(button.rect.topleft)
                focus_xy.x -= self.focus_thickness
                focus_xy.y += button.thickness_shift - self.focus_thickness
                pygame.draw.rect(surface, self.focus_colour,
                                 (*focus_xy.xy, *focus_wh.xy),
                                 border_radius=focus_wh.y // 2)
        super().draw(surface)
                
    def event_handler(self, event):
        if event.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN):
            for button in self.sprites():
                button.event_handler(event)


class MainMenu(Menu):
    # ImageButton-kwargs
    # name, action
    # surface_parameters: size, form, image_filepath
    # colours: fill, border
    # sounds: motion_filepath, click_filepath
    # label: text, font
    def __init__(self, app_menu, parent):
        super().__init__(app_menu, parent)
        self.add(
            image_button_module.ImageButton(
                self,
                name='button_play',
                action_parameters={
                    'callable': self.app_menu.game_app.set_current_process,
                    'callable_args': (partial(gameplay.GamePlay, self.app_menu.game_app), )},
                label_parameters={'text': 'P L A Y'},
                sounds_parameters={
                    'click_filepath': constants.SOUNDS_FOLDER / r'mixkit-game-click-1114.wav'}))
        self.add(
            image_button_module.ImageButton(
                self,
                name='button_settings',
                action_parameters={
                    'callable': self.app_menu.set_current_menu,
                    'args': (SettingsMenu(self.app_menu, self), )},
                label_parameters={'text': 'S E T T I N G S'}))
        self.add(
            image_button_module.ImageButton(
                self,
                name='button_quit',
                action_parameters={'callable': self.app_menu.game_app.quit_app},
                label_parameters={'text': 'Q U I T'}))
        for order_i, button in enumerate(self.sprites()):
            self.set_button_rect(button, order_i)


class SettingsMenu(Menu):
    def __init__(self, app_menu, parent):
        super().__init__(app_menu, parent)
        self.add(
            image_button_module.ImageButton(
                self,
                name='button_resolution',
                action_parameters={'callable': self.app_menu.set_current_menu,
                                   'args': (ChangeResolutionMenu(self.app_menu, self),)},
                label_parameters={'text': 'R E S O L U T I O N'}))
        self.add(
            image_button_module.ImageButton(
                self,
                name='button_cell_size',
                action_parameters={'callable': self.app_menu.set_current_menu,
                                   'args': (ChangeCellSizeMenu(self.app_menu, self),)},
                label_parameters={'text': 'C E L L  S I Z E'}))
        # Изменить на отключение, включение звука
        self.add(
            image_button_module.ImageButton(
                self,
                name='button_sound_configure',
                action_parameters={'callable': min,
                                   'args': (5, 6, )},
                label_parameters={'text': 'S O U N D'}))
        self.add(
            image_button_module.ImageButton(
                self,
                name='button_back',
                action_parameters={'callable': self.app_menu.set_current_menu,
                                   'args': (self.parent, )},
                label_parameters={'text': 'B A C K'}))
        for order_i, button in enumerate(self.sprites()):
            self.set_button_rect(button, order_i)


class ChangeResolutionMenu(Menu):
    def __init__(self, app_menu, parent):
        super().__init__(app_menu, parent)
        for resolution in constants.RESOLUTIONS:
            self.add(
                image_button_module.ImageButton(
                    self,
                    name=f'set_resolution_{resolution.index}',
                    action_parameters={
                        'callable': self.app_menu.game_app.change_resolution,
                        'args': (resolution, )},
                    label_parameters={'text': resolution.__str__()}))
        self.add(
            image_button_module.ImageButton(
                self,
                name='button_back',
                action_parameters={
                    'callable': self.app_menu.set_current_menu,
                    'args': (self.parent, )},
                label_parameters={'text': 'B A C K'}))
        for order_i, button in enumerate(self.sprites()):
            self.set_button_rect(button, order_i)


class ChangeCellSizeMenu(Menu):
    def __init__(self, app_menu, parent):
        super().__init__(app_menu, parent)
        for i, cell_length in enumerate(
                self.app_menu.game_app.resolution.cell_lengths):
            self.add(
                image_button_module.ImageButton(
                    self,
                    name=f'set_cell_size_{i}',
                    action_parameters={'callable': self.app_menu.game_app.set_cell_size,
                                       'args': (cell_length,)},
                    label_parameters={'text': f'{cell_length} x {cell_length}'}))
        self.add(
            image_button_module.ImageButton(
                self,
                name='button_back',
                action_parameters={
                    'callable': self.app_menu.set_current_menu,
                    'args': (self.parent, )},
                label_parameters={'text': 'B A C K'}))
        for order_i, button in enumerate(self.sprites()):
            self.set_button_rect(button, order_i)


if __name__ == '__main__':
    resolution = constants.RESOLUTIONS(0)
    game_app = GameApp(resolution)
    