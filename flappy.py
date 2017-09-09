import random, pygame, sys
from pygame.locals import *

FPS = 30
WINDOWWIDTH = 288
WINDOWHEIGHT = 512
PIPEGAPSIZE  = 100 # gap between upper and lower part of pipe
SPACEBETWEENPIPES = 200
PIPESSPAWNED = 4
POPULATION_SIZE = 1
GRAVITY = 1
JUMP_VELOCITY = -9
PIPEVELOCITY = 3
RED, BLUE, YELLOW = ('red', 'blue', 'yellow')
BIRDS_COLORS = (RED, BLUE, YELLOW)
UP, MID, DOWN = ('up', 'mid', 'down')
WINGS_DIRECTIONS = (UP, MID, DOWN)
POPULATION = []
PIPES = []

# dictionary of players and their states
PLAYERS_DICT = {
    RED: {
        UP: 'assets/sprites/redbird-upflap.png',
        MID: 'assets/sprites/redbird-midflap.png',
        DOWN: 'assets/sprites/redbird-downflap.png',
    },
    BLUE: {
        UP: 'assets/sprites/bluebird-upflap.png',
        MID: 'assets/sprites/bluebird-midflap.png',
        DOWN: 'assets/sprites/bluebird-downflap.png',
    },
    YELLOW: {
        UP: 'assets/sprites/yellowbird-upflap.png',
        MID: 'assets/sprites/yellowbird-midflap.png',
        DOWN: 'assets/sprites/yellowbird-downflap.png',
    }
}

# list of backgrounds
BACKGROUNDS_LIST = (
    'assets/sprites/background-day.png',
    'assets/sprites/background-night.png',
)

# list of pipes
PIPES_LIST = (
    'assets/sprites/pipe-green.png',
    'assets/sprites/pipe-red.png',
)



def main():
    global FPSCLOCK, DISPLAYSURF, BASE_RECT, BACKGROUND, RED_BIRD_IMAGE,PIPE_DOWN_IMAGE, PIPE_UP_IMAGE
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH,WINDOWHEIGHT))
    BASE_RECT = pygame.draw.rect(DISPLAYSURF,(0,0,0),(0,WINDOWHEIGHT,WINDOWWIDTH/2,WINDOWHEIGHT/2))
    pygame.display.set_caption('Flappy Birds Neuroevolution')

    BACKGROUND = pygame.image.load(BACKGROUNDS_LIST[0])

    RED_BIRD_IMAGE = pygame.image.load(PLAYERS_DICT[RED][UP])

    PIPE_DOWN_IMAGE = pygame.image.load(PIPES_LIST[1])
    PIPE_UP_IMAGE = pygame.transform.rotate(PIPE_DOWN_IMAGE, 180)


    while True:
        prepare()
        play()

def prepare():
    global POPULATION, PIPES
    POPULATION = []
    PIPES = []
    for i in range(POPULATION_SIZE):
        POPULATION.append({
            'number': i,
            'image': RED_BIRD_IMAGE,
            'rect': pygame.Rect((WINDOWWIDTH-RED_BIRD_IMAGE.get_width())/2,\
            (WINDOWHEIGHT-RED_BIRD_IMAGE.get_height())/2,RED_BIRD_IMAGE.get_width(),RED_BIRD_IMAGE.get_height()),
            'alive': True,
            'velocity': 1
        })


    for i in range(PIPESSPAWNED):
        random_y = random.randint(-PIPE_UP_IMAGE.get_height()/2,-15)
        PIPES.append({
            'image_up': PIPE_UP_IMAGE,
            'image_down': PIPE_DOWN_IMAGE,
            'up_rect': pygame.Rect(WINDOWWIDTH + i * SPACEBETWEENPIPES,\
            random_y,  PIPE_UP_IMAGE.get_width(), PIPE_UP_IMAGE.get_height()),
            'down_rect': pygame.Rect(WINDOWWIDTH + i * SPACEBETWEENPIPES,\
            random_y+PIPE_UP_IMAGE.get_height()+PIPEGAPSIZE,  PIPE_UP_IMAGE.get_width(),\
            PIPE_UP_IMAGE.get_height())
        })

def play():
    BIRDS_WINGS_STATE = UP
    SPACE_CLICKED = False
    while True:
        DISPLAYSURF.blit(BACKGROUND,(0,0))
        SPACE_CLICKED=False
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    POPULATION[0]['velocity']+=JUMP_VELOCITY
                    POPULATION[0]['rect'].y+=JUMP_VELOCITY
                    SPACE_CLICKED=True

        BIRDS_WINGS_STATE = changeBirdsWingsState(BIRDS_WINGS_STATE)
        if animateBirds(BIRDS_WINGS_STATE)==True:
            return

        for i in range(PIPESSPAWNED):
            DISPLAYSURF.blit(PIPES[i]['image_down'],(PIPES[i]['down_rect'].x,PIPES[i]['down_rect'].y))
            DISPLAYSURF.blit(PIPES[i]['image_up'],(PIPES[i]['up_rect'].x,PIPES[i]['up_rect'].y))
            if PIPES[i]['up_rect'].x<=-PIPE_UP_IMAGE.get_width():
                PIPES[i]['up_rect'].x= PIPES[(i+PIPESSPAWNED-1)%PIPESSPAWNED]['up_rect'].x+SPACEBETWEENPIPES
                PIPES[i]['down_rect'].x= PIPES[(i+PIPESSPAWNED-1)%PIPESSPAWNED]['down_rect'].x+SPACEBETWEENPIPES
                random_y = random.randint(-PIPE_UP_IMAGE.get_height()/2,-15)
                PIPES[i]['up_rect'].y=random_y
                PIPES[i]['down_rect'].y=random_y+PIPE_UP_IMAGE.get_height()+PIPEGAPSIZE
            PIPES[i]['up_rect'].x -= PIPEVELOCITY
            PIPES[i]['down_rect'].x -= PIPEVELOCITY


        for bird in POPULATION:
            bird_rect = bird['rect']
            for pipe in PIPES:
                PIPE_UP_IMAGE_rect = pipe['up_rect']
                PIPE_DOWN_IMAGE_rect = pipe['down_rect']
                if bird_rect.colliderect(PIPE_UP_IMAGE_rect) or bird_rect.colliderect(PIPE_DOWN_IMAGE_rect):
                    return


        pygame.display.update()
        FPSCLOCK.tick(FPS)

def changeBirdsWingsState(birds_wings_state):
    if birds_wings_state == UP:
        return MID
    elif birds_wings_state == MID:
        return DOWN
    elif birds_wings_state == DOWN:
        return UP

def changeBirdImage(bird, birds_wings_state):
    if birds_wings_state == UP:
        bird['image'] = pygame.image.load(PLAYERS_DICT[RED][MID])
    elif birds_wings_state == MID:
        bird['image'] = pygame.image.load(PLAYERS_DICT[RED][DOWN])
    elif birds_wings_state == DOWN:
        bird['image'] = pygame.image.load(PLAYERS_DICT[RED][UP])

def animateBirds(birds_wings_state):
    for bird in POPULATION:
        changeBirdImage(bird, birds_wings_state)
        DISPLAYSURF.blit(bird['image'],(bird['rect'].x,bird['rect'].y))
        if not (bird['rect'].colliderect(BASE_RECT)):
                bird['velocity']+=GRAVITY
                bird['rect'].y+=bird['velocity']
                return False
        else:
            return True


if __name__=='__main__':
    main()
