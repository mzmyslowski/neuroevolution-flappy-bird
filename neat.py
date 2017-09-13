import random
import numpy as np

class Genome(object):
    innovations = []
    global_innovation_number = 0
    # sensor_units can be found in connection_genes simply using number_of_sensor_units
    # way to output_units can be found following by order fields 'In' and 'Out' in connection_genes
    def __init__(self, number_of_sensor_units, number_of_output_units):
        self.number_of_sensor_units = number_of_sensor_units
        self.number_of_output_units = number_of_output_units
        self.node_genes = self.__create_node_genes()
        self.connection_genes = self.__create_connection_genes()
        self.connection_matrix = self.__create_connection_matrix()

    def __create_node_genes(self):
        node_genes = {
            'Sensor': [],
            'Hidden': [],
            'Output': []
        }
        for i in range(self.number_of_sensor_units):
            node_genes['Sensor'].append(i)
        for i in range(self.number_of_sensor_units,self.number_of_sensor_units+self.number_of_output_units):
            node_genes['Output'].append(i)
        return node_genes

    def __create_connection_genes(self):
        connection_genes = []
        for sensor in self.node_genes['Sensor']:
            for output in self.node_genes['Output']:
                self.increment_innovation_number()
                connection_genes.append({
                    'In': sensor,
                    'Out': output,
                    'Weight': random.gauss(0,1),
                    'State': 'Enabled',
                    'Innovation': Genome.get_innovation_id(sensor, output),
                    'Iterated': False
                })
        return connection_genes

    def __create_connection_matrix(self):
        matrix_dim = self.number_of_sensor_units*self.number_of_output_units+1
        connection_matrix = np.zeros((matrix_dim,matrix_dim))
        for connection in self.connection_genes:
            connection_matrix[connection['In'],connection['Out']]=connection['Innovation']
        return connection_matrix

    @staticmethod
    def get_innovation_id(in, out):
        hasInnovation = False
        innovation_number=-1
        for innovation in Genome.innovations:
            if innovation['In']==in and innovation['Out']==out:
                hasInnovation=True
                innovation_number=innovation['Innovation']
        if hasInnovation==False:
            Genome.global_innovation_number+=1
            innovations.append({
                'In': in,
                'Out': out
                'Innovation': Genome.global_innovation_number
            })
            innovation_number=Genome.global_innovation_number
        return innovation_number


    def mutate_add_connection(self):
        in, out = self.get_random_unconnected_genes()
        self.connection_matrix[in,out] = 1
        self.increment_innovation_number()
        self.connection_genes.append({
            'In': in,
            'Out': out,
            'Weight': random.gauss(0,1),
            'State': 'Enabled',
            'Innovation': get_innovation_id(in,out),
            'Iterated': False
        })

    def mutate_add_node(self):
        in, out = self.get_random_connected_genes()
        weight = -1
        for connection in self.connection_genes:
            if connection['In']=in and connection['Out']==out:
                weight=connection['Weight']
        innovation_number = int(self.connection_matrix[in,out])
        self.connection_genes[innovation_number-1]['State']='Disabled'
        new_connection_matrix = np.zeros((self.connection_matrix.shape[0]+1,self.connection_matrix.shape[1]+1))
        new_connection_matrix[:-1,:-1]=self.connection_matrix

        self.connection_genes.append({
            'In': in,
            'Out': new_connection_matrix.shape[0]-1,
            'Weight': 1,
            'State': 'Enabled',
            'Innovation': Genome.get_innovation_id(in, len(new_connection_matrix)-1),
            'Iterated': False
        })
        new_connection_matrix[self.connection_genes[-1]['In'],]self.connection_genes[-1]['Out']=self.connection_genes[-1]['Innovation']
        self.connection_genes.append({
            'In': new_connection_matrix.shape[0]-1,
            'Out': out,
            'Weight': ,
            'State': 'Enabled',
            'Innovation': Genome.get_innovation_id(new_connection_matrix.shape[0]-1,out),
            'Iterated': False
        })
        new_connection_matrix[self.connection_genes[-1]['In'],self.connection_genes[-1]['Out']]=self.connection_genes[-1]['Innovation']
        self.connection_matrix = new_connection_matrix

    def get_random_unconnected_genes(self):
        connected_indices = np.argwhere(self.connection_matrix==0)
        random_index = np.random.randint(0, connected_indices.shape[0])
        return (connected_indices[random_index][0],connected_indices[random_index][1])

    def get_random_connected_genes(self):
        connected_indices = np.argwhere(self.connection_matrix!=0)
        random_index = np.random.randint(0, connected_indices.shape[0])
        return (connected_indices[random_index][0],connected_indices[random_index][1])


