import random

class Genome(object):

    def __init__(self, number_of_sensor_units, number_of_output_units):
        self.number_of_sensor_units = number_of_sensor_units
        self.number_of_hidden_units = number_of_hidden_units
        self.number_of_output_units = number_of_output_units
        self.node_genes = self.__create_node_genes()
        self.global_innovation_number = -1
        self.connection_genes = self.__create_connection_genes()

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
                self.global_innovation_number+=1
                connection_genes.append({
                    'In': sensor,
                    'Out': output,
                    'Weight': random.gauss(0,1),
                    'State': 'Enabled',
                    'Innovation': self.global_innovation_number
                })
        return connection_genes

gen = Genome(2,0,1)
print(gen.connection_genes[0])
print(gen.connection_genes[1])
