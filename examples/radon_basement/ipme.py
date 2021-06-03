import ipme

if __name__=="__main__":
    infer_datapath='radon_basement_PyMC3.npz'
    imd_diag = ipme.Diagram(infer_datapath, predictive_checks = ['radon'])
    imd_diag.get_diagram().show()