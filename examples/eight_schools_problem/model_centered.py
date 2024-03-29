import pymc3 as pm
import numpy as np
import arviz as az
from arviz_json import get_dag, arviz_to_json
SEED = [20100420, 20134234]

#Hierarchical Model
#Reference: https://docs.pymc.io/notebooks/Diagnosing_biased_Inference_with_Divergences.html#The-Eight-Schools-Model
#data
J = 8
obs = np.array([28.,  8., -3.,  7., -1.,  1., 18., 12.])
sigma = np.array([15., 10., 16., 11.,  9., 11., 10., 18.])

#model-inference
coords_c = {"school": ["A","B","C","D","E","F","G","H"]}
fileName_c="eight_schools_centered"
samples=4000
chains=2
tune=1000
with pm.Model(coords=coords_c) as centered_eight:
    mu = pm.Normal('mu', mu=0, sigma=5)
    tau = pm.HalfCauchy('tau', beta=5)
    theta = pm.Normal('theta', mu=mu, sigma=tau, dims='school')
    y = pm.Normal('y', mu=theta, sigma=sigma, observed=obs, dims='school')
    #inference
    trace_c = pm.sample(samples, chains=chains, tune=tune, random_seed=SEED)
    prior_c= pm.sample_prior_predictive(samples=samples)
    posterior_predictive_c = pm.sample_posterior_predictive(trace_c, samples=samples)

## STEP 1
# will also capture all the sampler statistics
data_c = az.from_pymc3(trace = trace_c, prior = prior_c, posterior_predictive = posterior_predictive_c)

## STEP 2
#dag
dag_c = get_dag(centered_eight)
# insert dag into sampler stat attributes
data_c.sample_stats.attrs["graph"] = str(dag_c)

## STEP 3
# save data
arviz_to_json(data_c, fileName_c+'.npz')
