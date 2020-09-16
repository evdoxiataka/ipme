import imd

if __name__=="__main__":
    infer_datapath='income_regression_PyMC3.npz'
    imd_diag = imd.Diagram(infer_datapath, predictive_checks = ['y'])
    imd_diag.get_diagram().show()