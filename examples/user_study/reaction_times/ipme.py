import ipme

if __name__=="__main__":
    infer_datapath='reaction_times_hierarchical.npz'
    ipme.scatter_matrix(infer_datapath,vars=['a','b','c','d','reaction_time'])