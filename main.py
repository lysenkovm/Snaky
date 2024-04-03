from pathlib import Path
import pygame
import constants
import image_button as image_button_module
import gameplay_gameplay
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
        self.cell_length = self.resolution.cell_length(0)
        # self.developer_events_counter = pygame.USEREVENT
        # self.processes_stack = []
        self.screen = pygame.display.set_mode(self.resolution.xy)
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
            self.current_process.draw()
            self.clock.tick(constants.FPS)
            pygame.display.flip()
        #test<
        file.close()
        #test>
        pygame.quit()
    
    def set_current_process(self, next_process, kill_previous=False):
        if not kill_previous:
            self.processes_stack.append(self.current_process)
        self.current_process = next_process
    
    def change_resolution(self, resolution):
        self.resolution = resolution
        self.cell_length = self.resolution.cell_length(0)
        self.screen = pygame.display.set_mode(self.resolution.xy)
        self.current_process = AppMenu(self)
        main_menu = MainMenu(self.current_process, self.current_process)
        settings_menu = SettingsMenu(self.current_process, main_menu)
        self.current_process.set_current_menu(ChangeResolutionMenu(
            self.current_process, settings_menu))
    
    def set_cell_size(self, cell_length):
        self.cell_length = cell_length
        self.current_process = AppMenu(self)
        main_menu = MainMenu(self.current_process, self.current_process)
        settings_menu = SettingsMenu(self.current_process, main_menu)
        self.current_process.set_current_menu(ChangeCellSizeMenu(
            self.current_process, settings_menu))
    
    def quit_app(self):
        self.running = False
        
# GameApp
    # AppMenu
        # Menu
# Управление Меню Приложения
class AppMenu:
    def __init__(self, game_app):
        self.game_app = game_app
        self.background_image = self.load_background_image(
            constants.MENU_BACKGROUND_IMAGE_PATH)
        self.current_menu = MainMenu(self, self)

    # Инициализация
    def load_background_image(self, filepath):
        background_image = pygame.image.load(filepath)
        width, height = background_image.get_size()
        if width < self.game_app.resolution.x or height < self.game_app.resolution.y:
            return pygame.transform.scale_by(
                background_image, 1.3).subsurface(
                    0, 0, *self.game_app.resolution.xy)
        else:
            return background_image.subsurface(
                0, 0, *self.game_app.resolution.xy)

    # Рисование
    def draw(self):
        self.game_app.screen.blit(self.background_image, (0, 0))
        current_menu = self.current_menu
        self.current_menu.draw(self.game_app.screen)
    
    # События
    def event_handler(self, event):
        self.current_menu.event_handler(event)
    
    # Изменения
    def set_current_menu(self, menu):
        self.current_menu = menu


