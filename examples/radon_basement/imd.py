import imd

if __name__=="__main__":
    infer_datapath='radon_basement_PyMC3.npz'
    imd_diag = imd.Diagram(infer_datapath, predictive_ckecks = ['radon'])
    imd_diag.get_diagram().show()