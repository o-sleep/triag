import logging
import math
import os
import sys
import time
import pygame


BLUE  = (0, 0, 255, 255)
RED   = (255, 0, 0, 255)
GREEN = (0, 255, 0, 255)
BLACK = (0, 0, 0, 255)
WHITE = (255, 255, 255, 255)
TRANSPARENT = (255, 255, 255, 0)
ALL_SPRITES = None
TAGGED_SPRITES = None


def coord(centroid, median, aim) -> [(int, int), (int, int), (int, int)]:
    """ Return the coordinates of a equalateral triangle based on the origin
    length of a side and aim of where the triangle should point at.
        
    #>>> coord((5,5), 5, 90)
    #[(3, 2), (0, 1), (0, 3)]
    """
    # "Triangle", with title case, refers to the triangle this function returns
    # the vertices for.

    # coord() is using cartesian coordinates but with the assumption that the
    # vertical axis (i.e. y) is flipped and offset by centroid since pygame
    # puts (0,0) in the upperleft hand corner.

    # h is our hypoteneuse between the origin and the point on Triangle
    # closest to the direction we are aiming at.
    h = median

    # The directional vertex.  It's the closest vertex in the
    # direction of aim degrees (given y is inverted).
    x1 = int(math.sin(math.radians(aim)) * h)
    y1 = int(math.cos(math.radians(aim)) * h)
    
    # We are creating an equalateral triangle, we can assume all corners
    # are 60 deg.  Another triangle bounded by h, (x1, x2), the centroid,
    # and a line that is perpendicular to the vertical axis helps us find the
    # vertices of the Triangle.
    
    # This was necessary to find the directional vertex.  To find the other
    # vertices of the equalateral Triangle, we are subtracting the known
    # angles from 180, the sum of all angles in a triangle.  The remaining
    # angle bounds a right triangle outside of Triangle that share a vertex
    # with Triangle.

    # known angles are:
    #   1. 90 angle where we intersect the origin
    #   2. 30 angle which is half of one angle in an equalateral triangle
    #   3. aim
    angle3 = 180 - 90 - 30 - aim

    # Now that we know this angle, we know that the other right triangle on the
    # other side of Triangle, will share the other vertex of Triangle.  That 
    # angle added to angle3 and the corner of our equalateral Triangle should
    # add up to 90 deg.
    angle2 = 90 - 60 - angle3

    # The triangle_side is the actual length of one side of Triangle.
    triangle_side = int(math.cos(math.radians(30)) * h * 2)
    logging.debug('triside: {} {} {}'
        .format(angle3, angle2, triangle_side))

    # vertex of one side of Triangle
    #x2 = int(math.cos(math.radians(angle2)) * triangle_side)
    #y2 = int(math.sin(math.radians(angle2)) * triangle_side)
    x2 = int(math.sin(math.radians(angle2)) * h)
    y2 = int(math.cos(math.radians(angle2)) * h)

    # vertex of the other side of Triangle
    x3 = int(math.cos(math.radians(angle3)) * h)
    y3 = int(math.sin(math.radians(angle3)) * h)
    #x3 = int(math.cos(math.radians(angle3)) * triangle_side)
    #y3 = int(math.sin(math.radians(angle3)) * triangle_side)

    logging.debug('c: {} x,y: {} {} {}'
        .format(centroid, (x1, y1), (x2, y2), (x3, y3)))
    logging.debug('hypots: {} {} {}'
        .format(math.hypot(x1, y1), math.hypot(x2, y2), math.hypot(x3, y3)))

    #a = (centroid[0] + x1, centroid[1] + y1)
    #b = (centroid[0] + x2, centroid[1] + y2)
    #c = (centroid[0] + x3, centroid[1] + y3)
    a = (centroid[0] + x1, centroid[1] + y1)
    b = (centroid[0] - x2, centroid[1] - y2)
    c = (centroid[0] - x3, centroid[1] - y3)

    logging.debug('coord: {} {} {}'
        .format(a, b, c))
    return [a, b, c]


