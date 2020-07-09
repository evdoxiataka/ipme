import pandas as pd
import numpy as np
import pymc3 as pm
import arviz as az
from arviz_json import get_dag, arviz_to_json

## Hierarchical Multiple Linear Regression Model
## Reference: https://docs.pymc.io/notebooks/GLM.html?highlight=guber1999data#Hierarchical-GLM
#data
sat_data = pd.read_csv(pm.get_data('Guber1999data.txt'))
states=sat_data.index.tolist()

#model
fileName='sat_regression_PyMC3'
samples=2000
tune=2000
chains=2
dims={"y":["state"]}
coords = {"state":states}
with pm.Model() as model_sat:
    grp_mean = pm.Normal('grp_mean', mu=0, sigma=10)
    grp_sd = pm.Uniform('grp_sd', 0, 200)
    # Define priors for intercept and regression coefficients.
    priors = {'Intercept': pm.Normal.dist(mu=sat_data.sat_t.mean(), sigma=sat_data.sat_t.std()),
              'spend': pm.Normal.dist(mu=grp_mean, sigma=grp_sd),
              'stu_tea_rat': pm.Normal.dist(mu=grp_mean, sigma=grp_sd),
              'salary': pm.Normal.dist(mu=grp_mean, sigma=grp_sd),
              'prcnt_take': pm.Normal.dist(mu=grp_mean, sigma=grp_sd)
              }
    pm.GLM.from_formula(
        'sat_t ~ spend + stu_tea_rat + salary + prcnt_take', sat_data, priors=priors)
    #inference
    trace = pm.sample(samples, chains=chains,tune=tune, cores=2)
    prior = pm.sample_prior_predictive(samples=samples)
    posterior_predictive = pm.sample_posterior_predictive(trace, samples=samples)    
    dag = get_dag(model_sat, dims, coords)
    
# will also capture all the sampler statistics
data = az.from_pymc3(trace=trace, prior=prior, posterior_predictive=posterior_predictive,coords=coords, dims=dims)

# insert dag into sampler stat attributes
data.sample_stats.attrs["graph"] = str(dag)
    
# save data      
arviz_to_json(data, fileName+'.npz')