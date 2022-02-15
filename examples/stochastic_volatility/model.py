import pandas as pd
import pymc3 as pm
import arviz as az
import numpy as np
from arviz_json import get_dag, arviz_to_json

#StudentT Timeseries Model
#Reference1: https://docs.pymc.io/notebooks/getting_started.html#Case-study-1:-Stochastic-volatility
#Reference2: https://docs.pymc.io/notebooks/stochastic_volatility.html#Stochastic-Volatility-model
#data
returns = pd.read_csv(pm.get_data('SP500.csv'), parse_dates=True, index_col=0)
dates = returns.index.strftime("%Y/%m/%d").tolist()

#model-inference
fileName='stochastic_volatility_PyMC3'
samples=2000
tune=2000
chains=2
coords = {"date": dates}
with pm.Model(coords=coords) as model:
    step_size = pm.Exponential('step_size', 10)
    volatility = pm.GaussianRandomWalk('volatility', sigma = step_size, dims='date')
    nu = pm.Exponential('nu', 0.1)
    returns = pm.StudentT('returns', nu = nu, lam = np.exp(-2*volatility) , observed = returns["change"], dims='date')
    #inference
    trace = pm.sample(draws=samples, chains=chains, tune=tune)
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