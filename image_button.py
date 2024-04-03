import pygame
from functools import partial
import usefull_functions
import constants


class ImageButton(pygame.sprite.Sprite):  # coords removed
    # kwargs:   name, action, size, text, font_parameters: dict, fill, border, form,
    #           image_filepath, sound_motion_filepath, sound_click_filepath
    # name
    # +action_parameters:   +function_or_method, args
    # surface_parameters:   size, form, image_filepath
    # colours:  fill, border
    # sounds:   motion_filepath, click_filepath
    # +label:   +text, font_parameters
    def __init__(self, menu, **kwargs):
        super().__init__()
        self.menu = menu
        self.name = kwargs.get('name', 'unnamed')
        
        # +action_parameters:
            # +function_or_method
            # args
        action_parameters = kwargs.get('action_parameters')
        self.action = action_parameters.get('function_or_method')
        self.action_args = action_parameters.get('args', ())
        
        # +label
            # +text
            # font_parameters
        label_parameters = kwargs.get('label_parameters')
        self.text = label_parameters.get('text')
        # font_parameters
            # filepath
            # size
            # colour
        self.font_parameters = label_parameters.get(
            'font_parameters', constants.BUTTON_FONT_PARAMETERS)
        
        # surface_parameters:
            # size, form
            # image_filepath
        surface_parameters = kwargs.get(
            'surface_parameters', constants.BUTTON_SURFACE_PARAMETERS)
        self.size = constants.FPcs(surface_parameters.get('size'))
        self.thickness_percent = surface_parameters.get('thickness_percent')
        self.form = surface_parameters.get('form')
        self.image_filepath = surface_parameters.get('image_filepath', None)
        
        # colours:
            # fille
            # border
        colours = kwargs.get('colours', constants.BUTTON_COLOURS)
        self.fill_colour = colours.get('fill')
        self.border_colour = colours.get('border')
        self.thickness_colour = colours.get('thickness')
        
        # # focus_parameters
        #     # border
        #     # thickness_percent
        #     # indent
        # focus_parameters = kwargs.get(
        #     'focus_parameters', constants.BUTTON_FOCUS_PARAMETERS)
        
        # sounds_parameters:
            # motion_filepath
            # click_filepath
        sounds_parameters = kwargs.get('sounds_parameters',
                                       constants.BUTTON_SOUNDS_PARAMETERS)
        self.sounds = self.load_sounds(
            sounds_parameters.get('motion_filepath',
                                  constants.BUTTON_SOUND_MOTION_FILEPATH),
            sounds_parameters.get('click_filepath',
                                  constants.BUTTON_SOUND_CLICK_FILEPATH))
        
        # Создание изображения
        self.image = self.create_surface()
        
        # OTHER parameters
        self.status = {'active': True, 'focused': False, 'pushed': False}
        # self.delayed_events = {}
    
    # ИЗОБРАЖЕНИЕ КНОПКИ
    def create_image(self):
        # focus не входит в высоту кнопки, а высота - входит
        # focus рисуется классом меню
        # Пока без отступа (border)
        # Общая поверхность кнопки
        button_surface = pygame.Surface(self.size.xy)
        # Последовательность наложения поверхностей: height, button_top
        
        # Размеры поверхностей
        top_and_thickness_wh = self.size
        thickness_shift = top_and_thickness_wh * self.thickness_percent // 100
        top_wh = thickness_h = top_and_thickness_wh - constants.FPcs(
            0, thickness_shift)
        
        # Координаты поверхностей на кнопке
        top_xy = constants.FPcs(0, 0)
        thickness_xy = constants.FPcs(0, thickness_shift)
        
        # Thickeness
        thickness_image = self.create_thickness_image(
            thickness_h, top_and_thickness_wh)
        button_surface.blit(thickness_image, thickness_xy.xy)
        
        # Изображение или рисунок поверхности кнопки
        if self.image_filepath:
            top_image = self.load_image_from_filepath(
                top_and_thickness_wh.xy)
        elif self.form == 'oval':
            top_image = self.draw_oval(top_and_thickness_wh.xy,
                                       self.fill_colour)
        # Рисование текста на top_image кнопки
        text_surface = self.draw_text()
        text_surface_wh = constants.FPcs(text_surface.get_size())
        top_image.blit(
            top_image, text_surface,
            (*((top_wh - text_surface_wh) // 2).xy, *text_surface_wh.xy))
        
        # Размещение передней поверхности кнопки на общей поверхности
        button_surface.blit(top_image, top_xy.xy)
        usefull_functions.set_colorkey(button_surface)
        return button_surface
    
    def create_thickness_image(self, wh_FPcs):
        thickness_image = pygame.Surface(wh_FPcs.xy)
        if self.form == 'oval':
            thickness_image.blit(
                self.draw_oval(wh_FPcs, self.thickness_colour),
                (0, 0))
        usefull_functions.set_colorkey(thickness_image)
        return thickness_image
    
    def draw_oval(self, wh_FPcs, colour):
        oval_image = pygame.Surface(wh_FPcs.xy)
        pygame.draw.ellipse(oval_image, colour, (0, 0, wh_FPcs.y, wh_FPcs.y))
        pygame.draw.ellipse(oval_image, colour, (
            wh_FPcs.x - wh_FPcs.y, 0, wh_FPcs.y, wh_FPcs.y))
        pygame.draw.rect(oval_image, colour,
                         (wh_FPcs.y // 2, 0,
                          wh_FPcs.x - wh_FPcs.y, wh_FPcs.y))
        usefull_functions.set_colorkey(oval_image)
        return oval_image
    
    # Не используется, должен быть переделан
    def load_image_from_filepath(self, rect_size):
        button_top_image = pygame.image.load(r'./images/' + self.filepath)
        button_top_image = pygame.transform.scale(
            button_top_image, rect_size)
        usefull_functions.set_colorkey(button_top_image)
        return button_top_image
    
    def draw_text(self):
        font = pygame.font.Font(self.font_parameters['filepath'],
                                self.font_parameters['size'])
        text = font.render(self.text, True, self.font_parameters['colour'])
        return text
    
    # РАЗМЕРЫ И КООРДИНАТЫ
    def set_rect(self, coords):
        self.coords = coords
        self.image = self.draw_image()
    
    # ЗВУК
    def load_sounds(self, sound_motion_filepath, sound_click_filepath):
        sounds = {}
        sounds['motion'] = pygame.mixer.Sound(sound_motion_filepath)
        sounds['click'] = pygame.mixer.Sound(sound_click_filepath)
        return sounds
    
    # ЦВЕТ
    def set_colours(self, **colours):
        for colour_type in colours:
            self.colours[colour_type] = colours[colour_type]
    
    # ИЗОБРАЖЕНИЕ КНОПКИ
    def draw(self):
        if self.delayed_events:
            event_names = tuple(self.delayed_events.keys())
            for event_name in event_names:
                current_time = pygame.time.get_ticks()
                start_time = self.delayed_events[event_name]['start_time']
                delay = self.delayed_events[event_name]['delay']
                if current_time - start_time >= delay:
                    self.delayed_events[event_name]['function_or_method']()
                    self.delayed_events.pop(event_name)
        self.menu.app_menu.game_app.screen.blit(
            self.image, (*self.coords, *self.size))
    
    def calc_rect(self):
        return pygame.Rect(*self.coords, *self.size)
    
    # СОБЫТИЯ    
    # Изменение статусов кнопки
    def change_status(self, status_type, status_value):
        self.status[status_type] = status_value
    
    # Обработчики событий
    def event_handler(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.on_motion(event)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            self.on_click(event)
    
    def on_motion(self, event):
        if self.calc_rect().collidepoint(event.pos):
            if (self.status['active'] and not (self.status['focused']
                                               or self.status['pushed'])):
                self.focus(True)
        else:
            self.focus(False)
    
    def on_click(self, event):
        if self.status['focused'] and self.calc_rect().collidepoint(event.pos):
            self.push(True)                         # -> 210
            
    def push(self, status):                         # 208(True) ->, 194(False) ->
        self.change_status('pushed', status)
        self.image = self.draw_image()
        if self.status['pushed']:                   # 194 <-
            self.sounds['click'].play(0)
            self.delayed_events['BUTTON_UP'] = {
                'delay': 150,
                'start_time': pygame.time.get_ticks(),
                'function_or_method': partial(self.push, status=False)}
            self.delayed_events['BUTTON_PUSH'] = {
                'delay': 200,
                'start_time': pygame.time.get_ticks(),
                'function_or_method': self.make_action}
    
    def make_action(self):      # 197 ->
        if self.action:
            self.action['function_or_method'](*self.action.get('args', {}),
                                              **self.action.get('kwargs', {}))
    
    def focus(self, status):
        self.status['focused'] = status
        self.image = self.draw_image()
        if self.status['focused']:
            self.sounds['motion'].play(0)
