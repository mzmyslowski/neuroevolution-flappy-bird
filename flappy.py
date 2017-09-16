import random, pygame, sys, neat
from pygame.locals import *

FPS = 30
WINDOWWIDTH = 288
WINDOWHEIGHT = 512
PIPESSPAWNED = 4
POPULATION_SIZE = 1
RED, BLUE, YELLOW = ('red', 'blue', 'yellow')
BIRDS_COLORS = (RED, BLUE, YELLOW)
UP, MID, DOWN = ('up', 'mid', 'down')
WINGS_DIRECTIONS = (UP, MID, DOWN)
POPULATION = pygame.sprite.Group()
PIPES = pygame.sprite.Group()

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

class Bird(pygame.sprite.Sprite):

    jump_velocity = -1
    gravity = 1
    alive_count = 0

    def __init__(self, image_path, genome):
        super().__init__()
        Bird.alive_count+=1
        self.image = pygame.image.load(image_path).convert()
        self.rect = self.image.get_rect()
        self.rect.x = (WINDOWWIDTH-self.rect.width)/2
        self.rect.y = (WINDOWHEIGHT-self.rect.height)/2
        self.alive=True
        self.velocity=1
        self.genome = genome
        self.phenotype = neat.Neural_Network(self.genome)
        self.bird_wings_state = UP

    def update(self):
        if self.alive==True:
            self.moveBird()
            self.animateBirdImage()
            self.velocity+=Bird.gravity
            self.rect.y+=self.velocity
            if self.rect.colliderect(BASE_RECT):
                self.alive=False
                Bird.alive_count-=1
            nearest_pipe = Pipe.getNearestPipe(self.rect.x)
            if self.rect.colliderect(nearest_pipe[0].rect) or self.rect.colliderect(nearest_pipe[1].rect):
                self.alive=False
                Bird.alive_count-=1
            if nearest_pipe[0].pass_pipe_rect.x<=self.rect.x:
                self.genome.increase_fitness()
        nearest_pipe = Pipe.getNearestPipe(self.rect.x)

    def jump(self):
        self.velocity+=Bird.jump_velocity
        self.rect.y+=Bird.jump_velocity

    def animateBirdImage(self):
        self.changeBirdsWingsState()
        if self.bird_wings_state == UP:
            self.image = pygame.image.load(PLAYERS_DICT[RED][MID])
        elif self.bird_wings_state == MID:
            self.image = pygame.image.load(PLAYERS_DICT[RED][DOWN])
        elif self.bird_wings_state == DOWN:
            self.image = pygame.image.load(PLAYERS_DICT[RED][UP])

    def changeBirdsWingsState(self):
        if self.bird_wings_state == UP:
            return MID
        elif self.bird_wings_state == MID:
            return DOWN
        elif self.bird_wings_state == DOWN:
            return UP

    def moveBird(self):
        nearest_pipe = Pipe.getNearestPipe(self.rect.x)[0]
        distanceToPipe = Pipe.getDistanceToPipe(self.rect.x, nearest_pipe)
        yOfPipeGap = Pipe.getYOfPipeGap(nearest_pipe)
        probabilityOfJump=self.phenotype.forward([distanceToPipe,yOfPipeGap,self.rect.y])
        if probabilityOfJump[0]>=0.5:
            self.jump()

    def mutateBird(self):
        if random.uniform(0,1)<=0.05:
            self.genome.mutate_add_connection()
        if random.uniform(0,1)<=0.03:
            self.genome.mutate_add_node()
        self.phenotype = neat.Neural_Network(self.genome)


