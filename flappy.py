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
    global FPSCLOCK, DISPLAYSURF, POPULATION
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH,WINDOWHEIGHT))
    pygame.display.set_caption('Flappy Birds Neuroevolution')

    BACKGROUND = pygame.image.load(BACKGROUNDS_LIST[0])

    BIRDS_WINGS_STATE = UP

    image = pygame.image.load(PLAYERS_DICT[RED][UP])
    for i in range(POPULATION_SIZE):
        POPULATION.append({
            'number': i,
            'image': image,
            'rect': pygame.Rect((WINDOWWIDTH-image.get_width())/2,\
            (WINDOWHEIGHT-image.get_height())/2,image.get_width(),image.get_height()),
            'alive': True,
            'velocity': 1
        })

    pipe_down = pygame.image.load(PIPES_LIST[1])
    pipe_up = pygame.transform.rotate(pipe_down, 180)
    for i in range(PIPESSPAWNED):
        random_y = random.randint(-pipe_up.get_height()/2,-15)
        PIPES.append({
            'image_up': pipe_up,
            'image_down': pipe_down,
            'up_rect': pygame.Rect(WINDOWWIDTH + i * SPACEBETWEENPIPES,\
            random_y,  pipe_up.get_width(), pipe_up.get_height()),
            'down_rect': pygame.Rect(WINDOWWIDTH + i * SPACEBETWEENPIPES,\
            random_y+pipe_up.get_height()+PIPEGAPSIZE,  pipe_up.get_width(),\
            pipe_up.get_height())
        })

    while True:
        DISPLAYSURF.blit(BACKGROUND,(0,0))
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    POPULATION[0]['velocity']-=9

        BIRDS_WINGS_STATE = changeBirdsWingsState(BIRDS_WINGS_STATE)

        animateBirds(BIRDS_WINGS_STATE)

        for i in range(PIPESSPAWNED):
            DISPLAYSURF.blit(PIPES[i]['image_down'],(PIPES[i]['down_rect'].x,PIPES[i]['down_rect'].y))
            DISPLAYSURF.blit(PIPES[i]['image_up'],(PIPES[i]['up_rect'].x,PIPES[i]['up_rect'].y))
            if PIPES[i]['up_rect'].x<=-pipe_up.get_width():
                PIPES[i]['up_rect'].x= PIPES[(i+PIPESSPAWNED-1)%PIPESSPAWNED]['up_rect'].x+SPACEBETWEENPIPES
                PIPES[i]['down_rect'].x= PIPES[(i+PIPESSPAWNED-1)%PIPESSPAWNED]['down_rect'].x+SPACEBETWEENPIPES
                random_y = random.randint(-pipe_up.get_height()/2,-15)
                PIPES[i]['up_rect'].y=random_y
                PIPES[i]['down_rect'].y=random_y+pipe_up.get_height()+PIPEGAPSIZE
            PIPES[i]['up_rect'].x -= PIPEVELOCITY
            PIPES[i]['down_rect'].x -= PIPEVELOCITY


        for bird in POPULATION:
            bird_rect = bird['rect']
            for pipe in PIPES:
                pipe_up_rect = pipe['up_rect']
                pipe_down_rect = pipe['down_rect']
                if bird_rect.colliderect(pipe_up_rect) or bird_rect.colliderect(pipe_down_rect):
                    print('Collision.')

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
        bird['velocity']+=GRAVITY
        if ((bird['rect'].y+bird['velocity'])<=WINDOWHEIGHT) and (bird['velocity']<10):
            bird['rect'].y+=bird['velocity']



if __name__=='__main__':
    main()
