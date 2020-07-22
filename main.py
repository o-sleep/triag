import logging
import math
import os
import random
import sys
import time
import pygame


BLUE  = (201, 226, 255, 255)
RED   = (255, 201, 201, 255)
GREEN = (201, 255, 223, 255)
BLACK = (0, 0, 0, 255)
WHITE = (255, 255, 255, 255)
TRANSPARENT = (255, 255, 255, 0)
ALL_SPRITES = pygame.sprite.Group()
TAGGED_SPRITES = pygame.sprite.Group()
TAG_SPRITES = pygame.sprite.Group()
TRIANGLE_SPRITES = pygame.sprite.Group()
SCORE = {}
HEIGHT = 300
WIDTH = 600
BACKGROUND = "pink room dark.png"
LOOT = None


def coord(centroid, median, aim) -> [(int, int), (int, int), (int, int)]:
    """ Return the coordinates of a triangle based on the origin
    length of a side and aim of where the triangle should point at.
        
    >>> coord((5,5), 5, 90)
    [(10, 5), (1, 3), (1, 7)]
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
        #for key in self.keys_down:
        #    key_map[key]()
        pass


class Triangle(pygame.sprite.Sprite):
    """ The Triangle Class represents the player or computer bot.

    """

    def __init__(self, loc, aim, color, name):
        super().__init__()
        self.side = 50
        self.centroid = (self.side // 2, self.side // 2)
        self.speed = 5
        self.turn = 4
        self.border = 2

        self.color = color
        self.cooldown = 60
        self.cooldown_i = self.cooldown

        self.stats = {
            'fragmented': 0,
            'tagged': 0
        }
        self.name = name
        self.start_locations = {
            1: (30, 60),
            2: (270, 30),
            3: (540, 60),
            4: (540, 90),
            5: (270, 120),
            6: (30, 90),
        }

        if loc == None:
            self.loc = random.choice(list(self.start_locations.values()))
        else:
            self.loc = loc

        if aim == None:
            self.aim = random.randint(1, 360)
        else:
            self.aim = aim

        self.image = pygame.Surface([self.side, self.side], pygame.SRCALPHA)
        #self.image = pygame.Surface([self.side, self.side])
        self.rect = self.image.get_rect(center=self.loc)

        pygame.draw.polygon(self.image, self.color,
            coord(self.centroid, self.side // 3, self.aim), self.border)
        TRIANGLE_SPRITES.add(self)
        ALL_SPRITES.add(self)

    def left(self):
        self.aim += self.turn
        self.aim %= 360
        logging.debug('aim l: {}'
            .format(self.aim))
        self.image.fill(TRANSPARENT)
        pygame.draw.polygon(self.image, self.color,
            coord(self.centroid, self.side // 3, self.aim), self.border)
        
    def right(self):
        self.aim -= self.turn
        self.aim %= 360
        logging.debug('aim r: {}'
            .format(self.aim))
        self.image.fill(TRANSPARENT)
        pygame.draw.polygon(self.image, self.color,
            coord(self.centroid, self.side // 3, self.aim), self.border)
    
    def forward(self):
        x = math.sin(math.radians(self.aim)) * self.speed
        y = math.cos(math.radians(self.aim)) * self.speed
        logging.debug('move forward: {} {} in {}'
            .format(x, y, self.aim))
        if self.rect.x + x + 60 < WIDTH \
            and self.rect.y + y + 60 < HEIGHT \
            and self.rect.x + x > 0 \
            and self.rect.y + y > 0:

            self.rect.move_ip(int(x), int(y))

    def backward(self):
        x = -math.sin(math.radians(self.aim)) * self.speed
        y = -math.cos(math.radians(self.aim)) * self.speed
        logging.debug("move back: {} {} in {}"
            .format(x, y, self.aim))
        if self.rect.x + x + 60 < WIDTH \
            and self.rect.y + y + 60 < HEIGHT \
            and self.rect.x + x > 0 \
            and self.rect.y + y > 0:

            self.rect.move_ip(int(x), int(y))

    def tag(self):
        orient = coord(self.centroid, self.side, self.aim)[0]
        target = (int(self.rect.x + orient[0] * self.rect.x/abs(self.rect.x)),
            int(self.rect.y + orient[1] * self.rect.y/abs(self.rect.y)))
        Tag(target, 5, 5 * self.border, self.color, self.aim, 5, 200, 
            self.name)

    def update(self):
        if self in TAGGED_SPRITES:
            if self.cooldown_i < 1:
                self.respawn()
                self.cooldown_i = self.cooldown
            self.cooldown_i -= 1

    def respawn(self):
        self.kill()
        TRIANGLE_SPRITES.add(self)
        ALL_SPRITES.add(self)
        self.rect.center = random.choice(list(self.start_locations.values()))

class Tag(pygame.sprite.Sprite):
    """ The base logic of how one Triangle will Tag another Triangle.  When
        a Triangle is Tagged, the Tagger gets a point.

    """

    def __init__(self, loc, length, width, color, aim, speed, distance, name):
        super().__init__()

        self.loc = loc
        self.l = length
        self.w = width
        self.color = color
        self.aim = aim
        self.speed = speed
        self.distance = distance
        self.name = name

        self.progress = 0

        self.image = pygame.Surface([length, width], pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=loc)
        pygame.draw.polygon(self.image, color,
            coord((5, 5), 2, aim), 4)
        TAG_SPRITES.add(self)
        ALL_SPRITES.add(self)

    def update(self):
        tagged = pygame.sprite.spritecollide(self, TRIANGLE_SPRITES, False)
        if len(tagged) > 0:
            for sprite in tagged:
                SCORE[self.name] += 1
                sprite.kill()
                TAGGED_SPRITES.add(sprite)
                ALL_SPRITES.add(sprite)

        if self.progress < self.distance:
            x = math.sin(math.radians(self.aim)) * self.speed
            y = math.cos(math.radians(self.aim)) * self.speed

            self.rect.move_ip(int(x), int(y))
            self.progress += self.speed
        else:
            self.kill()
            del self

class Loot(pygame.sprite.Sprite):
    """ A random item that appears in a random location yielding a random
        boost for a Triangle, for a period of time.

    """

    def __init__(self):
        print("Boost")


def _test():
    import doctest
    doctest.testmod(raise_on_error=True, verbose=True, report=True)


def main():
    main_dir = os.path.split(os.path.abspath(__file__))[0]
    data_dir = os.path.join(main_dir, "data")

    logging.info('sdl_version: {}'
        .format(pygame.get_sdl_version()))

    pygame.init()

    surface = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    surface.fill(WHITE)
    background = pygame.image.load(os.path.join(data_dir, BACKGROUND))
    background = background.convert()

    playerOne = Triangle(None, None, BLUE, 'Bjorn')
    playerTwo = Triangle(None, None, RED, 'Chloe')
    playerThree = Triangle(None, None, GREEN, 'Zak')

    global SCORE
    SCORE = { 'Bjorn': 0, 'Chloe': 0, 'Zak': 0 }
    font = pygame.font.SysFont(None, 24)

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
        pygame.K_x: playerTwo.tag,
        pygame.K_t: playerThree.forward,
        pygame.K_g: playerThree.backward,
        pygame.K_h: playerThree.right,
        pygame.K_f: playerThree.left,
        pygame.K_b: playerThree.tag
    }
 
    player_event = PlayerEvent()

    while True:
        clock.tick(60)
        surface.blit(background, (0,0))

        player_event.call_keys_down(key_map)

        for event in pygame.event.get():
            logging.debug('event: {}'
                .format(event))
            player_event.handle(event, key_map)

        bjorn_score = font.render(str(SCORE['Bjorn']), True, BLUE)
        chloe_score = font.render(str(SCORE['Chloe']), True, RED)
        zak_score = font.render(str(SCORE['Zak']), True, GREEN)
        surface.blit(bjorn_score, (540, 260))
        surface.blit(chloe_score, (540, 240))
        surface.blit(zak_score, (540, 220))
        ALL_SPRITES.update()
        TRIANGLE_SPRITES.draw(surface)
        TAG_SPRITES.draw(surface)
        pygame.display.update()


if __name__ == "__main__":
    #logging.basicConfig(level = logging.DEBUG if __debug__ else logging.INFO)
    logging.basicConfig(level = logging.INFO)

    _test()
    main()