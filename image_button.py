import pygame
from functools import partial
import usefull_functions


BUTTON_FOCUS_BORDER = 10
BUTTON_THICKNESS_PERCENT = 10
BUTTON_SIZE = (400, 60)
BUTTON_INDENT = BUTTON_SIZE[1] // 2
BUTTON_FONT_SIZE = 40
BUTTON_SOUND_MOTION_FILENAME = r'mixkit-camera-shutter-click-1133.wav'
BUTTON_SOUND_CLICK_FILENAME = r'mixkit-arcade-game-jump-coin-216.wav'
BUTTON_FONT_FILENAME = r'SerpensRegular-7MGE.ttf'


def point_in_rect(rect, point):
    x1, y1, width, height = rect
    x2, y2 = x1 + width, y1 + height
    return (x1 <= point[0] <= x2) and (y1 <= point[1] <= y2)


class ImageButton:  # coords removed
    # kwargs:   action, size, text, font_parameters: dict, fill, border, form,
    #           image_filename, sound_motion_filename, sound_click_filename
    def __init__(self, menu, **kwargs):
        self.menu = menu
        self.action = kwargs.get('action')
        self.coords = None
        self.size = kwargs.get('size', BUTTON_SIZE)
        self.form = kwargs.get('form', 'oval')
        self.colours = {'fill': kwargs.get('fill', 'blue'),
                        'border': kwargs.get('border', 'red')}
        self.sounds = self.load_sounds(
            kwargs.get('sound_motion_filename', BUTTON_SOUND_MOTION_FILENAME),
            kwargs.get('sound_click_filename', BUTTON_SOUND_CLICK_FILENAME))
        self.text = kwargs.get('text')
        self.font = self.load_font(kwargs.get('font_parameters', {}))
        self.status = {'active': True, 'focused': False, 'pushed': False}
        self.delayed_events = {}
        self.image_filename = kwargs.get('image_filename')
        self.image = None
    
    # РАЗМЕРЫ И КООРДИНАТЫ
    def set_button_coords(self, coords):
        self.coords = coords
        self.image = self.draw_image()
    
    # ЗВУК
    def load_sounds(self, sound_motion_filename, sound_click_filename):
        sounds = {}
        sounds['motion'] = pygame.mixer.Sound(
            r'./sounds/' + sound_motion_filename)
        sounds['click'] = pygame.mixer.Sound(
            r'./sounds/' + sound_click_filename)
        return sounds
    
    # ЦВЕТ
    def set_colours(self, **colours):
        for colour_type in colours:
            self.colours[colour_type] = colours[colour_type]
    
    def invert_colour(self, colour):
        if isinstance(colour, (tuple, str)):
            pygame_colour = pygame.color.Color(colour)
        else:
            pygame_colour = colour
        for i in range(3):
            pygame_colour[i] = 255 - pygame_colour[i]
        return pygame_colour
    
    # ШРИФТ
    # {'filename': str, 'size': int, 'colour': Color/(r, g, b)/str}
    def load_font(self, parameters):
        parameters['filename'] = r'./fonts/' + parameters.get(
            'filename', BUTTON_FONT_FILENAME)
        parameters['size'] = parameters.get('size', BUTTON_FONT_SIZE)
        
        parameters['colour'] = parameters.get(
            'colour', self.invert_colour(self.colours['fill']))
        return parameters
    
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
    
    def draw_oval(self, image_size, colour):
        oval_image = pygame.Surface(image_size)
        radius = image_size[1] // 2
        pygame.draw.circle(oval_image, colour, (radius, radius), radius)
        pygame.draw.circle(oval_image, colour,
                           (image_size[0] - radius, radius), radius)
        pygame.draw.rect(oval_image, colour,
                         (radius, 0, image_size[0] - 2 * radius,
                          image_size[1]))
        usefull_functions.set_colorkey(oval_image)
        return oval_image
    
    def draw_focus(self, focus_rect_size):
        focus_image = pygame.Surface(focus_rect_size)
        focus_image.blit(self.draw_oval(focus_rect_size, 'red'), (0, 0))     # Наложить овал
        usefull_functions.set_colorkey(focus_image)
        return focus_image
    
    def draw_button_height_image(self, rect_size):
        button_height_image = pygame.Surface(rect_size)         # поверхность высоты кнопки
        button_height_image.blit(
            self.draw_oval(rect_size, (10, 10, 10)), (0, 0))    # размещение овала на поверхности высоты кнопки
        usefull_functions.set_colorkey(button_height_image)
        return button_height_image
    
    def load_image_from_filename(self, rect_size):
        button_top_image = pygame.image.load(r'./images/' + self.filename)
        button_top_image = pygame.transform.scale(
            button_top_image, rect_size)
        usefull_functions.set_colorkey(button_top_image)
        return button_top_image
    
    def draw_image(self):
        # Последовательность наложения поверхностей: focus, height, button_top
        # Размеры поверхностей
        focus_rect_size = self.size
        top_and_height_image_rect_size = (
            self.size[0] - BUTTON_FOCUS_BORDER * 2,
            self.size[1] - BUTTON_FOCUS_BORDER * 2)
        button_thickness_value = (BUTTON_THICKNESS_PERCENT *    # Высота кнопки
                                  self.size[1] // 100)
        # Координаты поверхностей
        focus_coords = (0, 0)
        height_image_coords = (BUTTON_FOCUS_BORDER, BUTTON_FOCUS_BORDER)
        top_image_coords = height_image_coords if self.status['pushed'] \
            else (BUTTON_FOCUS_BORDER, BUTTON_FOCUS_BORDER -
                  button_thickness_value)
        # Общая поверхность кнопки
        button_surface = pygame.Surface(self.size)
        # Focus
        if self.status['focused']:
            button_surface.blit(self.draw_focus(focus_rect_size),
                                focus_coords)
        # Height
        button_height_image = self.draw_button_height_image(
            top_and_height_image_rect_size)
        button_surface.blit(button_height_image, height_image_coords)
        # Изображение или рисунок поверхности кнопки
        if self.image_filename:
            button_top_image = self.load_image_from_filename(
                top_and_height_image_rect_size)
        elif self.form == 'oval':
            button_top_image = self.draw_oval(top_and_height_image_rect_size,
                                              self.colours['fill'])
        # Рисование текста на передней поверхности кнопки
        text = self.draw_text()
        text_size = text.get_size()
        button_top_image.blit(
            text, ((top_and_height_image_rect_size[0] - text_size[0]) // 2,
                   (top_and_height_image_rect_size[1] - text_size[1]) // 2,
                   *text_size))
        # Размещение передней поверхности кнопки на общей поверхности
        button_surface.blit(button_top_image, top_image_coords)
        usefull_functions.set_colorkey(button_surface)
        return button_surface
    
    def draw_text(self):
        font = pygame.font.Font(self.font['filename'], self.font['size'])
        text = font.render(self.text, True, self.font['colour'])
        return text
    
    # СОБЫТИЯ    
    # Изменение статусов кнопки
    def change_status(self, status_type, status_value):
        self.status[status_type] = status_value
    
    # Обработчики событий
    def events_handler(self, event):
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
