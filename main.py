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

MENU_BACKGROUND_IMAGE_FILENAME = r'menu_background.jpg'


# GameApp:
    # self.current_process = AppMenu:
        # MainMenu(Menu)
            # SettingsMenu(Menu)
                # ChangeResolutionMenu(Menu)
                # ChangeCellSizeMenu(Menu)
            # gameplay_gameplay.GamePlay


class GameApp:
    def __init__(self, resolution):
        self.resolution = resolution
        self.cell_size = constants.RESOLUTIONS_SIDE_LENGTH[self.resolution][0]
        self.initPyGame()
        
    def initPyGame(self):
        pygame.init()
        # self.developer_events_counter = pygame.USEREVENT
        self.screen = pygame.display.set_mode(self.resolution)
        self.running = True          # Программа работает
        self.game_start = False      # Игра началась
        self.clock = pygame.time.Clock()
        self.processes_stack = []
        self.current_process = AppMenu(self)
        self.main_loop()
        # self.new_snake_dir = False   # У Змеи изменилось направление -> в др.класс

        # self.field = Field(resolution, RESOLUTIONS_SIDE_LENGTH[resolution][0])
        # self.game = Game(self)
    
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
        self.cell_size = constants.RESOLUTIONS_SIDE_LENGTH[self.resolution][0]
        self.screen = pygame.display.set_mode(self.resolution)
        self.current_process = AppMenu(self)
        main_menu = MainMenu(self.current_process, self.current_process)
        settings_menu = SettingsMenu(self.current_process, main_menu)
        self.current_process.set_current_menu(ChangeResolutionMenu(
            self.current_process, settings_menu))
    
    def set_cell_size(self, cell_size):
        self.cell_size = cell_size
        self.current_process = AppMenu(self)
        main_menu = MainMenu(self.current_process, self.current_process)
        settings_menu = SettingsMenu(self.current_process, main_menu)
        self.current_process.set_current_menu(ChangeCellSizeMenu(
            self.current_process, settings_menu))
    
    def quit_app(self):
        self.running = False
        

class AppMenu:
    def __init__(self, game_app):
        self.game_app = game_app
        self.background_image = self.set_background_image(
            MENU_BACKGROUND_IMAGE_FILENAME)
        self.current_menu = MainMenu(self, self)

    def set_background_image(self, filename):
        background_image = pygame.image.load(r'./images/' + filename)
        # Обрезка изображения по размеру экрана
        width, height = background_image.get_size()
        if width >= self.game_app.resolution[0] and height >= self.game_app.resolution[1]:
            return background_image.subsurface(0, 0, *self.game_app.resolution)
        else:
            return pygame.transform.scale_by(
                background_image, 1.3).subsurface(0, 0, *self.game_app.resolution)

    def set_current_menu(self, menu):
        self.current_menu = menu

    def draw(self):
        self.game_app.screen.blit(self.background_image, (0, 0))
        current_menu = self.current_menu
        for button_key in self.current_menu.image_buttons:
            if current_menu != self.current_menu:
                break
            self.current_menu.image_buttons[button_key].draw()
    
    def event_handler(self, event):
        self.current_menu.event_handler(event)


# Набор кнопок одного меню
class Menu:
    def __init__(self, app_menu, parent):
        self.app_menu = app_menu
        self.parent = parent
        self.buttons_names_in_order = []
        self.image_buttons = {}
    
    def add_button(self, button_name, **kwargs):
        self.buttons_names_in_order.append(button_name)
        self.image_buttons[button_name] = image_button_module.ImageButton(
            self, **kwargs)
    
    def calc_buttons_start_coord_y(self):
        buttons_quantity = len(self.image_buttons)
        buttons_block_height = (sum([self.image_buttons[button_key].size[1]
                                     for button_key in self.image_buttons]) +
                                image_button_module.BUTTON_INDENT *
                                (buttons_quantity - 1))
        return (self.app_menu.game_app.resolution[1] -
                buttons_block_height) // 2
    
    def get_previous_button(self, button_order_i):
        previous_button_order_i = button_order_i - 1
        if previous_button_order_i < 0:
            return
        previous_button_name = self.buttons_names_in_order[
            previous_button_order_i]
        return self.image_buttons[previous_button_name]
    
    def set_button_coords(self, button, button_order_i):
        center_point = (self.app_menu.game_app.resolution[0] // 2,
                        self.app_menu.game_app.resolution[1] // 2)
        button_coord_x = center_point[0] - button.size[0] // 2
        previous_button = self.get_previous_button(button_order_i)
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
            for button_name in self.image_buttons:
                self.image_buttons[button_name].events_handler(event)


class MainMenu(Menu):
    def __init__(self, app_menu, parent):
        super().__init__(app_menu, parent)
        self.add_button(
            'button_play', text='P L A Y',
            sound_click_filename=r'mixkit-game-click-1114.wav',
            action={'function_or_method': self.app_menu.game_app.set_current_process,
                    'args': (gameplay_gameplay.GamePlay(self.app_menu.game_app), )})
        self.add_button('button_settings', text='S E T T I N G S',
                        action={'function_or_method': self.app_menu.set_current_menu,
                                'args': (SettingsMenu(self.app_menu, self), )})
        self.add_button('button_quit', text='Q U I T',
                        action={'function_or_method': self.app_menu.game_app.quit_app})
        self.buttons_start_coord_y = self.calc_buttons_start_coord_y()
        for order_i, name in enumerate(self.buttons_names_in_order):
            self.set_button_coords(self.image_buttons[name], order_i)


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
        for i, resolution in enumerate(constants.RESOLUTIONS):    
            self.add_button(f'set_resolution_{i}',
                            text=f'{resolution[0]} x {resolution[1]}',
                            action={'function_or_method': self.app_menu.game_app.change_resolution,
                                    'args': (resolution,)})
        self.add_button('button_back', text='B A C K',
                        action={'function_or_method': self.app_menu.set_current_menu,
                                'args': (self.parent, )})
        self.buttons_start_coord_y = self.calc_buttons_start_coord_y()
        for order_i, name in enumerate(self.buttons_names_in_order):
            self.set_button_coords(self.image_buttons[name], order_i)


class ChangeCellSizeMenu(Menu):
    def __init__(self, app_menu, parent):
        super().__init__(app_menu, parent)
        for i, cell_size in enumerate(constants.RESOLUTIONS_SIDE_LENGTH[
                                       self.app_menu.game_app.resolution]):
            self.add_button(f'set_cell_size_{i}',
                            text=f'{cell_size} x {cell_size}',
                            action={'function_or_method': self.app_menu.game_app.set_cell_size,
                                    'args': (cell_size,)})
        self.add_button('button_back', text='B A C K',
                        action={'function_or_method': self.app_menu.set_current_menu,
                                'args': (self.parent, )})
        self.buttons_start_coord_y = self.calc_buttons_start_coord_y()
        for order_i, name in enumerate(self.buttons_names_in_order):
            self.set_button_coords(self.image_buttons[name], order_i)


if __name__ == '__main__':
    game_app = GameApp(constants.RESOLUTIONS[0])
    
