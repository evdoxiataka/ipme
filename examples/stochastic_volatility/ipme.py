import ipme

if __name__=="__main__":
    infer_datapath='stochastic_volatility__PyMC3.npz'
    imd_diag = ipme.Diagram(infer_datapath, predictive_checks=['returns'])
    imd_diag.get_diagram().show()