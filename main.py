import math
import os
import sys
import time

import pygame

main_dir = os.path.split(os.path.abspath(__file__))[0]
data_dir = os.path.join(main_dir, "data")

BLUE  = (0, 0, 255)
RED   = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

print('sdl_version: {}'.format(pygame.get_sdl_version()))

pygame.init()
surface = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()

surface.fill(WHITE)
background = pygame.image.load(os.path.join(data_dir, 'ancient dice.jpg'))
background = background.convert()


def coord(orig, side, aim) -> [(), (), ()]:
    """ Return the coordinates of a equalateral triangle based on the origin
    length of a side and aim of where the triangle should point at.
        
    >>> coord((5,5), 5, 90)
    [(3, 2), (0, 1), (0, 3)]
    """
    orig = (side // 2, side // 2)

    h = side / 3
    x = int(math.sin(math.radians(aim)) * h)
    y = int(math.cos(math.radians(aim)) * h)
    
    angle3 = 90 - aim - 30
    angle2 = 90 - 60 - angle3

    triangle_side = math.cos(math.radians(30)) * h * 2
    #print('{} {} {}'.format(angle3, angle2, triangle_side))

    x2 = int(math.sin(math.radians(angle2)) * triangle_side)
    y2 = int(math.cos(math.radians(angle2)) * triangle_side)

    x3 = int(math.cos(math.radians(angle3)) * triangle_side)
    y3 = int(math.sin(math.radians(angle3)) * triangle_side)

    a = (orig[0] + x, orig[1] + y)
    b = (orig[0] - x2, orig[1] - y2)
    c = (orig[0] - x3, orig[1] - y3)

    #rint('coord: {} {}, {} {} {}'.format(x, y, a, b, c))

    return [a, b, c]

class Triangle(pygame.sprite.Sprite):
    def __init__(self, loc, aim, color):
        super().__init__()
        self.side = 30
        self.orig = (self.side // 2, self.side // 2)
        self.speed = 10
        self.turn = 5


        self.loc = loc
        self.aim = aim
        self.color = color

        self.image = pygame.Surface([self.side, self.side])
        self.rect = self.image.get_rect(center=loc)

        #self.a = (loc[0], loc[1]-self.side//2)
        #self.b = (loc[0]-self.side//2, loc[1]-self.side//2)
        #self.c = (loc[0]-self.side//2, loc[1])
        #self.coord = [self.a, self.b, self.c]
        self.image.fill(WHITE)
        pygame.draw.polygon(self.image, self.color,
            coord(self.orig, self.side, aim), 1)

    def left(self):
        self.aim += self.turn
        self.aim %= 360
        print('aim l: {}'.format(self.aim))
        self.image.fill(WHITE)
        pygame.draw.polygon(self.image, self.color,
            coord(self.orig, self.side, self.aim), 1)
        

    def right(self):
        self.aim -= self.turn
        self.aim %= 360
        print('aim r: {}'.format(self.aim))
        self.image.fill(WHITE)
        pygame.draw.polygon(self.image, self.color,
            coord(self.orig, self.side, self.aim), 1)
    
    def forward(self):
        x = math.sin(math.radians(self.aim)) * self.speed
        y = math.cos(math.radians(self.aim)) * self.speed
        print('move for: {} {} in {}'.format(x, y, self.aim))
        self.rect.move_ip(x, y)

    def backward(self):
        x = -math.sin(math.radians(self.aim)) * self.speed
        y = -math.cos(math.radians(self.aim)) * self.speed
        print("move back: {} {} in {}".format(x, y, self.aim))
        self.rect.move_ip(x, y)

    def tag(self):
        pass

class PlayerEvent():
    def __init__(self, ):
        self.keys_down = {}

    def handle(self, event, key_map):
        if pygame.QUIT == event.type:
            pygame.quit()
            sys.exit(0)

        elif pygame.KEYDOWN == event.type:
            if event.key in key_map.keys():
                print('found key: {}'.format(event.key))
                self.keys_down[event.key] = True
                key_map[event.key]()

        elif pygame.KEYUP == event.type:
            if event.key in self.keys_down.keys():
                del self.keys_down[event.key]
                
    def call_keys_down(self, key_map):
        for key in self.keys_down:
            key_map[key]()

def _test():
    import doctest
    doctest.testmod(raise_on_error=True, report=True)

def main():
    playerOne = Triangle((30,30), 30, RED)

    key_map = {
        pygame.K_UP: playerOne.forward,
        pygame.K_DOWN: playerOne.backward,
        pygame.K_RIGHT: playerOne.right,
        pygame.K_LEFT: playerOne.left,
        pygame.K_RCTRL: playerOne.tag
    }

    all_sprites = pygame.sprite.Group()
    all_sprites.add(playerOne)
    player_event = PlayerEvent()

    while True:
        clock.tick(60)
        surface.blit(background, (0,0))

        player_event.call_keys_down(key_map)

        for event in pygame.event.get():
            print('Event: {}'.format(event))
            player_event.handle(event, key_map)

        all_sprites.draw(surface)
        pygame.display.update()

if __name__ == "__main__":
    _test()
    main()