class Offspring(Genome):

    def __init__(self, Parent1, Parent2):
        self.connection_genes = self.__mate(Parent1, Parent2)
        self.number_of_sensor_units = Parent1.number_of_sensor_units
        self.number_of_output_units = Parent1.number_of_output_units
        self.connection_matrix = self.__create_connection_matrix()

    def __mate(self, Parent1, Parent2):
        connection_genes = []
        parent1_connection_genes = Parent1.connection_genes
        parent2_connection_genes = Parent2.connection_genes
        min_length = min([len(parent1_connection_genes),len(parent2_connection_genes)])
        i, j = (0,0)
        while i < min_length and j < min_length:
            # In this situation we either have matching genes or disjoint genes
            if parent1_connection_genes[i]['Innovation']==parent2_connection_genes[j]['Innovation']:
                # Now we are hadnling matching genes, choosing randomly one of them
                random_index = np.random.randint(1, 3)
                if random_index == 1:
                    connection_genes.append(parent1_connection_genes[i])
                elif random_index == 2:
                    connection_genes.append(parent2_connection_genes[i])
                i+=1
                j+=1
            elif parent1_connection_genes[i]['Innovation']<parent2_connection_genes[j]['Innovation']:
                # We are taking disjoint gene from parent1
                connection_genes.append(parent1_connection_genes[i])
                i+=1
            else:
                # We are taking disjoint gene from parent2
                connection_genes.append(parent2_connection_genes[j])
                j+=1
        if i<len(parent1_connection_genes)-1:
            # We have some disjoint and excess genes in Parent1
            connection_genes.extend(parent1_connection_genes[i:len(parent1_connection_genes)])
        if j<len(parent2_connection_genes)-1:
            # We have some disjoint and excess genes in Parent2
            connection_genes.extend(parent2_connection_genes[j:len(parent2_connection_genes)])
        return connection_genes

    def __create_connection_matrix(self):
        max_value = 0
        for connection in self.connection_genes:
            if max(connection['In'],connection['Out'])>max_value:
                max_value = max(connection['In'],connection['Out'])
        matrix_dim = int(max_value+1)
        connection_matrix = np.zeros((matrix_dim,matrix_dim))
        for connection in self.connection_genes:
            connection_matrix[connection['In'],connection['Out']]=connection['Innovation']
        return connection_matrix

class Speciation(object):

    @staticmethod
    def measure_compatibility_distance(Genome1, Genome2, c1, c2, c3, N):
        genome1_connection_genes = Genome1.connection_genes
        genome2_connection_genes = Genome2.connection_genes
        excess = 0
        disjoint = 0
        matching = 0
        weight_difference = 0
        i=0
        j=0
        while i < len(genome1_connection_genes) or j < len(genome2_connection_genes):
            if i<len(genome1_connection_genes) and j<len(genome2_connection_genes):
                # Now we have either matching or disjoint genes
                if genome1_connection_genes[i]['Innovation']<genome2_connection_genes[j]['Innovation']:
                    # We have disjoint genes in genome1
                    disjoint+=1
                    i+=1
                elif genome2_connection_genes[j]['Innovation']<genome1_connection_genes[i]['Innovation']:
                    # We have disjoint genes in genome2
                    disjoint+=1
                    j+=1
                else:
                    # Now we have matching genes
                    weight_difference = (genome1_connection_genes[i]['Weight']-genome2_connection_genes[j]['Weight'])**2
                    matching+=1
                    i+=1
                    j+=1
            else:
                # Now we only have disjoint genes
                excess+=1
                i+=1
                j+=1

        return c1*excess/N + c2*disjoint/N + c3*weight_difference/matching

    @staticmethod
    def compute_adjusted_fitness(organism, species, threshold, c1, c2, c3, N):
        adjusted_fitness = organism.fitness
        denominator = 0
        for other_organism in species:
            denominator = 0 if Speciation.measure_compatibility_distance(organism, other_organism, c1, c2, c3, N) > threshold else 0
        return adjusted_fitness/denominator

class Neural_Network(object):

    @staticmethod
    def modified_sigmoid(x):
        return 1/(1+np.exp(-4.9*x))

    #@staticmethod
    #def forward(x, genome, start_iteration):
    #    output_index = len(x)-1
    #    output = 0
    #    if start_iteration>=output_index:
    #        for connection in genome.connection_genes:
    #            if start_iteration==connection['Out'] and connection['State']=='Enabled':
    #                output+=Neural_Network.forward(x, genome, connection['In'])*connection['Weight']
    #        return Neural_Network.modified_sigmoid(output)
    #    else:
    #        return x[start_iteration]
    @staticmethod
    def forward(input, connection_genes):
        x=input
        x.append(-1)
        output_index=len(x)-1
        output=0
        for connection in connection_genes:
            if connection['Iterated']==False and connection['State']=='Enabled':
                if connection['Out']==output_index:
                    output+=connection['Weight']*x[connection['In']]
                    connection['Iterated']=True
                else:
                    local_output = Neural_Network.compute_neuron(x, connection_genes, connection['Out'])
                    x.append(Neural_Network.modified_sigmoid(local_output))
        return Neural_Network.modified_sigmoid(output)

    @staticmethod
    def compute_neuron(x, connection_genes, output_index):
        output=0
        for connection in connection_genes:
            if connection['Out']==output_index:
                output+=x[connection['In']]*connection['Weight']
                connection['Iterated']=True
        return output


for _ in range(50):
    parent = Genome(2,1)
    parent.mutate_add_node()
    Neural_Network.forward([1,1],parent.connection_genes)
    print(parent.i)
