import ipme

if __name__=="__main__":
    infer_datapath='coal_mining_disasters_PyMC3.npz'
    imd_diag = ipme.Diagram(infer_datapath, predictive_checks = ['disasters'])
    imd_diag.get_diagram().show()