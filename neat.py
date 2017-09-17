import random
import numpy as np

class Genome(object):
    # Here we initialize static innovations list
    # and static innovation number
    innovations = []
    global_innovation_number = 0
    global_genomes_id = 0
    add_connection_rate = 0.05
    add_node_rate = 0.03
    change_weight_rate = 0.9
    max_weight_perturbation = 0.5

    def __init__(self, number_of_sensor_units, number_of_output_units):
        Genome.global_genomes_id+=1
        self.genome_id = Genome.global_genomes_id
        self.number_of_sensor_units = number_of_sensor_units
        self.number_of_output_units = number_of_output_units

        self.init_node_genes()
        self.init_connection_genes()

        self.fitness = 1

    def init_node_genes(self):
        self.node_genes = []
        for i in range(self.number_of_sensor_units):
            self.add_node('sensor', i)
        for i in range(self.number_of_sensor_units, self.number_of_sensor_units+self.number_of_output_units):
            self.add_node('output', i)

    def init_connection_genes(self):
        self.connection_genes = []
        dim = self.number_of_sensor_units+self.number_of_output_units
        self.connection_matrix = np.zeros((dim,dim))
        for node1 in self.node_genes:
            if node1['type']=='sensor':
                for node2 in self.node_genes:
                    if node2['type']=='output':
                        self.add_connection(node1['id'], node2['id'])

    def add_node(self, node_type='hidden', node_id=None):
        node_id = len(self.node_genes) if node_id == None else node_id
        new_node = {
            'id': node_id,
            'type': node_type,
            'innovation': Genome.get_innovation_id(gene_type='node',node_id=node_id)
        }
        self.node_genes.append(new_node)
        return new_node

    def add_connection(self, in_node_id, out_node_id, weight=None):
        innovation_number = Genome.get_innovation_id(gene_type='connection', in_node_id=in_node_id, out_node_id=out_node_id)
        new_connection = {
            'in': in_node_id,
            'out': out_node_id,
            'weight': self.getRandomWeight() if weight == None else weight,
            'state': 'enabled',
            'innovation': innovation_number
        }
        self.connection_genes.append(new_connection)
        self.connection_matrix[in_node_id,out_node_id] = innovation_number
        return new_connection

    def mutate_add_node(self):
        if random.uniform(0,1)<=Genome.add_node_rate:
            in_node_id, out_node_id = self.get_random_connected_genes()

            connection_to_split_weight = -1
            for connection in self.connection_genes:
                if connection['in']==in_node_id and connection['out']==out_node_id:
                    connection_to_split_weight=connection['weight']
                    connection['state']= 'disabled'

            # We flag the connection as disabled by -1
            self.connection_matrix[in_node_id,out_node_id]=-1

            new_connection_matrix = np.zeros((self.connection_matrix.shape[0]+1,self.connection_matrix.shape[1]+1))
            new_connection_matrix[:-1,:-1]=self.connection_matrix
            self.connection_matrix = new_connection_matrix

            new_node = self.add_node()
            self.add_connection(in_node_id, new_node['id'], 1)
            self.add_connection(new_node['id'], out_node_id, connection_to_split_weight)

    def mutate_add_connection(self):
        if random.uniform(0,1)<=Genome.add_connection_rate:
            random_unconnected_genes = self.get_random_unconnected_genes()
            # We check if there are some unconnected genes
            if random_unconnected_genes!=None:
                in_node_id, out_node_id = random_unconnected_genes
                self.add_connection(in_node_id, out_node_id)

    def mutate_perturb_weights(self):
        for connection in self.connection_genes:
            if random.uniform(0,1) < Genome.change_weight_rate:
                connection['weight'] += random.uniform(-1,1)*Genome.max_weight_perturbation
            else:
                connection['weight'] = random.uniform(-1,1)

    def get_random_unconnected_genes(self):
        # We get indices of unconnected nodes
        # with an exception that sensor_units
        # can't be treate as out units
        connected_indices = np.argwhere(self.connection_matrix[:,self.number_of_sensor_units:]==0)
        if len(connected_indices)==0:
            return None
        else:
            random_index = np.random.randint(0, connected_indices.shape[0])
            return (connected_indices[random_index][0],connected_indices[random_index][1])

    def get_random_connected_genes(self):
        # -1 is for disabled
        # 0 is for connected
        connected_indices = np.argwhere((self.connection_matrix>0))
        random_index = np.random.randint(0, connected_indices.shape[0])
        return (connected_indices[random_index][0],connected_indices[random_index][1])

    def increase_fitness(self):
        self.fitness+=1

    def getRandomWeight(self):
        return np.random.randn()*np.sqrt(2.0/self.number_of_sensor_units)

    def getMaxValueInConnectionGenesIds(self):
        max_value = 0
        # We look for the highsted id in offspring's connection_genes
        for connection in self.connection_genes:
            current_max_value=max(connection['in'],connection['out'])
            if current_max_value>max_value:
                max_value = current_max_value
        return max_value

    @staticmethod
    def get_innovation_id(gene_type, node_id=None, in_node_id=None, out_node_id=None):
        hasInnovation = False
        innovation_number = -1
        for innovation in Genome.innovations:
            if gene_type=='node' and innovation['type'] == gene_type and innovation['node_id']==node_id:
                hasInnovation=True
                innovation_number=innovation['innovation_number']
            elif gene_type=='connection' and innovation['type'] == gene_type and innovation['in']==in_node_id and innovation['out']==out_node_id:
                hasInnovation=True
                innovation_number=innovation['innovation_number']
        if hasInnovation==False:
            Genome.global_innovation_number+=1
            innovation_number = Genome.global_innovation_number
            if gene_type=='node':
                Genome.innovations.append({
                    'type': 'node',
                    'node_id': node_id,
                    'innovation_number': innovation_number
                })
            else:
                Genome.innovations.append({
                    'type': 'connection',
                    'in': in_node_id,
                    'out': out_node_id,
                    'innovation_number': innovation_number
                })
        return innovation_number


