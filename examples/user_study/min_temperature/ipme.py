import ipme

if __name__=="__main__":
    infer_datapath='min_temperature.npz'
    ipme.scatter_matrix(infer_datapath,vars=['a','b','c','temperature'])