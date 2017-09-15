import random, pygame, sys, neat
from pygame.locals import *

FPS = 30
WINDOWWIDTH = 288
WINDOWHEIGHT = 512
PIPEGAPSIZE  = 100 # gap between upper and lower part of pipe
SPACEBETWEENPIPES = 200
PIPESSPAWNED = 4
POPULATION_SIZE = 1
GRAVITY = 1
#JUMP_VELOCITY = -9
JUMP_VELOCITY = -1
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

    for i in range(POPULATION_SIZE):
        POPULATION.append({
            'number': i,
            'image': RED_BIRD_IMAGE,
            'rect': pygame.Rect((WINDOWWIDTH-RED_BIRD_IMAGE.get_width())/2,\
            (WINDOWHEIGHT-RED_BIRD_IMAGE.get_height())/2,RED_BIRD_IMAGE.get_width(),RED_BIRD_IMAGE.get_height()),
            'alive': True,
            'velocity': 1,
            'genome': neat.Genome(3,1)
        })

    while True:
        prepare()
        play()

def prepare():
    global PIPES
    PIPES = []

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
    while True:
        DISPLAYSURF.blit(BACKGROUND,(0,0))
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    POPULATION[0]['velocity']+=JUMP_VELOCITY
                    POPULATION[0]['rect'].y+=JUMP_VELOCITY

        moveBirds()

        BIRDS_WINGS_STATE = changeBirdsWingsState(BIRDS_WINGS_STATE)

        if animateBirds(BIRDS_WINGS_STATE)==False:
            return

        animatePipes()

        if doesBirdCollide()==True:
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
                return True
        else:
            return False

def moveBirds():
    count=0
    for bird in POPULATION:
        nearest_pipe = getNearestPipe(bird)
        #print(getDistanceToPipe(bird,nearest_pipe),getYOfPipeGap(nearest_pipe),bird['rect'].y)
        #for connection in bird['genome'].connection_genes:
        #    print(connection['Weight'])
        probabilityOfJump=neat.Neural_Network.forward([getDistanceToPipe(bird,nearest_pipe),getYOfPipeGap(nearest_pipe),bird['rect'].y],bird['genome'].connection_genes)
        #print(probabilityOfJump)
        if probabilityOfJump>=0.5:
            jump(bird)

def mutateBirds():
    for bird in POPULATION:
        if random.uniform(0,1)<=0.05:
            bird['genome'].mutate_add_connection()
        if random.uniform(0,1)<=0.03:
            bird['genome'].mutate_add_node()

def jump(bird):
    bird['velocity']+=JUMP_VELOCITY
    bird['rect'].y+=JUMP_VELOCITY

def animatePipes():
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

def doesBirdCollide():
    collide=False
    for bird in POPULATION:
        bird_rect = bird['rect']
        for pipe in PIPES:
            if bird_rect.colliderect(pipe['up_rect']) or bird_rect.colliderect(pipe['down_rect']):
                collide=True
    return collide

def getNearestPipe(bird):
    nearest_pipe_x = sys.maxsize
    nearest_pipe=PIPES[0]
    for pipe in PIPES:
        if pipe['up_rect'].x + pipe['up_rect'].width < nearest_pipe_x and bird['rect'].x < pipe['up_rect'].x + pipe['up_rect'].width:
            nearest_pipe_x = pipe['up_rect'].x
            nearest_pipe=pipe
    return nearest_pipe

def getDistanceToPipe(bird, pipe):
    return pipe['up_rect'].x-bird['rect'].x

def getYOfPipeGap(pipe):
    return pipe['up_rect'].height+pipe['up_rect'].y


if __name__=='__main__':
    main()
