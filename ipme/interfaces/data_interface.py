from abc import ABC, abstractmethod

class Data_Interface(ABC):

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
                _idx_dimensions     A Dict {<var_name>:{<dim_name>:Dimension obj}}. 
                _spaces             A List of Strings in {'prior', 'posterior'} of all  
                                    the available MCMC sample spaces in the inference data        
        """
        self._inferencedata = self._load_inference_data(inference_path)
        self._graph = self._get_graph()
        self._observed_variables = self._get_obeserved_variables()
        self._idx_dimensions = self._get_idx_dimensions()      
        self._spaces = self._get_spaces_from_data()

    @abstractmethod
    def _load_inference_data(self,datapath):
        pass

    @abstractmethod
    def _get_graph(self):
        pass  

    @abstractmethod
    def _get_obeserved_variables(self):     
        pass

    @abstractmethod
    def _get_idx_dimensions(self):     
        pass

    @abstractmethod
    def _get_spaces_from_data(self):     
        pass

    @abstractmethod
    def is_observed_variable(self,var_name):
        pass

    @abstractmethod
    def get_var_type(self,var_name):
        pass

    @abstractmethod
    def get_var_dist(self,var_name):
        pass

    @abstractmethod
    def get_var_dist_type(self,var_name):
        pass

    @abstractmethod
    def get_var_parents(self,var_name):
        pass

    @abstractmethod
    def get_samples(self,var_name,space=['prior','posterior']):
        pass

    @abstractmethod
    def get_range(self, var_name, space=['prior','posterior']):
        pass

    @abstractmethod
    def get_varnames_per_graph_level(self):
        pass

    def get_data(self):
        return self._data

    def get_obeserved_variables(self):     
        return self._observed_variables

    def get_inferencedata(self):
        return self._inferencedata 

    def get_idx_dimensions(self, var_names):
        idx_dims = {}
        for var in var_names:
            if var in self._idx_dimensions:
                for dim in self._idx_dimensions[var]:
                    if dim not in idx_dims:
                        idx_dims[dim] = self._idx_dimensions[var][dim]
        return idx_dims

    def get_indx_for_idx_dim(self, var_name, d_name, d_value):
        indx=-1     
        if var_name in self._idx_dimensions and d_name in self._idx_dimensions[var_name]:
            dvalues = self._idx_dimensions[var_name][d_name].values
            if d_value in dvalues:
                indx = dvalues.index(d_value)
        return indx

    def get_spaces(self):
        return self._spaces
    
