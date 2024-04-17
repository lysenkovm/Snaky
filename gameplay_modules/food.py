import pygame
import random
import constants
import usefull_functions


class Food(pygame.sprite.Group):
    def __init__(self, field):
        super().__init__()
        self.field = field
        self.path = constants.FOOD_SPRITES_PARAMETERS.get('filepath')
        self.piece_length = constants.FOOD_SPRITES_PARAMETERS.get('piece_length')
        self.piece_size_inFCcs = constants.Point(
            constants.FOOD_SPRITES_PARAMETERS.get('size_inFCcs'))
        self.food_images = self.load_food_images()
        self.food_pieces = []
        self.set_food_appearing_timer()

    # Загрузка изображений Еды
    def load_food_images(self):
        image = pygame.image.load(self.path)
        food_images = []
        for column_i in range(image.get_width() // self.piece_length):
            for row_i in range(image.get_height() // self.piece_length - 5):
                piece_image = image.subsurface(column_i * self.piece_length,
                                               row_i * self.piece_length,
                                               self.piece_length,
                                               self.piece_length)
                food_images.append(piece_image)
        return food_images
    
    # from Field.update()
    # def update(self):
    def food_update(self):
        self.empty()
        self.add(FoodPiece(self))
        self.set_food_disappearing_timer()
    
    def set_food_disappearing_timer(
          self, millis=1000 * constants.FOOD_DISAPPEAR_SECONDS, loops=1):
        pygame.time.set_timer(constants.FOOD_PIECE_NEED_EVENT, millis, loops)
        
    def set_food_appearing_timer(self, loops=1):
        pygame.time.set_timer(constants.FOOD_PIECE_NEED_EVENT,
                              1000 * constants.FOOD_APPEAR_SECONDS, loops)
    
    def event_handler(self, event):
        if event.type == constants.FOOD_PIECE_NEED_EVENT:
            self.food_update()
        elif event.type == constants.FOOD_PIECE_EATEN_EVENT:
            self.set_food_disappearing_timer(millis=0)
            self.set_food_appearing_timer()


class FoodPiece(pygame.sprite.Sprite):
    def __init__(self, food, parameters={}):
        super().__init__()
        self.food = food
        self.image = self.obtain_image(
            parameters.get('size_inFCcs', self.food.piece_size_inFCcs),
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
            image = random.choice(self.food.food_images)
        else:
            image = self.food.food_images[filename]
        scale_size = (size_inFCcs * self.cell_length).xy
        image = pygame.transform.scale(image, scale_size)
        usefull_functions.set_colorkey(image)
        return image
        
    def calc_rect(self):
        
        def calc_random_Point_inFCcs():
            return constants.Point(
                random.randint(
                    0, field_size.x - self.food.piece_size_inFCcs.x),
                random.randint(
                    0, field_size.y - self.food.piece_size_inFCcs.y))
        
        rect = self.image.get_rect()
        field_size = constants.Point(
            self.field.rect.size).to_FCcs(self.cell_length)
        xy_inFCcs = calc_random_Point_inFCcs()
        rect.x, rect.y = xy_inFCcs.to_FPcs(self.cell_length).xy
        while rect.collidelist([*self.food.sprites(),
                                *self.snake_of_player.snake_body_lines,
                                self.snake_of_player.snake_head]) != -1:
            xy_inFCcs = calc_random_Point_inFCcs()
            rect.x, rect.y = xy_inFCcs.to_FPcs(self.cell_length).xy
        return rect
    