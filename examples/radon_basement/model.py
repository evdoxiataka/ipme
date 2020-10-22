import numpy as np
import pymc3 as pm
import pandas as pd
import theano
import arviz as az
from arviz_json import get_dag, arviz_to_json

#Hierarchical Linear Regression Model
#Reference1: https://docs.pymc.io/notebooks/multilevel_modeling.html
#Reference2: https://docs.pymc.io/notebooks/GLM-hierarchical.html#The-data-set
#data
data_r = pd.read_csv(pm.get_data('radon.csv'))
data_r['log_radon'] = data_r['log_radon'].astype(theano.config.floatX)
county_names = data_r.county.unique()
county_idx = data_r.county_code.values

n_counties = len(data_r.county.unique())

#model-inference
fileName='radon_basement_PyMC3'
samples=3000
tune=10000
chains=2
coords = {"county":county_names, "county_idx_household":data_r["county"].tolist()}
with pm.Model(coords=coords) as model:
    # Hyperpriors for group nodes
    mu_a = pm.Normal('mu_a', mu=0., sigma=100)
    sigma_a = pm.HalfNormal('sigma_a', 5.)
    mu_b = pm.Normal('mu_b', mu=0., sigma=100)
    sigma_b = pm.HalfNormal('sigma_b', 5.)

    # Intercept for each county, distributed around group mean mu_a
    # Above we just set mu and sd to a fixed value while here we
    # plug in a common group distribution for all a and b (which are
    # vectors of length n_counties).
    a = pm.Normal('a', mu=mu_a, sigma=sigma_a, dims='county')
    # Intercept for each county, distributed around group mean mu_a
    b = pm.Normal('b', mu=mu_b, sigma=sigma_b, dims='county')

    # Model error
    eps = pm.HalfCauchy('eps', 5.)

    radon_est = a[county_idx] + b[county_idx]*data_r.floor.values

    # Data likelihood
    radon = pm.Normal('radon', mu=radon_est,
                           sigma=eps, observed=data_r.log_radon, dims='county_idx_household')

    #Inference
    trace = pm.sample(samples, chains=chains, tune=tune, target_accept=1.0)
    prior = pm.sample_prior_predictive(samples=samples)
    posterior_predictive = pm.sample_posterior_predictive(trace, samples=samples)    
    
## STEP 1
# will also capture all the sampler statistics
data = az.from_pymc3(trace=trace, prior=prior, posterior_predictive=posterior_predictive)

## STEP 2
#dag
dag = get_dag(model)
# insert dag into sampler stat attributes
data.sample_stats.attrs["graph"] = str(dag)

## STEP 3    
# save data      
arviz_to_json(data, fileName+'.npz')