import random
import numpy as np

class Genome(object):
    # Here we initialize static innovations list
    # and static innovation number
    innovations = []
    global_innovation_number = 0

    def __init__(self, number_of_sensor_units, number_of_output_units):
        self.number_of_sensor_units = number_of_sensor_units
        self.number_of_output_units = number_of_output_units

        self.init_node_genes()
        self.init_connection_genes()

        self.fitness = 0

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
        random_unconnected_genes = self.get_random_unconnected_genes()
        # We check if there are some unconnected genes
        if random_unconnected_genes!=None:
            in_node_id, out_node_id = random_unconnected_genes
            self.add_connection(in_node_id, out_node_id)

    def get_random_unconnected_genes(self):
        # We get indices of unconnected nodes
        # with an exception of of sensor_units
        # being treated as out
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
        self.number_of_sensor_units = Parent1.number_of_sensor_units
        self.number_of_output_units = Parent1.number_of_output_units

        self.mate(Parent1, Parent2)
        self.init_connection_matrix()
        self.init_node_genes()



    def mate(self, Parent1, Parent2):
        self.connection_genes = []
        parent1_connection_genes = Parent1.connection_genes
        parent2_connection_genes = Parent2.connection_genes
        min_length = min([len(parent1_connection_genes),len(parent2_connection_genes)])
        i, j = (0,0)
        while i < min_length and j < min_length:
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
        if i<len(parent1_connection_genes):
            # We have some excess genes in Parent1
            self.connection_genes.extend(parent1_connection_genes[i:len(parent1_connection_genes)])
        if j<len(parent2_connection_genes):
            # We have some excess genes in Parent2
            self.connection_genes.extend(parent2_connection_genes[j:len(parent2_connection_genes)])

    def init_connection_matrix(self):
        max_value = self.getMaxValueInConnectionGenesIds()
        matrix_dim = int(max_value)+1
        self.connection_matrix = np.zeros((matrix_dim,matrix_dim))
        for connection in self.connection_genes:
            self.connection_matrix[connection['in'],connection['out']]=connection['innovation']

    def init_node_genes(self):
        super(Offspring, self).init_node_genes()
        max_value = self.getMaxValueInConnectionGenesIds()
        start=self.number_of_sensor_units+self.number_of_output_units
        for i in range(start, max_value):
            self.add_node()



class Species(object):
    species_list = []
    c1 = 1.0
    c2 = 1.0
    c3 = 0.4
    N = 1
    threshold = 3.0


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

        return Species.c1*excess/Species.N + Species.c2*disjoint/Species.N + Species.c3*weight_difference/matching

    @staticmethod
    def compute_adjusted_fitness(organism, species):
        adjusted_fitness = organism.fitness
        denominator = 0
        for other_organism in species:
            denominator = 0 if Speciation.measure_compatibility_distance(organism, other_organism) > Species.threshold else 0
        return adjusted_fitness/denominator

    @staticmethod
    def assign_genome_to_spieces(genome):
        create_new_species=True
        for species in Species.species_list:
            if Species.compute_adjusted_fitness(genome, species) < threshold:
                create_new_species=False
                species.append(genome)
                break
        if create_new_species==True:
            Species.species_list.append([genome])


class Neural_Network(object):

    @staticmethod
    def modified_sigmoid(x):
        return 1/(1+np.exp(-4.9*x))

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
        for connection in connection_genes:
            connection['Iterated']=False
        return Neural_Network.modified_sigmoid(output)

    @staticmethod
    def compute_neuron(x, connection_genes, output_index):
        output=0
        for connection in connection_genes:
            if connection['Out']==output_index:
                if len(x)==connection['In']:
                    print(connection_genes)
                    print('\n')
                    print(connection)
                output+=x[connection['In']]*connection['Weight']
                connection['Iterated']=True
        return output

gen1 = Genome(2,1)
gen2 = Genome(2,1)
gen1.mutate_add_node()
gen2.mutate_add_node()
kid = Offspring(gen1, gen2)
print(gen1.node_genes)
print(gen1.connection_genes)
print('\n')
print(gen2.node_genes)
print(gen2.connection_genes)
print('\n')
print(kid.node_genes)
print(kid.connection_genes)
#print(kid.connection_genes)
#print(kid.node_genes)
#print(kid.connection_genes)
#print(kid.connection_matrix)
#gen = Genome(3,1)
#weights=[]
#inputs=[35,174, 287]
#for connection in gen.connection_genes:
#    weights.append(connection['Weight'])
#    print(connection['Weight'])
#sum1=0
#for x, weight in zip(inputs, weights):
#    sum1+=x*weight
#print(Neural_Network.forward(inputs, gen.connection_genes))
#print(Neural_Network.modified_sigmoid(sum1))
