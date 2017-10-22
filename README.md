# Neuroevolution Flappy Bird

Building Flappy Bird in Python using Pygame and implementing NEAT algorithm from the article: http://nn.cs.utexas.edu/downloads/papers/stanley.ec02.pdf. Finally, applying the algorithm to
make the birds learn how to fly through gaps in pipes.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

What things you need to install beforehand:

```
Python 3.5
NumPy
PyGame
```

### Running

In order to see the results of applying NEAT to Flappy Bird:

1. Clone the repository to your local machine:
```
git clone https://github.com/schizoburger/neuroevolution-flappy-bird.git
```
2. Open terminal and navigate to the folder containing the cloned repository
3. Type:
```
python3 flappy.py
```
4. Be patient and enjoy!

## Important to note
Some bird should learn successfully how to fly through gaps in pipes before 30th generation. If it's not the case, please exit the game and start it again.

## Acknowledgments

* Kenneth O. Stanley and Risto Miikkulainen for great paper on NEAT.
* Mat Buckland "AI Techniques for Game Programming" for inspiration for architecture of the neural network used in my implementation
