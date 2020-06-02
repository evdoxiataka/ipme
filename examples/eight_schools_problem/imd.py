import imd

if __name__=="__main__":
    infer_datapath='inference_8_schools_centered.npz'
	#infer_datapath='inference_8_schools_non_centered.npz'
    imd_diag = imd.Diagram(infer_datapath, predictive_ckecks = ['y'])
    imd_diag.get_plot().show()