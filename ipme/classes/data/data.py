import numpy as np
import json

from ...interfaces.data_interface import Data_Interface
from .dimension import Dimension

class Data(Data_Interface):

    def __init__(self, inference_path):
        """
            Parameters:
            --------
                inference_path      A String of the inference data file path.
            Sets:
            --------
                _inferencedata      A structure of the inference data.
                _graph              A structure of the  model's variables graph data.
                _observed_variables A List of Strings of the observed variables.
                _idx_dimensions     A List of Dimension Objects defining
                                    the indexing dimensions of the data.
                _spaces             A List of Strings in {'prior', 'posterior'} of all
                                    the available MCMC sample spaces in the inference data
        """
        Data_Interface.__init__(self, inference_path)

    def _load_inference_data(self, datapath):
        """
            Inference data is retrieved from memory in .npz format

            Parameters:
            --------
                datapath   A String of the inference data path.
            Returns:
            --------
                A Dictionary of inference data
        """
        try:
            return np.load(datapath)
        except IOError:
            print("File %s cannot be loaded" % datapath)
            return None

    def _get_graph(self):
        """
            A graph of the probabilistic model in json format is
            retrieved from inference data.

            Returns:
            --------
                A Dictionary of graph data
        """
        graph=""
        try:
            header = self._inferencedata['header.json']
            header_js = json.loads(header)
            graph = header_js["inference_data"]["sample_stats"]["attrs"]["graph"]
        except KeyError:
            print("Inference_data has no key 'header.json'")
            return None
        return json.loads(graph.replace("'", "\""))
        #return json.loads(graph)

    def _get_obeserved_variables(self):
        return [k for k,v in self._graph.items() if v['type'] == 'observed']

    def _get_idx_dimensions(self):
        """
            Returns:
            --------
                idx_dimensions      A Dict {<var_name>: List of Dimension objects}
        """
        idx_dimensions={}
        for k,v in self._graph.items():
            if not k.endswith("__"):
                idx_dimensions[v["name"]] = {}
                vdims = v["dims"]
                vcoords = v["coords"]
                for d in vdims:
                    if d in vcoords:
                        idx_dimensions[v["name"]][d] = Dimension(d, values = vcoords[d])
        return idx_dimensions

    def _get_spaces_from_data(self):
        """
            Returns:
            --------
                spaces    A List of Strings in {'prior','posterior','prior_predictive','posterior_predictive','observed_data',
                          'constant_data', 'sample_stats', 'log_likelihood', 'predictions', 'predictions_constant_data'}
        """
        spaces=[]
        if 'header.json' in self._inferencedata:
            header = self._inferencedata['header.json']
            header_js = json.loads(header)
            if 'inference_data' in header_js:
                for space in ['prior','posterior','prior_predictive','posterior_predictive','observed_data','constant_data', 'sample_stats', 'log_likelihood', 'predictions', 'predictions_constant_data']:
                    if space in header_js['inference_data']:
                        spaces.append(space)
        return spaces

    def is_observed_variable(self,var_name):
        if var_name in self._observed_variables:
            return True
        else:
            return False

    def get_var_type(self, var_name):
        """"
            Return any in {"observed","free","deterministic"}
        """
        return self._graph[var_name]["type"]

    def get_var_dist(self, var_name):
        if "dist" in self._graph[var_name]["distribution"]:
            return self._graph[var_name]["distribution"]["dist"]
        else:
            return self._graph[var_name]["type"]

    def get_var_dist_type(self, var_name):
        """"
            Return any in {"Continuous","Discrete"}
        """
        if "type" in self._graph[var_name]["distribution"]:
            return self._graph[var_name]["distribution"]["type"]
        else:
            return ""

    def get_var_parents(self, var_name):
        if "parents" in self._graph[var_name]:
            return self._graph[var_name]["parents"]
        else:
            return []

    def get_samples(self, var_name, space=['prior','posterior']):
        """
            Returns the samples of <var_name> variable of the given space(s).

            Parameters:
            --------
                var_name      A String of the model's variables name
                space         Either a List of Strings or a String with String in {'prior','posterior'}
            Returns:
            --------
                A Dictionary of the form { <space> : <samples> }
                <space>    A String from {"prior", "posterior"}
                <samples>  A numpy.ndarray of <space> samples of the <var_name> parameter.
                            e.g. PyMC3 shape=N, sample=M
                                for i in M
                                     for j in N:
                                        Element (i,j) = (ith sample, jth prior/posterior distribution draw).
                If a String of space is given, it returns the numpy.ndarray.

        """
        array_name=""
        header = self._inferencedata['header.json']
        header_js = json.loads(header)
        if isinstance(space, list):
            data = {}
            for sp in space:
                if sp in self._spaces and self._is_var_in_space(var_name,sp):
                    array_name = header_js['inference_data'][sp]['array_names'][var_name]
                    if 'chain' in header_js['inference_data'][sp]['vars'][var_name]['dims']:
                        data[sp] = np.mean(self._inferencedata[array_name],axis=0)
                    else:
                        data[sp] = self._inferencedata[array_name]
            return data
        elif isinstance(space, str):
            data = np.asarray([])
            if space in self._spaces and self._is_var_in_space(var_name,space):
                array_name = header_js['inference_data'][space]['array_names'][var_name]
                if 'chain' in header_js['inference_data'][space]['vars'][var_name]['dims']:
                    data = np.mean(self._inferencedata[array_name],axis=0)
                else:
                    data = self._inferencedata[array_name]
            return data
        else:
            raise ValueError("space argument of get_sample should be either a List of Strings or a String")

    def get_observations(self, var_name):
        """
            Returns the observations of <var_name> variable.

            Parameters:
            --------
                var_name      A String of the model's variables name
            Returns:
            --------
                A numpy.ndarray of observations of the <var_name> parameter.
        """
        array_name=""
        header = self._inferencedata['header.json']
        header_js = json.loads(header)
        data = None  
        if var_name in header_js['inference_data']['observed_data']['array_names']:
            array_name = header_js['inference_data']['observed_data']['array_names'][var_name]
            dims = header_js['inference_data']['observed_data']['vars'][var_name]['dims']
            if 'chain' in dims:
                data = np.mean(self._inferencedata[array_name], axis=0)
            else:
                data = self._inferencedata[array_name]
            return data
        else:
            return data

    def get_range(self, var_name, space=['prior','posterior']):
        """
            Returns the range of samples of <var_name> variable of the given space(s).

            Parameters:
            --------
                var_name      A String of the model's variables name
                space         Either a List of Strings or a String with String in {'prior','posterior'}
            Returns:
            --------
                Tuple (min,max)

        """
        if self.get_var_type(var_name) == "observed":
            if space == "posterior" and "posterior_predictive" in self.get_spaces():
                space="posterior_predictive"
            elif space == "prior" and "prior_predictive" in self.get_spaces():
                space="prior_predictive"
        data = self.get_samples(var_name, space)
        min=0
        max=0
        if data.size:
            min = np.amin(data)
            max = np.amax(data)
        return (min - 0.1*(max-min),max + 0.1*(max-min))

    def get_varnames_per_graph_level(self, vars):
        """
            Matches variable names to graph levels.

            Returns:
            --------
                A Dict of the model's parameters names per graph level.
                Level 0 corresponds to the higher level.
                {<level>: List of variable names}, level=0,1,2...
        """
        nodes = self._add_nodes_to_graph(self._get_observed_nodes(), 0)
        varnames_per_graph_level = {}
        if vars == 'all':
            varnames_per_graph_level = self._reverse_nodes_levels(nodes)
        else:
            vars_per_level = self._reverse_nodes_levels(nodes)
            level = 0            
            for l in sorted(vars_per_level):
                for var in vars:
                    if var in vars_per_level[l] :
                        if level not in varnames_per_graph_level:
                            varnames_per_graph_level[level] = []
                        varnames_per_graph_level[level].append(var)
                level+=1
        return varnames_per_graph_level

    def _is_var_in_space(self, var_name, space):
        """
            Returns True if variable is in space and False if not.

            Parameters:
            --------
                var_name       A String of the model's variables name.
                space          A String in {'prior','posterior','posterior_predictive','prior_predictive'}.
            Returns:
            --------
                A Boolean
        """
        header = self._inferencedata['header.json']
        header_js = json.loads(header)
        if var_name in header_js['inference_data'][space]['array_names']:
            return True
        else:
            return False

    def _get_observed_nodes(self):
        """
            Get the observed nodes of the graph.

            Parameters:
            --------
                graph   A Dictionary
            Returns:
            --------
                A List of the model's observed nodes of the graph (dict objects)
        """
        try:
            return [v for k,v in self._graph.items() if v['type'] == 'observed']
        except KeyError:
            print("Graph has no key 'type'")
            return None

    def _get_graph_nodes(self, varnames):
        """
            Get the nodes of the graph indicated by a list of varnames.

            Parameters:
            --------
                graph       A Dictionary
                varnames    A List of Strings
            Returns:
            --------
                A List of the model's nodes of the graph (Dictionary objects)
        """
        nodes = []
        for vn in varnames:
            if vn in self._graph:
                nodes.append(self._graph[vn])
        return nodes

    @staticmethod
    def _reverse_nodes_levels(nodes):
        """
            Reverses the nodes' levels so that level 0 corresponds
            to the highest grid row.

            Parameters:
            --------
                nodes   A Dictionary
            Returns:
            --------
                A Dictionary of the nodes with reversed keys
        """
        max_level = max(nodes.keys())
        return dict((max_level-k, v) for k, v in nodes.items())

    def _add_nodes_to_graph(self, level_nodes, level):
        """
            Adds nodes to graph levels recursively.

            Parameters:
            --------
                level_nodes    A List of nodes (dict) of the same graph <level>.
                level          An Int denoting the level of the graph
                               where <level_nodes> belong to.
            Returns:
            --------
                A Dict of the model's parameters names per graph level.
                Level 0 corresponds to the lowest level.
                {<level>: List of variables names}, level=0,1,2...
        """
        nodes = {}
        try:
            for v in level_nodes:
                if level in nodes and v['name'] not in nodes[level]:
                    nodes[level].append(v['name'])
                else:
                    nodes[level]=[v['name']]

                parents_nodes = self._get_graph_nodes(v['parents'])
                if(len(parents_nodes)):
                    # if incl_nodes == 'all':
                    #     par_nodes = self._add_nodes_to_graph(parents_nodes, level+1, 'all')
                    # else:
                    #     parents_nodes_to_go_ahead = []
                    #     rest_nodes = []
                    #     for node in incl_nodes:
                    #         if node in parents_nodes:
                    #             parents_nodes_to_go_ahead.append(node)
                    #         else:
                    #             rest_nodes.append(node)
                    par_nodes = self._add_nodes_to_graph(parents_nodes, level+1)
                    for k in par_nodes:
                        if k in nodes:
                            for n in par_nodes[k]:
                                if n not in nodes[k]:
                                    nodes[k].append(n)
                        else:
                            nodes[k] = par_nodes[k]
            return nodes
        except KeyError:
            print("Graph node has no key 'name' or 'parents' ")
            return None