class Pipe(pygame.sprite.Sprite):
    space_between_pipes = 200
    pipe_gap_size  = 100
    pipes_velocity = 3
    pipes_count = 0
    last_pipe_y = 0
    last_pipe_x = WINDOWWIDTH - space_between_pipes
    last_pipe_in_row_x = 0
    last_pipe_in_row_y = 0

    def __init__(self, pipe_type):
        super().__init__()
        self.updatePipesCount()

        self.pipe_type = pipe_type

        self.image = pygame.image.load(PIPES_LIST[1]).convert()
        if pipe_type == UP:
            self.image = pygame.transform.rotate(self.image, 180)

        self.rect = self.image.get_rect()
        self.rect.y = Pipe.last_pipe_y

        if Pipe.pipes_count % 2 - 1 == 0:
            Pipe.last_pipe_x += Pipe.space_between_pipes
            Pipe.last_pipe_y = self.getRandomYForPipe()
            self.rect.y = Pipe.last_pipe_y+self.rect.height+Pipe.pipe_gap_size

        self.rect.x=Pipe.last_pipe_x

        self.pass_pipe_rect = pygame.Rect(self.rect.x+self.rect.width,0,0,WINDOWHEIGHT)

        if Pipe.pipes_count / 2 % PIPESSPAWNED == 0:
            Pipe.last_pipe_in_row_x = self.rect.x - WINDOWWIDTH - self.rect.width
            Pipe.last_pipe_in_row_y = self.getRandomYForPipe()

    def update(self):
        self.updatePipesCount()
        self.rect.x -= Pipe.pipes_velocity
        if self.rect.x<=-self.rect.width:
            self.rect.x = Pipe.last_pipe_in_row_x + Pipe.space_between_pipes
            self.rect.y = Pipe.last_pipe_in_row_y + self.rect.height+Pipe.pipe_gap_size
            if Pipe.pipes_count % 2 - 1 != 0:
                self.rect.y -= self.rect.height+Pipe.pipe_gap_size
                Pipe.last_pipe_in_row_x = self.rect.x - Pipe.space_between_pipes
                Pipe.last_pipe_in_row_y = self.getRandomYForPipe()
        self.pass_pipe_rect.x=self.rect.x+self.rect.width



    def getRandomYForPipe(self):
        return random.randint(-self.rect.height/2,-15)

    def updatePipesCount(self):
        Pipe.pipes_count+=1

    @staticmethod
    def getNearestPipe(x):
        nearest_pipe_x = sys.maxsize
        pipes_list = PIPES.sprites()
        nearest_pipe=[]
        for pipe in pipes_list:
            if (pipe.rect.x + pipe.rect.width <= nearest_pipe_x and x <= pipe.rect.x + pipe.rect.width) or (pipe.rect.x==nearest_pipe_x):
                if len(nearest_pipe)==2:
                    nearest_pipe=[]
                nearest_pipe_x = pipe.rect.x
                nearest_pipe.append(pipe)
        return nearest_pipe

    @staticmethod
    def getDistanceToPipe(x, pipe):
        return pipe.rect.x-x

    @staticmethod
    def getYOfPipeGap(pipe):
        return pipe.rect.height+pipe.rect.y


def main():
    global FPSCLOCK, DISPLAYSURF, BASE_RECT, BACKGROUND, RED_BIRD_IMAGE,PIPE_IMAGE
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH,WINDOWHEIGHT))
    BASE_RECT = pygame.draw.rect(DISPLAYSURF,(0,0,0),(0,WINDOWHEIGHT,WINDOWWIDTH/2,WINDOWHEIGHT/2))
    pygame.display.set_caption('Flappy Birds Neuroevolution')

    BACKGROUND = pygame.image.load(BACKGROUNDS_LIST[0])

    RED_BIRD_IMAGE = pygame.image.load(PLAYERS_DICT[RED][UP])

    PIPE_IMAGE = pygame.image.load(PIPES_LIST[1])

    while True:
        prepare()
        play()

def prepare():
    for _ in range(POPULATION_SIZE):
        POPULATION.add(Bird(PLAYERS_DICT[RED][UP], neat.Genome(3,1)))
    for i in range(PIPESSPAWNED):
        PIPES.add(Pipe(DOWN,))
        PIPES.add(Pipe(UP))


def play():
    while True:
        DISPLAYSURF.blit(BACKGROUND,(0,0))
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

        POPULATION.update()
        PIPES.update()

        POPULATION.draw(DISPLAYSURF)
        PIPES.draw(DISPLAYSURF)

        FPSCLOCK.tick(FPS)
        pygame.display.flip()

if __name__=='__main__':
    main()
