import pymc3 as pm
import pandas as pd
import numpy as np
import arviz as az
# !pip install git+https://github.com/johnhw/arviz_json.git
from arviz_json import get_dag, arviz_to_json

RANDOM_SEED = np.random.seed(1225)

DATAPATH='../../data/evaluation_sleepstudy.csv' ## data from Belenky et al. (2003)
reactions = pd.read_csv(DATAPATH,usecols=['Reaction','Days','Subject'])
reactions = reactions[0:3*10]

driver_idx, drivers = pd.factorize(reactions["Subject"], sort=True)
day_idx, days = pd.factorize(reactions["Days"], sort=True)
coords_c = {"driver": drivers,"driver_idx_day":reactions.Subject}
with pm.Model(coords=coords_c) as hierarchical_model:
    #hyper-priors
    c = pm.Normal('c', mu=100, sd=150)
    e = pm.HalfNormal('e', sd=150)
    f = pm.Normal('f', mu=10, sd=100)
    g = pm.HalfNormal('g', sd=100)
    h = pm.HalfNormal('h', sd=200)
    #priors
    a = pm.Normal("a", mu=c, sd=e, dims="driver")
    b = pm.Normal("b", mu=f, sd=g, dims="driver")
    sigma = pm.HalfNormal("sigma", sd=h, dims="driver")
    d = pm.Normal("d", mu = 0, sd=10.0)
    
    reaction_time = pm.Normal('reaction_time', 
                              mu = a[driver_idx]+b[driver_idx]*day_idx, 
                              sd=sigma[driver_idx],
                              observed=reactions.Reaction, 
                              dims="driver_idx_day")
    
samples=4000
chains=3
tune=3000
fileName_hi="reaction_times_hierarchical"
with hierarchical_model:
    # Get posterior trace, prior trace, posterior predictive samples, and the DAG
    trace_hi = pm.sample(draws=samples, chains=chains, tune=tune, target_accept=0.9)
    prior_hi = pm.sample_prior_predictive(samples=samples)
    posterior_predictive_hi = pm.sample_posterior_predictive(trace_hi, 
                                                             samples=samples)        
    
# export inference results in ArviZ InferenceData obj    
# will also capture all the sampler statistics
data_hi = az.from_pymc3(trace = trace_hi, 
                        prior = prior_hi, 
                        posterior_predictive = posterior_predictive_hi)
    
# insert dag into sampler stat attributes
dag_hi = get_dag(hierarchical_model)
data_hi.sample_stats.attrs["graph"] = str(dag_hi)
    
# save data   
arviz_to_json(data_hi, fileName_hi+'.npz')