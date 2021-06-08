from .classes.graph import Graph
from .classes.scatter_matrix import ScatterMatrix

def graph(data_path, mode = "i", predictive_checks = []):
    graph = Graph(data_path, mode, predictive_checks)
    graph.get_graph().show()

def scatter_matrix(data_path, mode = "i", vars = []):
    scatter_matrix = ScatterMatrix(data_path, mode, vars)
    scatter_matrix.get_scatter_matrix().show()