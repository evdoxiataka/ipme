import ipme

if __name__=="__main__":
    infer_datapath='reaction_times_pooled.npz'
    # infer_datapath='reaction_times_hierarchical.npz'
    imd_diag = ipme.Diagram(infer_datapath, predictive_checks = ['y_pred'])
    imd_diag.get_diagram().show()