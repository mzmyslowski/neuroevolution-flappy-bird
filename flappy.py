import random, pygame, sys, neat
from pygame.locals import *

FPS = 30
WINDOWWIDTH = 288
WINDOWHEIGHT = 512
PIPESSPAWNED = 4
POPULATION_SIZE = 50
SPACEBETWEENPIPES = 200
PIPEGAPSIZE  = 100
PIPESVELOCITY = 3
JUMP_VELOCITY = -1
GRAVITY = 1
NUMBEROFINPUTS = 3
NUMBEROFOUTPUTS = 1
RED, BLUE, YELLOW = 'red', 'blue', 'yellow'
BIRDS_COLORS = (RED, BLUE, YELLOW)
UP, MID, DOWN = ('up', 'mid', 'down')
WINGS_DIRECTIONS = (UP, MID, DOWN)
POPULATION = pygame.sprite.Group()
PIPES = pygame.sprite.Group()
epochs_count=0

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

    alive_count = 0

    def __init__(self, image_path, genome):
        super().__init__()
        Bird.alive_count+=1
        self.image = pygame.image.load(image_path).convert()
        self.rect = self.image.get_rect()
        self.rect.x = (WINDOWWIDTH-self.rect.width)/2
        self.rect.y = (WINDOWHEIGHT-self.rect.height)/2
        self.alive = True
        self.velocity = 1
        self.genome = genome
        self.phenotype = neat.Neural_Network(self.genome)
        self.bird_wings_state = UP
        self.passed_pipe = False

    def update(self):
        if self.alive == True:
            self.moveBird()
            self.animateBirdImage()
            self.velocity+=GRAVITY
            self.rect.y+=self.velocity
            if self.rect.colliderect(BASE_RECT):
                self.alive = False
                Bird.alive_count -= 1
            nearest_pipe = Pipe.getNearestPipe(self.rect.x)
            if self.rect.colliderect(nearest_pipe[0].rect) or self.rect.colliderect(nearest_pipe[1].rect):
                self.alive=False
                Bird.alive_count-=1

            '''
            Since bird is not a point (has width)
            we ensure that colliderect fires
            only once per pipe
            '''

            if nearest_pipe[0].rect.x - self.rect.x > SPACEBETWEENPIPES / 2:
                self.passed_pipe=False

            if self.rect.colliderect(nearest_pipe[0].pass_pipe_rect) and self.passed_pipe==False:
                self.passed_pipe=True
                self.genome.increase_fitness()
        else:
            self.rect.x-=PIPESVELOCITY

    def jump(self):
        self.velocity+=JUMP_VELOCITY
        self.rect.y+=JUMP_VELOCITY

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

class Pipe(pygame.sprite.Sprite):
    pipes_count = 0
    last_pipe_y = 0
    last_pipe_x = WINDOWWIDTH - SPACEBETWEENPIPES
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
            Pipe.last_pipe_x += SPACEBETWEENPIPES
            Pipe.last_pipe_y = self.getRandomYForPipe()
            self.rect.y = Pipe.last_pipe_y+self.rect.height+PIPEGAPSIZE

        self.rect.x=Pipe.last_pipe_x

        self.pass_pipe_rect = pygame.Rect(self.rect.x+self.rect.width,0,1,WINDOWHEIGHT)

        if Pipe.pipes_count / 2 % PIPESSPAWNED == 0:
            Pipe.last_pipe_in_row_x = self.rect.x - WINDOWWIDTH - self.rect.width
            Pipe.last_pipe_in_row_y = self.getRandomYForPipe()

    def update(self):
        self.updatePipesCount()
        self.rect.x -= PIPESVELOCITY
        if self.rect.x<=-self.rect.width:
            self.rect.x = Pipe.last_pipe_in_row_x + SPACEBETWEENPIPES
            self.rect.y = Pipe.last_pipe_in_row_y + self.rect.height+PIPEGAPSIZE
            if Pipe.pipes_count % 2 - 1 != 0:
                self.rect.y -= self.rect.height+PIPEGAPSIZE
                Pipe.last_pipe_in_row_x = self.rect.x - SPACEBETWEENPIPES
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
        nearest_pipes=[]
        for pipe in pipes_list:
            if (pipe.rect.x + pipe.rect.width <= nearest_pipe_x and x <= pipe.rect.x + pipe.rect.width) or (pipe.rect.x==nearest_pipe_x):
                # If length of nearest_pipes is eqaul to 2 and
                # above if statement evaluates to True
                # then it means we have 2 more
                # closer pipes (up and down) and
                # we need just them
                if len(nearest_pipes)==2:
                    nearest_pipes=[]
                nearest_pipe_x = pipe.rect.x
                nearest_pipes.append(pipe)
        return nearest_pipes

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

    spawn_birds()
    while True:
        spawn_pipes()
        play()
        epoch()

def spawn_birds():
    for _ in range(POPULATION_SIZE):
        bird = Bird(PLAYERS_DICT[RED][UP],neat.Genome(NUMBEROFINPUTS,NUMBEROFOUTPUTS))
        POPULATION.add(bird)
        neat.Species.assign_genome_to_spieces(bird.genome)

def spawn_pipes():
    PIPES.empty()
    reset_pipe_static_var()
    for _ in range(PIPESSPAWNED):
        PIPES.add(Pipe(DOWN))
        PIPES.add(Pipe(UP))

def epoch():
    len_sum = 0
    #for species in neat.Species.species_list:
    #    len_sum+=len(species)
    #print(len_sum)
    neat.Species.assign_species_representatives()
    print('Representatives assigned.')
    for bird in POPULATION.sprites():
        neat.Species.assign_genome_to_spieces(bird.genome)
    print('Genomes assigned.')
    neat.Species.adjustFitnesses()
    print('Fitnesses adjusted.')
    neat.Species.computeHowManyOffspringToSpawn()
    print('Spawn levels calculated.')
    new_genomes = neat.Species.getNewGenomes(POPULATION_SIZE)
    print('New genomes created.')
    POPULATION.empty()
    for genome in new_genomes:
        POPULATION.add(Bird(PLAYERS_DICT[RED][UP],genome))

def reset_pipe_static_var():
    Pipe.pipes_count = 0
    Pipe.last_pipe_y = 0
    Pipe.last_pipe_x = WINDOWWIDTH - SPACEBETWEENPIPES
    Pipe.last_pipe_in_row_x = 0
    Pipe.last_pipe_in_row_y = 0

def play():
    while True:
        DISPLAYSURF.blit(BACKGROUND,(0,0))
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
        if Bird.alive_count==0:
           return
        POPULATION.update()
        PIPES.update()

        POPULATION.draw(DISPLAYSURF)
        PIPES.draw(DISPLAYSURF)

        FPSCLOCK.tick(FPS)
        pygame.display.flip()

if __name__=='__main__':
    main()
