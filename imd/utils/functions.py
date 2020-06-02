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

def replace_inf_with_nan(np_array):
    if isinstance(np_array, np.ndarray):            
        np_array[np_array == np.inf] = np.nan
        np_array[np_array == -np.inf] = np.nan
    return np_array