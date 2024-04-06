import constants
import pygame


class Block(pygame.sprite.Sprite):
    def __init__(self, image, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.image = image
        self.rect = self.image.get_rect()
        self.group = pygame.sprite.Group()
        
    def draw(self):
        self.group.draw(self.image)
    
    def add(self, sprite):
        self.group.add(sprite)
        
    def copy(self):
        image = self.image.copy()
        rect = self.rect.copy()
        group = self.group.copy()
        block = self.__class__(image)
        block.rect = rect
        block.group = group
        return block


pygame.init()
running = True
screen = pygame.display.set_mode((640, 480))

block3 = Block(pygame.Surface((50, 50)))
block3.image.fill('orange')
block3.rect.topleft = (25, 25)

block2 = Block(pygame.Surface((100, 100)))
block2.image.fill('green')
block2.rect.topleft = (50, 50)
block2.group.add(block3)

block1 = Block(pygame.Surface((200, 200)))
block1.image.fill('white')
block1.rect.topleft = (100, 100)
block1.group.add(block2)
block1.draw()

block11 = block1.copy()
block11.rect.topleft = (300, 200)
block11.group.sprites()[0]




while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            break
    screen.fill('yellow')
    screen.blit(block1.image, block1.rect.topleft)
    screen.blit(block11.image, block11.rect.topleft)
    pygame.display.flip()
pygame.quit()

