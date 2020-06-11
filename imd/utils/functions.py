import numpy as np
from math import gcd

def lcm(list_of_int):
    """
        Get the Least Common Multyply (lcm) of a list of integer numbers.

         Parameters:
         --------
            list_of_int   A List of integers
        Returns:
        --------
            An integer (the lcm of list_of_int).
    """    
    try:
        lcm = list_of_int[0]
        for i in list_of_int[1:]:
            lcm = lcm*i/gcd(int(lcm), i)
        return int(lcm)
    except IndexError:
        return None

def find_indices(lst, condition):
    return [i for i, elem in enumerate(lst) if condition(elem)]

def find_inds_before_after(lst, el):
    inds_sm=find_indices(lst, lambda e: e<= el)
    if len(inds_sm):
        ind_before=inds_sm[-1]
    else:
        ind_before=-1
    inds_bi=find_indices(lst, lambda e: e>= el)
    if len(inds_bi):
        ind_after=inds_bi[0]
    else:
        ind_after=-1
    return (ind_before,ind_after)

def find_highest_point( x, y):
    x=np.asarray(x, dtype=np.float64)
    y=np.asarray(y, dtype=np.float64)
    if len(y):
        max_idx=np.argmax(y)
        return (x[max_idx],y[max_idx])
    else:
        return ()

def get_samples_for_pred_check(samples, func):
    # samples = np.asarray(samples)
    shape = samples.shape
    if 0 not in shape:               
        if len(shape) == 1:
            axis = 0
        else:
            axis = 1    
        if len(shape) > 2:
            fir_dim = shape[0]
            sec_dim = 1
            for i in np.arange(1,len(shape),1):
                sec_dim = sec_dim*shape[i]  
            samples=samples.reshape(fir_dim,sec_dim)                      
        if func == "min":                
            samples = samples.min(axis=axis)            
        elif func == "max":
            samples = samples.max(axis=axis)
        elif func == "mean":
            samples = samples.mean(axis=axis)
        elif func == "std":
            samples = samples.std(axis=axis)
        else:
            samples = np.empty([1, 2])   
        if ~np.isfinite(samples).all():
            samples = get_finite_samples(samples)         
    else:
        samples = np.empty([1, 2]) 
    return samples

def get_finite_samples(np_array):
    if isinstance(np_array, np.ndarray):  
        shape = len(np_array.shape)
        if shape == 1:
            np_array = np_array[np.isfinite(np_array)]
        elif shape > 1:
            samples_idx = np.isfinite(np_array).all(axis=shape-1)
            for axis in np.arange(shape-2,0,-1):          
                samples_idx = np.isfinite(np_array).all(axis=axis)
            np_array = np_array[samples_idx]
    return np_array

def get_hist_bins_range(samples, var_type):
    """
        samples: flatten finite samples
    """
    if var_type == "Discrete":
        values = np.unique(samples)
        if len(values) < 20:
            min_v = values.min()
            max_v = values.max()
            bins = len(values)       
            range = ( min_v, max_v + (max_v - min_v) / (bins - 1))     
            return (bins, range)
    bins = 20
    range = (samples.min(),samples.max())
    return (bins, range)

def get_dim_names_options(dim):
    """
        dim: imd.Dimension object
    """
    name1 = dim.name
    name2 = ""
    options1 = dim.values 
    options2 = []
    if "_idx_" in name1:
        idx = name1.find("_idx_")
        st_n1 = idx + 5
        end_n1 = len(name1)
        name2 = name1[st_n1:end_n1] 
        name1 = name1[0:idx]
        values = np.array(dim.values)
        options1 = np.unique(values).tolist()                    
        if len(options1):
            tmp = np.arange(np.count_nonzero(values == options1[0]))
            options2 = list(map(str,tmp))  
    return (name1, name2, options1, options2)  

def get_w2_w1_val_mapping(dim):
    """
        dim: imd.Dimension object
        Returns:
        -------
        A Dict {<opt1_val>: A List of <opt2_val> for this <opt1_val>}
    """
    options1 = dim.values 
    options2 = []
    values = np.array(dim.values)
    options1 = np.unique(values)    
    val_dict = {}                
    if len(options1):
        for v1 in options1:
            tmp = np.arange(np.count_nonzero(values == v1))
            val_dict[v1] = list(map(str,tmp))
    return val_dict                         