class Triangle(pygame.sprite.Sprite):
    """ The Triangle Class represents the player or computer bot.

    """

    def __init__(self, loc, aim, color):
        super().__init__()
        self.side = 30
        self.centroid = (self.side // 2, self.side // 2)
        self.speed = 10
        self.turn = 5


        self.loc = loc
        self.aim = aim
        self.color = color

        self.image = pygame.Surface([self.side, self.side], pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=loc)

        pygame.draw.polygon(self.image, self.color,
            coord(self.centroid, self.side // 3, aim), 1)

    def left(self):
        self.aim += self.turn
        self.aim %= 360
        logging.debug('aim l: {}'
            .format(self.aim))
        self.image.fill(TRANSPARENT)
        pygame.draw.polygon(self.image, self.color,
            coord(self.centroid, self.side // 3, self.aim), 1)
        
    def right(self):
        self.aim -= self.turn
        self.aim %= 360
        logging.debug('aim r: {}'
            .format(self.aim))
        self.image.fill(TRANSPARENT)
        pygame.draw.polygon(self.image, self.color,
            coord(self.centroid, self.side // 3, self.aim), 2)
    
    def forward(self):
        x = math.sin(math.radians(self.aim)) * self.speed
        y = math.cos(math.radians(self.aim)) * self.speed
        logging.debug('move for: {} {} in {}'
            .format(x, y, self.aim))
        self.rect.move_ip(x, y)

    def backward(self):
        x = -math.sin(math.radians(self.aim)) * self.speed
        y = -math.cos(math.radians(self.aim)) * self.speed
        logging.debug("move back: {} {} in {}"
            .format(x, y, self.aim))
        self.rect.move_ip(x, y)

    def tag(self):
        orient = coord(self.centroid, self.side // 3, self.aim)[0]
        target = (self.rect.x + orient[0], self.rect.y + orient[1])
        tag = Tag(target, 6, 6, self.color, self.aim, 10, 200)
        ALL_SPRITES.add(tag)

    def update(self):
        pass
        #if self in 


class PlayerEvent():
    def __init__(self, ):
        self.keys_down = {}

    def handle(self, event, key_map):
        if pygame.QUIT == event.type:
            pygame.quit()
            sys.exit(0)

        elif pygame.KEYDOWN == event.type:
            if event.key in key_map.keys():
                logging.debug('found key: {}'
                    .format(event.key))
                self.keys_down[event.key] = True
                key_map[event.key]()

        elif pygame.KEYUP == event.type:
            if event.key in self.keys_down.keys():
                del self.keys_down[event.key]
                
    def call_keys_down(self, key_map):
        for key in self.keys_down:
            key_map[key]()


class Tag(pygame.sprite.Sprite):
    """ The base logic of how one Triangle will Tag another Triangle.  When
        a Triangle is Tagged, the Tagger gets a point.

    """

    def __init__(self, loc, length, width, color, aim, speed, distance):
        super().__init__()

        self.loc = loc
        self.l = length
        self.w = width
        self.color = color
        self.aim = aim
        self.speed = speed
        self.distance = distance

        self.progress = 0

        self.image = pygame.Surface([self.l, self.w], pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=loc)
        pygame.draw.polygon(self.image, color,
            coord((5, 5), 1, 1), 1)

    def update(self):
        logging.debug('tag for: {} until {}/{}'
            .format(self.aim, self.progress, self.distance))
        
        if self.progress < self.distance:
            x = math.sin(math.radians(self.aim)) * self.speed
            y = math.cos(math.radians(self.aim)) * self.speed

            self.rect.move_ip(x, y)
            self.progress += self.speed
        #elif tagged = self.spritecollideany(ALL_SPRITES):
        #    self.kill()
        #    del self
        #    TAGGED_SPRITES.append(tagged)
        else:
            self.kill()
            del self

def _test():
    import doctest
    doctest.testmod(raise_on_error=True, verbose=True, report=True)


def main():
    main_dir = os.path.split(os.path.abspath(__file__))[0]
    data_dir = os.path.join(main_dir, "data")

    logging.info('sdl_version: {}'
        .format(pygame.get_sdl_version()))

    pygame.init()

    surface = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()

    surface.fill(WHITE)
    background = pygame.image.load(os.path.join(data_dir, 'ancient dice.jpg'))
    background = background.convert()

    playerOne = Triangle((30,30), 30, RED)
    playerTwo = Triangle((60,60), 30, BLUE)

    key_map = {
        pygame.K_UP: playerOne.forward,
        pygame.K_DOWN: playerOne.backward,
        pygame.K_RIGHT: playerOne.right,
        pygame.K_LEFT: playerOne.left,
        pygame.K_RCTRL: playerOne.tag,
        pygame.K_w: playerTwo.forward,
        pygame.K_s: playerTwo.backward,
        pygame.K_d: playerTwo.right,
        pygame.K_a: playerTwo.left,
        pygame.K_SPACE: playerTwo.tag
    }
 
    global ALL_SPRITES
    ALL_SPRITES = pygame.sprite.Group()
    ALL_SPRITES.add(playerOne)
    ALL_SPRITES.add(playerTwo)
    player_event = PlayerEvent()

    global TAGGED_SPRITES
    TAGGED_SPRITES = pygame.sprite.Group()

    while True:
        clock.tick(60)
        surface.blit(background, (0,0))

        player_event.call_keys_down(key_map)

        for event in pygame.event.get():
            logging.debug('event: {}'
                .format(event))
            player_event.handle(event, key_map)

        ALL_SPRITES.update()
        ALL_SPRITES.draw(surface)
        pygame.display.update()


if __name__ == "__main__":
    logging.basicConfig(level = logging.DEBUG if __debug__ else logging.INFO)

    _test()
    main()