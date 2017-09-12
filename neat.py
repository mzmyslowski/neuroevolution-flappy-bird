import random
import numpy as np

class Genome(object):
    # sensor_units can be found in connection_genes simply using number_of_sensor_units
    # way to output_units can be found following by order fields 'In' and 'Out' in connection_genes

    def __init__(self, number_of_sensor_units, number_of_output_units):
        self.number_of_sensor_units = number_of_sensor_units
        self.number_of_output_units = number_of_output_units
        self.node_genes = self.__create_node_genes()
        self.global_innovation_number = 0
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
                    'Innovation': self.global_innovation_number
                })
        return connection_genes

    def __create_connection_matrix(self):
        matrix_dim = self.number_of_sensor_units*self.number_of_output_units+1
        connection_matrix = np.zeros((matrix_dim,matrix_dim))
        for connection in self.connection_genes:
            connection_matrix[connection['In'],connection['Out']]=connection['Innovation']
        return connection_matrix

    def mutate_add_connection(self):
        connection_indices = self.get_random_unconnected_genes()
        self.connection_matrix[connection_indices] = 1
        self.increment_innovation_number()
        self.connection_genes.append({
            'In': connection_indices[0],
            'Out': connection_indices[1],
            'Weight': random.gauss(0,1),
            'State': 'Enabled',
            'Innovation': self.global_innovation_number
        })

    def mutate_add_node(self):
        connection_indices = self.get_random_connected_genes()
        innovation_number = int(self.connection_matrix[connection_indices])
        self.connection_genes[innovation_number-1]['State']='Disabled'
        new_connection_matrix = np.zeros((self.connection_matrix.shape[0]+1,self.connection_matrix.shape[1]+1))
        new_connection_matrix[:-1,:-1]=self.connection_matrix

        self.increment_innovation_number()
        new_connection_matrix[connection_indices[0],-1]=self.global_innovation_number
        self.increment_innovation_number()
        new_connection_matrix[-1,connection_indices[1]]=self.global_innovation_number
        self.connection_matrix = new_connection_matrix

        self.connection_genes.append({
            'In': connection_indices[0],
            'Out': int(self.connection_matrix[connection_indices[0],-1]),
            'Weight': 1,
            'State': 'Enabled',
            'Innovation': int(new_connection_matrix[connection_indices[0],-1])
        })
        self.connection_genes.append({
            'In': int(self.connection_matrix[connection_indices[0],-1]),
            'Out': connection_indices[1],
            'Weight': self.connection_genes[innovation_number-1]['Weight'],
            'State': 'Enabled',
            'Innovation': int(new_connection_matrix[-1,connection_indices[1]])
        })

    def get_random_unconnected_genes(self):
        connected_indices = np.argwhere(self.connection_matrix==0)
        random_index = np.random.randint(0, connected_indices.shape[0])
        return (connected_indices[random_index][0],connected_indices[random_index][1])

    def get_random_connected_genes(self):
        connected_indices = np.argwhere(self.connection_matrix!=0)
        random_index = np.random.randint(0, connected_indices.shape[0])
        return (connected_indices[random_index][0],connected_indices[random_index][1])

    def increment_innovation_number(self):
        self.global_innovation_number+=1

class Offspring(Genome):

    def __init__(self, Parent1, Parent2):
        self.connection_genes = self.__mate(Parent1, Parent2)
        self.global_innovation_number=self.connection_genes[len(self.connection_genes)-1]['Innovation']
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


Parent1 = Genome(2,1)
Parent1.mutate_add_node()
Parent2 = Genome(2,1)
print(Parent1.connection_genes)
print(Parent2.connection_genes)
Offspring1 = Offspring(Parent1, Parent2)
print(Offspring1.connection_genes)
print(Offspring1.connection_matrix)
Offspring1.mutate_add_node()
print(Offspring1.connection_genes)
