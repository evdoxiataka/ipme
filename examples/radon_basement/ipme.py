import ipme

if __name__=="__main__":
    infer_datapath='radon_basement_PyMC3.npz'
    ipme.graph(infer_datapath, predictive_checks = ['radon'])