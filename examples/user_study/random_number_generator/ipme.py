import ipme

if __name__=="__main__":
    infer_datapath='transformation.npz'
    ipme.scatter_matrix(infer_datapath, vars=['a','b','c','random_number'])