# Набор кнопок одного меню
class Menu(pygame.sprite.Group):
    def __init__(self, app_menu, parent):
        super().__init__()
        self.app_menu = app_menu
        self.parent = parent
    
    @property
    def button_group_top_left(self):
        group_wh = constants.FPcs(0, 0)
        for button in self.sprites():
            group_wh += button
    
    def calc_buttons_start_coord_y(self):
        buttons_quantity = len(self.sprites)
        buttons_block_height = sum(
            [button.size[1] for button in self.sprites()]) + \
                (buttons_quantity - 1) * image_button_module.BUTTON_INDENT
        return (self.app_menu.game_app.resolution.y -
                buttons_block_height) // 2
    
    def get_previous_button(self, current_button):
        previous_button_i = self.sprites().index(current_button) - 1
        if previous_button_i < 0:
            return
        return self.sprites()[previous_button_i]
    
    def set_button_rect(self, button, button_order_i):
        center_point = constants.FPcs(
            self.app_menu.game_app.screen.get_rect().center)
        # Topleft кнопки
        button_coord_x = center_point[0] - button.size[0] // 2
        previous_button = self.get_previous_button(button)
        if previous_button is None:
            button_coord_y = self.buttons_start_coord_y
        else:
            previous_button_coord_y = previous_button.coords[1]
            previous_button_size_y = previous_button.size[1]
            button_coord_y = (previous_button_coord_y +
                              previous_button_size_y +
                              image_button_module.BUTTON_INDENT)
        button.set_button_coords((button_coord_x, button_coord_y))
    
    def event_handler(self, event):
        if event.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN):
            for button in self.sprites():
                button.events_handler(event)


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
                name='button_play',
                action_parameters={
                    'function_or_method': self.app_menu.game_app.set_current_process,
                    'args': (gameplay_gameplay.GamePlay(self.app_menu.game_app), )},
                label_parameters={'text': 'P L A Y'},
                sounds_parameters={'click_filepath': r'mixkit-game-click-1114.wav'}))
        self.add(
            image_button_module.ImageButton(
                name='button_settings',
                action_parameters={
                    'function_or_method': self.app_menu.set_current_menu,
                    'args': (SettingsMenu(self.app_menu, self), )},
                label_parameters={'text': 'S E T T I N G S'}))
        self.add(
            image_button_module.ImageButton(
                name='button_quit',
                action_parameters={'function_or_method': self.app_menu.game_app.quit_app},
                label_parameters={'text': 'Q U I T'}))
        self.buttons_start_coord_y = self.calc_buttons_start_coord_y()
        for order_i, button in enumerate(self.sprites()):
            self.set_button_rect(button, order_i)


class SettingsMenu(Menu):
    def __init__(self, app_menu, parent):
        super().__init__(app_menu, parent)
        self.add_button('button_resolution', text='R E S O L U T I O N',
                        action={'function_or_method': self.app_menu.set_current_menu,
                                'args': (ChangeResolutionMenu(self.app_menu, self),)})
        self.add_button('button_cell_size', text='C E L L  S I Z E',
                        action={'function_or_method': self.app_menu.set_current_menu,
                                'args': (ChangeCellSizeMenu(self.app_menu, self),)})
        self.add_button('button_sound_configure', text='S O U N D')
        self.add_button('button_back', text='B A C K',
                        action={'function_or_method': self.app_menu.set_current_menu,
                                'args': (self.parent, )})
        self.buttons_start_coord_y = self.calc_buttons_start_coord_y()
        for order_i, name in enumerate(self.buttons_names_in_order):
            self.set_button_coords(self.image_buttons[name], order_i)


class ChangeResolutionMenu(Menu):
    def __init__(self, app_menu, parent):
        super().__init__(app_menu, parent)
        for resolution in constants.RESOLUTIONS:
            self.add_button(f'set_resolution_{resolution.index}',
                            text=resolution.__str__(),
                            action={'function_or_method': self.app_menu.game_app.change_resolution,
                                    'args': (resolution, )})
        self.add_button('button_back', text='B A C K',
                        action={'function_or_method': self.app_menu.set_current_menu,
                                'args': (self.parent, )})
        self.buttons_start_coord_y = self.calc_buttons_start_coord_y()
        for order_i, name in enumerate(self.buttons_names_in_order):
            self.set_button_coords(self.image_buttons[name], order_i)


class ChangeCellSizeMenu(Menu):
    def __init__(self, app_menu, parent):
        super().__init__(app_menu, parent)
        for i, cell_length in enumerate(
                self.app_menu.game_app.resolution.cell_lengths):
            self.add_button(f'set_cell_size_{i}',
                            text=f'{cell_length} x {cell_length}',
                            action={'function_or_method': self.app_menu.game_app.set_cell_size,
                                    'args': (cell_length,)})
        self.add_button('button_back', text='B A C K',
                        action={'function_or_method': self.app_menu.set_current_menu,
                                'args': (self.parent, )})
        self.buttons_start_coord_y = self.calc_buttons_start_coord_y()
        for order_i, name in enumerate(self.buttons_names_in_order):
            self.set_button_coords(self.image_buttons[name], order_i)


if __name__ == '__main__':
    resolution = constants.RESOLUTIONS(0)
    game_app = GameApp(resolution)
    