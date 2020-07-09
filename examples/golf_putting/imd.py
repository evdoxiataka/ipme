import imd

if __name__=="__main__":
    infer_datapath='golf_simple_PyMC3.npz'
	#infer_datapath='golf_geometry_PyMC3.npz'
    imd_diag = imd.Diagram(infer_datapath, predictive_ckecks = ['successes'])
    imd_diag.get_diagram().show()