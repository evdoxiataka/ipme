import ipme

if __name__=="__main__":
    infer_datapath='reaction_times_pooled.npz'
    # infer_datapath='reaction_times_hierarchical.npz'
    ipme.graph(infer_datapath, predictive_checks = ['y_pred'])