import imd

if __name__=="__main__":
    infer_datapath='stochastic_volatility__PyMC3.npz'
    imd_diag = imd.Diagram(infer_datapath)
    imd_diag.get_diagram().show()