class Offspring(Genome):

    def __init__(self, Parent1, Parent2):
        Genome.global_genomes_id+=1
        self.genome_id = Genome.global_genomes_id
        self.number_of_sensor_units = Parent1.number_of_sensor_units
        self.number_of_output_units = Parent1.number_of_output_units

        self.mate(Parent1, Parent2)
        self.init_connection_matrix()
        self.init_node_genes()

        self.fitness = 1


    def mate(self, Parent1, Parent2):
        self.connection_genes = []
        parent1_connection_genes = Parent1.connection_genes
        parent2_connection_genes = Parent2.connection_genes
        i, j = (0,0)
        while i < len(parent1_connection_genes) and j < len(parent2_connection_genes):
            # In this situation we either have matching genes or disjoint genes
            if parent1_connection_genes[i]['innovation']==parent2_connection_genes[j]['innovation']:
                # Now we are hadnling matching genes, choosing randomly one of them
                random_index = np.random.randint(1, 3)
                if random_index == 1:
                    self.connection_genes.append(parent1_connection_genes[i])
                elif random_index == 2:
                    self.connection_genes.append(parent2_connection_genes[j])
                i+=1
                j+=1
            elif parent1_connection_genes[i]['innovation']<parent2_connection_genes[j]['innovation']:
                # We are taking disjoint gene from parent1
                self.connection_genes.append(parent1_connection_genes[i])
                i+=1
            else:
                # We are taking disjoint gene from parent2
                self.connection_genes.append(parent2_connection_genes[j])
                j+=1

        max_innovation_number = self.connection_genes[-1]['innovation']

        while i<len(parent1_connection_genes):
            parent1_connection_gene = parent1_connection_genes[i]
            if parent1_connection_gene['innovation']>max_innovation_number:
                self.connection_genes.append(parent1_connection_gene)
            i+=1

        while j<len(parent2_connection_genes):
            parent2_connection_gene = parent2_connection_genes[j]
            if parent2_connection_gene['innovation']>max_innovation_number:
                self.connection_genes.append(parent2_connection_gene)
            j+=1


    def init_connection_matrix(self):
        max_value = self.getMaxValueInConnectionGenesIds()
        matrix_dim = int(max_value)+1
        self.connection_matrix = np.zeros((matrix_dim,matrix_dim))
        for connection in self.connection_genes:
            self.connection_matrix[connection['in'],connection['out']]=connection['innovation']

    def init_node_genes(self):
        super(Offspring, self).init_node_genes()
        max_value = self.getMaxValueInConnectionGenesIds() + 1
        start=self.number_of_sensor_units+self.number_of_output_units
        for i in range(start, max_value):
            self.add_node()



