import pygame
import random
import constants
import usefull_functions


class Food(pygame.sprite.Group):
    def __init__(self, field):
        super().__init__()
        self.field = field
        self.food_images = self.load_food_images()
        self.food_pieces = []
        self.is_hungry = True
        self.set_food_appearing_timer()

    # Загрузка изображений Еды
    def load_food_images(self):
        path = constants.FOOD_SPRITES_PARAMETERS.get('filepath')
        piece_length = constants.FOOD_SPRITES_PARAMETERS.get('piece_length')
        image = pygame.image.load(path)
        food_images = []
        for column_i in range(image.get_width() // piece_length):
            for row_i in range(image.get_height() // piece_length - 5):
                food_images.append(image.subsurface(
                    column_i * piece_length, row_i * piece_length, 72, 72))
        return food_images
    
    # from Field.update()
    def update(self):
        if self.is_hungry:
            self.empty()
            self.add(FoodPiece(self))
            self.is_hungry = False
    
    def set_food_appearing_timer(self):
        pygame.time.set_timer(constants.FOOD_PIECE_NEED_EVENT,
                              1000 * constants.FOOD_APPER_SECONDS)
    
    def event_handler(self, event):
        if event.type in (constants.FOOD_PIECE_NEED_EVENT,
                          constants.FOOD_PIECE_EATEN_EVENT):
            self.is_hungry = True


class FoodPiece(pygame.sprite.Sprite):
    def __init__(self, food, parameters={}):
        super().__init__()
        self.food = food
        self.image = self.obtain_image(
            parameters.get('size_inFCcs', constants.Point(3, 3)),
            parameters.get('filename', 'random'))
        self.rect = self.calc_rect()
    
    @property
    def cell_length(self):
        return self.food.field.cell_length
    
    @property
    def field(self):
        return self.food.field
    
    @property
    def snake_of_player(self):
        return self.field.field_parts['snake_of_player']
    
    # Получить изображение Еды
    def obtain_image(self, size_inFCcs, filename):
        if not filename or filename == 'random':
            image = random.choice(tuple(self.food.food_images))
        else:
            image = self.food.food_images[filename]
        scale_size = (self.cell_length * size_inFCcs.x,
                      self.cell_length * size_inFCcs.y)
        image = pygame.transform.scale(image, scale_size)
        usefull_functions.set_colorkey(image)
        return image
        
    def calc_rect(self):
        rect = self.image.get_rect()
        field_size = constants.Point(
            self.field.rect.size).to_FCcs(self.cell_length)
        xy_inFCcs = constants.Point(random.randint(0, field_size.x),
                                    random.randint(0, field_size.y))
        rect.x, rect.y = xy_inFCcs.to_FPcs(self.cell_length).xy
        while rect.collidelist([
              *self.food.sprites(),
              *self.snake_of_player.snake_body_lines,
              self.snake_of_player.snake_head]) != -1:
            xy_inFCcs = constants.Point(random.randint(0, field_size.x),
                                        random.randint(0, field_size.y))
            rect.x, rect.y = xy_inFCcs.to_FPcs(self.cell_length).xy
        return rect
    