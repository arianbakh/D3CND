import networkx as nx
import os
import tarfile
import urllib.request

from networks.abstract_network import Network
from networks.tools import random_walk_sample, save_graph_figure
from settings import DATA_DIR


UCI_ONLINE_URL = 'http://konect.uni-koblenz.de/downloads/tsv/opsahl-ucsocial.tar.bz2'
UCI_ONLINE_TAR_PATH = os.path.join(DATA_DIR, 'opsahl-ucsocial.tar.bz2')
UCI_ONLINE_DIR = os.path.join(DATA_DIR, 'opsahl-ucsocial')
UCI_ONLINE_TSV_PATH = os.path.join(UCI_ONLINE_DIR, 'out.opsahl-ucsocial')


class UCIOnline(Network):
    name = 'UCI'

    def __init__(self):
        self.sample_size = 20
        super().__init__()

    @staticmethod
    def _ensure_data():
        if not os.path.exists(UCI_ONLINE_DIR):
            urllib.request.urlretrieve(UCI_ONLINE_URL, UCI_ONLINE_TAR_PATH)
            tar = tarfile.open(UCI_ONLINE_TAR_PATH, "r:bz2")
            tar.extractall(DATA_DIR)
            tar.close()

    @staticmethod
    def _data_generator():
        UCIOnline._ensure_data()
        with open(UCI_ONLINE_TSV_PATH, 'r') as tsv_file:
            for i, line in enumerate(tsv_file.readlines()):
                if not line.startswith('%'):
                    split_line = line.strip().split()
                    from_id = int(split_line[0])
                    to_id = int(split_line[1])
                    count = int(split_line[2])
                    timestamp = int(split_line[3])
                    yield from_id, to_id, count, timestamp

    def _create_adjacency_matrix(self):
        graph = nx.Graph()
        for from_id, to_id, count, timestamp in UCIOnline._data_generator():
            graph.add_edge(from_id, to_id)

        sorted_components = sorted(nx.connected_components(graph), key=len, reverse=True)
        giant_component = graph.subgraph(sorted_components[0])

        subgraph = random_walk_sample(giant_component, self.sample_size)
        self.number_of_nodes = len(subgraph)
        save_graph_figure(subgraph, UCIOnline.name)
        return nx.to_numpy_array(subgraph)
