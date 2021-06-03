import pandas as pd
import pymc3 as pm
import arviz as az
from arviz_json import get_dag, arviz_to_json

## data
DATAPATH='./data/evaluation_sleepstudy.csv'
reactions = pd.read_csv(DATAPATH,usecols=['Reaction','Days','Subject'])

## Drivers Reaction Times Pooled Model
samples=4000
chains=2
tune=2000

## data
driver_idx, drivers = pd.factorize(reactions["Subject"], sort=True)
day_idx, days = pd.factorize(reactions["Days"], sort=True)

## dims
coords_p = {"driver": drivers,"driver_idx_day":reactions.Subject}

with pm.Model(coords=coords_p) as fullyPooled_model:
    ## model
    a = pm.Normal("a", mu=100, sd=250)
    b = pm.Normal("b", mu=10, sd=250)
    sigma = pm.HalfNormal("sigma", sd=200)        
    y_pred = pm.Normal('y_pred', mu = a + b*day_idx, sd = sigma, observed = reactions.Reaction, dims = "driver_idx_day")
    ## inference
    trace_p = pm.sample(samples, chains=chains, tune=tune)
    prior_p = pm.sample_prior_predictive(samples=samples)
    posterior_predictive_p = pm.sample_posterior_predictive(trace_p, samples=samples)  

## STEP 1
## export inference results in ArviZ InferenceData obj    
## will also capture all the sampler statistics
data_p = az.from_pymc3(trace = trace_p, prior = prior_p, posterior_predictive = posterior_predictive_p)

## STEP 2
## extract dag
dag_p = get_dag(fullyPooled_model)
## insert dag into sampler stat attributes
data_p.sample_stats.attrs["graph"] = str(dag_p)

## STEP 3
## save data   
fileName_p = "reaction_times_pooled"
arviz_to_json(data_p, fileName_p+'.npz')