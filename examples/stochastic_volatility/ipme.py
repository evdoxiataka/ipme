import ipme

if __name__=="__main__":
    infer_datapath='stochastic_volatility__PyMC3.npz'
    ipme.graph(infer_datapath, predictive_checks=['returns'])