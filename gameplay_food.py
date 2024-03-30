import pygame
import constants
import random
import usefull_functions
from pathlib import Path


class Food(pygame.sprite.Group):
    def __init__(self, field):
        super().__init__()
        self.field = field
        self.food_images = self.load_food_images()
        self.food_pieces = []
        self.need_food = True

    def load_food_images(self):
        path = Path(constants.FOOD_FOLDER) / 'food-drink-00.png'
        full_image_sprite_length = 72
        full_image = pygame.image.load(path)
        food_images = []
        for row_i in range(full_image.get_height() //
                           full_image_sprite_length - 5):
            for column_i in range(full_image.get_width() //
                                  full_image_sprite_length):
                topleft = usefull_functions.point_multiply(
                    (column_i, row_i), operand=full_image_sprite_length)
                food_images.append(full_image.subsurface(topleft + (72, 72)))
        return food_images
        # path = Path(constants.FOOD_FOLDER)
        # for element in path.iterdir():
        #     if element.is_file():
        #         image = pygame.image.load(element)
        #         usefull_functions.set_colorkey(image)
        #         food_images[element.name] = image
        # return food_images
    
    def update(self):
        if self.need_food:
            self.add(FoodPiece(self))
            self.need_food = False
    
    def to_feed(self):
        self.need_food = True
        self.update()


class FoodPiece(pygame.sprite.Sprite):
    def __init__(self, food, parameters={}):
        super().__init__()
        self.food = food
        self.image = self.obtain_image(parameters.get('filename', 'random'),
                                       parameters.get('size_inFCcs', (3, 3)))
        self.rect = self.calc_rect()
    
    def obtain_image(self, filename, size_inFCcs):
        if not filename or filename == 'random':
            image = random.choice(tuple(self.food.food_images))
        else:
            image = self.food.food_images[filename]
        scale_size = (self.food.field.cell_length * size_inFCcs[0],
                      self.food.field.cell_length * size_inFCcs[1])
        image = pygame.transform.scale(image, scale_size)
        usefull_functions.set_colorkey(image)
        # if not filename or filename == 'random':
        #     image = random.choice(tuple(self.food.food_images.values()))
        # else:
        #     image = self.food.food_images[filename]
        # scale_size = (self.food.field.cell_length * size_inFCcs[0],
        #               self.food.field.cell_length * size_inFCcs[1])
        # image = pygame.transform.scale(image, scale_size)
        # usefull_functions.set_colorkey(image)
        return image
        
    def calc_rect(self):
        rect = self.image.get_rect()
        field_size = self.food.field.field_size['inFCcs']
        cell_length = self.food.field.cell_length
        snake_head = self.food.field.field_parts['snake_of_player'].snake_head
        snake_body_lines = self.food.field.field_parts[
            'snake_of_player'].snake_body_lines
        xy_inFCcs = (random.randint(0, field_size[0]),
                     random.randint(0, field_size[1]))
        rect.x, rect.y = usefull_functions.calc_rect_xy_from_FCcs(
            xy_inFCcs, cell_length)
        while rect.collidelist([*self.food.sprites(), *self.food,
                                *snake_body_lines, snake_head]) != -1:
            xy_inFCcs = (random.randint(0, field_size[0]),
                         random.randint(0, field_size[1]))
            rect.x, rect.y = usefull_functions.calc_rect_xy_from_FCcs(
                xy_inFCcs, cell_length)
        return rect
    