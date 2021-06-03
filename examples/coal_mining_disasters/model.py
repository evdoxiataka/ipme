import pandas as pd
import pymc3 as pm
import numpy as np
import arviz as az
from arviz_json import get_dag, arviz_to_json

## Discrete Variables Model
## Reference: https://docs.pymc.io/notebooks/getting_started.html#Case-study-2:-Coal-mining-disasters
#data
disaster_data = pd.Series([4, 5, 4, 0, 1, 4, 3, 4, 0, 6, 3, 3, 4, 0, 2, 6,
                           3, 3, 5, 4, 5, 3, 1, 4, 4, 1, 5, 5, 3, 4, 2, 5,
                           2, 2, 3, 4, 2, 1, 3, np.nan, 2, 1, 1, 1, 1, 3, 0, 0,
                           1, 0, 1, 1, 0, 0, 3, 1, 0, 3, 2, 2, 0, 1, 1, 1,
                           0, 1, 0, 1, 0, 0, 0, 2, 1, 0, 0, 0, 1, 1, 0, 2,
                           3, 3, 1, np.nan, 2, 1, 1, 1, 1, 2, 4, 2, 0, 0, 1, 4,
                           0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 1])
years = np.arange(1851, 1962)
years_missing=[1890,1935]

#model-inference
fileName='coal_mining_disasters_PyMC3'
samples=10000
tune=10000
chains=2
coords = {"year": years}
with pm.Model(coords=coords) as disaster_model:
    switchpoint = pm.DiscreteUniform('switchpoint', lower=years.min(), upper=years.max(), testval=1900)
    early_rate = pm.Exponential('early_rate', 1)
    late_rate = pm.Exponential('late_rate', 1)
    rate = pm.math.switch(switchpoint >= years, early_rate, late_rate)
    disasters = pm.Poisson('disasters', rate, observed=disaster_data, dims='year')
	#inference
	trace = pm.sample(samples, chains=chains, tune=tune)
    prior = pm.sample_prior_predictive(samples=samples)
    posterior_predictive = pm.sample_posterior_predictive(trace,samples=samples) 
	
## STEP 1	
# will also capture all the sampler statistics
data = az.from_pymc3(trace=trace, prior=prior, posterior_predictive=posterior_predictive)

## STEP 2	
# extract dag
dag = get_dag(disaster_model)
# insert dag into sampler stat attributes
data.sample_stats.attrs["graph"] = str(dag)

## STEP 3  
# save data      
arviz_to_json(data, fileName+'.npz')