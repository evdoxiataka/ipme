import pymc3 as pm
import pandas as pd
import numpy as np
import arviz as az
from arviz_json import get_dag, arviz_to_json
SEED = [20100420, 20134234]

#Reference: https://docs.pymc.io/notebooks/Diagnosing_biased_Inference_with_Divergences.html#A-Non-Centered-Eight-Schools-Implementation
#data
J = 8
obs = np.array([28.,  8., -3.,  7., -1.,  1., 18., 12.])
sigma = np.array([15., 10., 16., 11.,  9., 11., 10., 18.])

#model-inference
dims={ "theta_t": ["school"], "theta": ["school"], "y": ["school"],}
coords = {"school": ["A","B","C","D","E","F","G","H"]}
samples=5000
chains=2
tune=1000
fileName="inference_8_schools_non_centered"
with pm.Model() as NonCentered_eight:
    mu = pm.Normal('mu', mu=0, sigma=5)
    tau = pm.HalfCauchy('tau', beta=5)
    theta_tilde = pm.Normal('theta_t', mu=0, sigma=1, shape=J)
    theta = pm.Deterministic('theta', mu + tau * theta_tilde)
    y = pm.Normal('y', mu=theta, sigma=sigma, observed=obs)
	#inference
    trace_nc = pm.sample(samples, chains=chains, tune=tune, random_seed=SEED, target_accept=.90)
    prior_nc= pm.sample_prior_predictive(samples=samples)
    posterior_predictive_nc = pm.sample_posterior_predictive(trace_nc,samples=samples)
	#dag	
    dag_nc = get_dag(NonCentered_eight,dims,coords)
    
# will also capture all the sampler statistics
data_nc = az.from_pymc3(trace = trace_nc, prior = prior_nc, posterior_predictive = posterior_predictive_nc, coords = coords, dims = dims)
    
# insert dag into sampler stat attributes
data_nc.sample_stats.attrs["graph"] = str(dag_nc)
    
# save data   
arviz_to_json(data_nc, fileName+'.npz')