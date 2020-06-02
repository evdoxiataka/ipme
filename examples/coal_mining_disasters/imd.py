import imd

if __name__=="__main__":
    infer_datapath='coal_mining_disasters_PyMC3.npz'
    imd_diag = imd.Diagram(infer_datapath, predictive_ckecks = ['disasters'])
    imd_diag.get_plot().show()