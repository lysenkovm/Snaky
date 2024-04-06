import pygame
from functools import partial
import usefull_functions
import constants


class ImageButton(pygame.sprite.Sprite):  # coords removed
    # kwargs:   name, action, size, text, font_parameters: dict, fill, border, form,
    #           image_filepath, sound_motion_filepath, sound_click_filepath
    # name
    # +action_parameters:   +function_or_method, args, kwargs
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
            # kwargs
        action_parameters = kwargs.get('action_parameters')
        self.action = action_parameters.get('function_or_method')
        self.action_args = action_parameters.get('args', ())
        self.action_kwargs = action_parameters.get('kwargs', {})
        
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
        
        # sounds_parameters:
            # motion_filepath
            # click_filepath
        sounds_parameters = kwargs.get('sounds_parameters',
                                       constants.BUTTON_SOUNDS_PARAMETERS)
        self.sounds = self.load_sounds(
            sounds_parameters.get(
                'motion_filepath',
                constants.BUTTON_SOUNDS_PARAMETERS['motion_filepath']),
            sounds_parameters.get(
                'click_filepath',
                constants.BUTTON_SOUNDS_PARAMETERS['click_filepath']))
        
        # Создание изображения
        self.images = self.create_images()
        # OTHER parameters
        self.status = {'active': True, 'focused': False, 'pushed': False}
        self._xy = constants.FPcs(0, 0)
        self.delayed_events = {}
        # @properties:
            # image
            # rect
            # xy
            # button_indent
            # thickness_shift
            # text_sprite
    
    # ИЗОБРАЖЕНИЕ КНОПКИ
    def create_images(self):
        # focus не входит в высоту кнопки, а высота - входит
        # focus рисуется классом меню
        # Пока без отступа (border)
        
        button_images = {'pushed': pygame.Surface(self.size.xy),
                         'notpushed': pygame.Surface(self.size.xy)}
        # Последовательность наложения поверхностей: height, button_top
        # Размеры поверхностей: нажатой кнопки и высоты
        top_rects = {}
        top_rects['notpushed'] = pygame.Rect(
            0, 0, *(self.size - (0, self.thickness_shift)).xy)
        top_rects['pushed'] = top_rects['notpushed'].copy().move(
            0, self.thickness_shift)
        # Thickeness
        pygame.draw.rect(
            button_images['notpushed'], self.thickness_colour,
            top_rects['pushed'], border_radius=top_rects['pushed'].h // 2)
        # Изображение или рисунок поверхности кнопки с текстом
        if self.image_filepath:
            pass
        elif self.form == 'oval':
            pygame.draw.rect(
                button_images['notpushed'], self.fill_colour,
                top_rects['notpushed'], border_radius=top_rects['notpushed'].h // 2)
            pygame.draw.rect(
                button_images['pushed'], self.fill_colour,
                top_rects['pushed'], border_radius=top_rects['pushed'].h // 2)
        # Рисование текста на top_image кнопки
        text_sprite = self.text_sprite
        for key in button_images:
            usefull_functions.set_colorkey(button_images[key])
            text_sprite.rect.center = top_rects[key].center
            button_images[key].blit(
                self.text_sprite.image, text_sprite.rect)
        return button_images
        
    # Не используется, должен быть переделан
    def load_image_from_filepath(self, rect_size):
        button_top_image = pygame.image.load(r'./images/' + self.filepath)
        button_top_image = pygame.transform.scale(
            button_top_image, rect_size)
        usefull_functions.set_colorkey(button_top_image)
        return button_top_image
    
    # АТРИБУТЫ
    @property
    def thickness_shift(self):
        return self.size.y * self.thickness_percent // 100
    
    @property
    def text_sprite(self):
        font = pygame.font.Font(self.font_parameters['filepath'],
                                self.font_parameters['size'])
        text_sprite = pygame.sprite.Sprite()
        text_sprite.image = font.render(
            self.text, True, self.font_parameters['colour'])
        text_sprite.rect = text_sprite.image.get_rect()
        return text_sprite
    
    @property
    def image(self):
        if self.status['pushed']:
            return self.images['pushed']
        else:
            return self.images['notpushed']
    
    @property
    def rect(self):
        rect = self.image.get_rect()
        rect.topleft = self.xy.xy
        return rect
    
    @property
    def xy(self):
        return self._xy
    
    @xy.setter
    def xy(self, xy_inFPcs):
        self._xy = xy_inFPcs

    @property       # Для определения координат в 'rect'
    def button_indent(self):
        return self.size.y * self.menu.buttons_indent_percent // 100
    
    # ЗВУК
    def load_sounds(self, sound_motion_filepath, sound_click_filepath):
        sounds = {}
        sounds['motion'] = pygame.mixer.Sound(sound_motion_filepath)
        sounds['click'] = pygame.mixer.Sound(sound_click_filepath)
        return sounds
    
    # СОБЫТИЯ    
    # Обработчики событий
    def event_handler(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.on_motion(event)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            self.on_click(event)
    
    def on_motion(self, event):
        if self.rect.collidepoint(event.pos):
            if (self.status['active'] and not (self.status['focused']
                                               or self.status['pushed'])):
                self.focus(True)
        else:
            self.focus(False)
    
    def on_click(self, event):
        if self.status['focused'] and self.rect.collidepoint(event.pos):
            self.push(True)
            
    def push(self, status):
        self.status['pushed'] = status
        if self.status['pushed']:
            self.sounds['click'].play(0)
            self.delayed_events['BUTTON_UP'] = {
                'delay': 150,
                'start_time': pygame.time.get_ticks(),
                'function_or_method': partial(self.push, status=False)}
            # нужно, чтобы выполнить действие только после анимации
            self.delayed_events['BUTTON_PUSH'] = {
                'delay': 200,
                'start_time': pygame.time.get_ticks(),
                'function_or_method': self.make_action}
    
    def make_action(self):
        if self.action:
            self.action(*self.action_args, **self.action_kwargs)
    
    def focus(self, status):
        self.status['focused'] = status
        if self.status['focused']:
            self.sounds['motion'].play(0)

    # Отложенные события
    def update(self):
        if self.delayed_events:
            event_names = tuple(self.delayed_events.keys())
            for event_name in event_names:
                current_time = pygame.time.get_ticks()
                start_time = self.delayed_events[event_name]['start_time']
                delay = self.delayed_events[event_name]['delay']
                if current_time - start_time >= delay:
                    self.delayed_events.pop(event_name)['function_or_method']()
