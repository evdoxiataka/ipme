import pandas as pd
import pymc3 as pm
import arviz as az
from arviz_json import get_dag, arviz_to_json

## data
DATAPATH='../data/evaluation_sleepstudy.csv' ## data from Belenky et al. (2003)
reactions = pd.read_csv(DATAPATH, usecols=['Reaction','Days','Subject'])

## Drivers Reaction Times Hierarchical Model
samples = 2000
chains = 2
tune = 1000

## data
driver_idx, drivers = pd.factorize(reactions["Subject"], sort=True)
day_idx, days = pd.factorize(reactions["Days"], sort=True)

##dims
coords_h = {"driver": drivers,"driver_idx_day":reactions.Subject}

with pm.Model(coords=coords_h) as hierarchical_model:
    ## model
    #hyper-priors
    mu_a = pm.Normal('mu_a' ,mu=100, sd=250)
    sigma_a = pm.HalfNormal('sigma_a', sd=250)
    mu_b = pm.Normal('mu_b',mu=10, sd=250)
    sigma_b = pm.HalfNormal('sigma_b', sd=250)
    sigma_sigma = pm.HalfNormal('sigma_sigma', sd=200)
    #priors
    a = pm.Normal("a", mu=mu_a, sd=sigma_a, dims="driver")
    b = pm.Normal("b", mu=mu_b, sd=sigma_b, dims="driver")
    sigma = pm.HalfNormal("sigma", sd=sigma_sigma, dims="driver")    
    y_pred = pm.Normal('y_pred', mu=a[driver_idx]+b[driver_idx]*day_idx, sd=sigma[driver_idx], observed=reactions.Reaction, dims="driver_idx_day")
    ## inference
    trace_hi = pm.sample(draws=samples, chains=chains, tune=tune)
    prior_hi = pm.sample_prior_predictive(samples=samples)
    posterior_predictive_hi = pm.sample_posterior_predictive(trace_hi, samples=samples)  

## STEP 1
## export inference results in ArviZ InferenceData obj    
## will also capture all the sampler statistics
data_hi = az.from_pymc3(trace = trace_hi, prior = prior_hi, posterior_predictive = posterior_predictive_hi)
  
## STEP 2
## extract dag
dag_hi = get_dag(hierarchical_model)
## insert dag into sampler stat attributes
data_hi.sample_stats.attrs["graph"] = str(dag_hi)

## STEP 3
## save data   
fileName_hi = "reaction_times_hierarchical"
arviz_to_json(data_hi, fileName_hi+'.npz')