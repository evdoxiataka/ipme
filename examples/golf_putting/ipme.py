import ipme

if __name__=="__main__":
    infer_datapath='golf_simple_PyMC3.npz'
	#infer_datapath='golf_geometry_PyMC3.npz'
    ipme.graph(infer_datapath, predictive_checks = ['successes'])