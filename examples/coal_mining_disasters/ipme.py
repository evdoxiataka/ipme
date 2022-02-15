import ipme

if __name__=="__main__":
    infer_datapath='coal_mining_disasters_PyMC3.npz'
    ipme.graph(infer_datapath, predictive_checks = ['disasters'])