class Species(object):
    species_list = []
    species_average_adjusted_fitness_list = []
    species_offspring_to_spawn = []
    c1 = 1.0
    c2 = 1.0
    c3 = 0.4
    N = 1
    threshold = 3.0
    crossover_rate = 0.75


    @staticmethod
    def measure_compatibility_distance(Genome1, Genome2):
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
                if genome1_connection_genes[i]['innovation']<genome2_connection_genes[j]['innovation']:
                    # We have disjoint genes in genome1
                    disjoint+=1
                    i+=1
                elif genome2_connection_genes[j]['innovation']<genome1_connection_genes[i]['innovation']:
                    # We have disjoint genes in genome2
                    disjoint+=1
                    j+=1
                else:
                    # Now we have matching genes
                    weight_difference = (genome1_connection_genes[i]['weight']-genome2_connection_genes[j]['weight'])
                    matching+=1
                    i+=1
                    j+=1
            else:
                # Now we only have excess genes
                excess+=1
                i+=1
                j+=1

        return Species.c1*excess/Species.N + Species.c2*disjoint/Species.N + Species.c3*weight_difference/matching

    @staticmethod
    def compute_adjusted_fitness(genome, species_length):
        return genome.fitness/species_length

    @staticmethod
    def assign_genome_to_spieces(genome):
        create_new_species=True
        for species in Species.species_list:
            if genome.genome_id==species[0].genome_id:
                create_new_species=False
                break
            elif Species.measure_compatibility_distance(genome, species[0]) < Species.threshold:
                create_new_species=False
                species.append(genome)
                break
        if create_new_species==True:
            Species.species_list.append([genome])

    @staticmethod
    def select_species_representatives():
        selected_representatives = []
        for species in Species.species_list:
            best = species[0]
            for genome in species:
                if best.fitness < genome.fitness:
                    best = genome
            selected_representatives.append([best])
        return selected_representatives

    @staticmethod
    def assign_species_representatives():
        Species.species_list = Species.select_species_representatives()

    @staticmethod
    def adjustFitnesses():
        Species.species_average_adjusted_fitness_list = []
        for species in Species.species_list:
            adjusted_fitness_sum=0
            for genome in species:
                genome.fitness=Species.compute_adjusted_fitness(genome, len(species))
                adjusted_fitness_sum+=genome.fitness
            Species.species_average_adjusted_fitness_list.append(adjusted_fitness_sum/len(species))

    @staticmethod
    def computeHowManyOffspringToSpawn():
        Species.species_offspring_to_spawn = []
        for species, average in zip(Species.species_list, Species.species_average_adjusted_fitness_list):
            species_offspring_to_spawn_sum = 0
            for genome in species:
                species_offspring_to_spawn_sum += genome.fitness/average
            Species.species_offspring_to_spawn.append(species_offspring_to_spawn_sum)

    @staticmethod
    def getNewGenomes(number_of_offspring):
        new_genomes = []
        current_number_of_offspring = 0
        for species, offspring_to_spawn in zip(Species.species_list,Species.species_offspring_to_spawn):
            offspring_to_spawn = int(round(offspring_to_spawn))
            offspring = species[0]
            best_choosed=True
            while offspring_to_spawn!=0 and current_number_of_offspring < number_of_offspring:
                if best_choosed==False and len(species)!=1:
                    random_genome_1 = Species.getRandomGenomeFromSpecies(species)
                    if random.uniform(0,1) < Species.crossover_rate:
                        try_to_mate_times = 5
                        random_genome_2 = Species.getRandomGenomeFromSpecies(species)
                        while random_genome_1.genome_id==random_genome_2.genome_id and try_to_mate_times!=0:
                            random_genome_2 = Species.getRandomGenomeFromSpecies(species)
                            try_to_mate_times-=1
                        if random_genome_1.genome_id!=random_genome_2.genome_id:
                            offspring=Offspring(random_genome_1,random_genome_2)
                        else:
                            offspring=random_genome_1
                    else:
                        offspring=random_genome_1

                offspring.mutate_add_connection()
                offspring.mutate_add_node()
                offspring.mutate_perturb_weights()

                new_genomes.append(offspring)
                best_choosed = False
                offspring_to_spawn-=1
                current_number_of_offspring+=1
        print(len(new_genomes))
        return new_genomes



    @staticmethod
    def getRandomGenomeFromSpecies(species):
        return species[random.randint(0,len(species)-1)]

class Neural_Network(object):

    def __init__(self, genome):
        self.init_neurons(genome)
        self.init_connections(genome.connection_genes)

    def init_connections(self, connection_genes):
        self.connections = []
        for connection_gene in connection_genes:
            if connection_gene['state']=='enabled':
                neuron_in=self.findNeuronById(connection_gene['in'])
                neuron_out=self.findNeuronById(connection_gene['out'])
                new_connection = {
                    'in': neuron_in,
                    'out': neuron_out,
                    'weight': connection_gene['weight']
                }
                self.connections.append(new_connection)
                neuron_in['connectionsOut'].append(new_connection)
                neuron_out['connectionsIn'].append(new_connection)


    def init_neurons(self, genome):
        self.neurons = []
        for node in genome.node_genes:
            self.neurons.append(self.create_neuron(node))


    def create_neuron(self, node):
        new_neuron = {
            'id': node['id'],
            'type': node['type'],
            'connectionsIn': [],
            'connectionsOut': [],
            'sumToActivate': 0,
            'output': 0
        }
        return new_neuron

    def findNeuronById(self, neuron_id):
        for neuron in self.neurons:
            if neuron['id']==neuron_id:
                return neuron

    def forward(self, x):
        # We first set the output of sensor neurons
        # to be equal to x, we assume that
        # sensor units are first
        current_neuron_id = 0

        while self.neurons[current_neuron_id]['type']=='sensor':
            self.neurons[current_neuron_id]['output']=x[current_neuron_id]
            current_neuron_id+=1

        outputs = []

        while current_neuron_id<len(self.neurons):
            sumToActivate = 0
            current_neuron = self.neurons[current_neuron_id]
            for connectionIn in current_neuron['connectionsIn']:
                weight = connectionIn['weight']
                neuronOutput = connectionIn['in']['output']
                sumToActivate+= weight * neuronOutput

            # Not sure if this works
            current_neuron['output']=self.modified_sigmoid(sumToActivate)

            if current_neuron['type']=='output':
                outputs.append(current_neuron['output'])

            current_neuron_id+=1

        return outputs

    @staticmethod
    def modified_sigmoid(x):
        return 1/(1+np.exp(-4.9*x))
