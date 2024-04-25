import constants
import usefull_functions
import pygame


class Label(pygame.sprite.Sprite):
    def __init__(self,
                 interface,
                 name, y_position, align, max_length_symbols,
                 font_parameters,
                 start_value='',
                 changeable=False, change_event_type=None,
                 update_value_callable=None):
        super().__init__()
        # Interface
        self.interface = interface
        # Geometry
        self.name = name
        self.y_position = y_position
        self.align = align
        self.max_length_symbols = max_length_symbols
        # Font
        self.font_parameters = font_parameters
        self.font_size = self.calc_font_size()
        # Updating
        self.value = start_value
        self.changeable = changeable
        self.change_event_type = change_event_type
        self.update_value_callable = update_value_callable
        # image, rect
        self.image = self.create_image()
        self.rect = self.calc_rect()
    
    @property
    def indent_pixels(self):
        return self.interface.indent_pixels
    
    @property
    def indents_positions(self):
        return self.interface.indents_positions
    
    def calc_font_size(self):
        # +2 - задел
        fonts_size = (self.interface.rect.w - 2 * self.indent_pixels) // (
            self.max_length_symbols + 2)
        return fonts_size

    def create_image(self):
        font = pygame.font.Font(self.font_parameters['filepath'],
                                self.font_size)
        text_image = font.render(str(self.value), True,
                                 self.font_parameters['colour'])
        return text_image
    
    def calc_rect(self):
        rect = self.image.get_rect()
        rect.y = self.y_position
        if self.align == constants.LEFT:
            rect.left = self.indents_positions[self.align]
        elif self.align == constants.RIGHT:
            rect.right = self.indents_positions[self.align]
        return rect
    
    def event_handler(self, event):
        if self.changeable and event.type == self.change_event_type:
            self.value = self.update_value_callable()
        self.update()

    def update(self):
        self.image = self.create_image()
        self.rect = self.calc_rect()
    
    def draw(self, surface):
        surface.blit(self.image, self.rect)
    