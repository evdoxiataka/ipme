import pymc3 as pm
import numpy as np
import arviz as az
# !pip install git+https://github.com/johnhw/arviz_json.git
from arviz_json import get_dag, arviz_to_json

RANDOM_SEED = np.random.seed(1225)

## the average minimum temperature in Scotland in month November for the years
## 1884-2020: metoffice.gov.uk
## https://www.metoffice.gov.uk/pub/data/weather/uk/climate/datasets/Tmin/date/Scotland.txt
l = [1.0,1.1,2.5,0.8,2.7,2.9,1.4,1.1,2.2,0.3,3.6,1.7,2.1,3.5,1.5,4.6,2.3,
     1.2,3.5,1.8,1.3,1.2,3.7,1.4,2.9,-0.3,-1.1,1.1,1.6,3.2,1.9,-1.3,3.2,
     3.1,0.8,-1.6,3.6,0.7,2.1,-0.5,3.5,-0.0,1.1,1.8,2.7,2.0,0.6,3.6,1.8,
     1.7,1.5,1.7,1.3,1.5,3.8,3.0,1.9,1.7,1.0,2.2,0.4,3.4,2.7,1.6,3.0,2.4,
     0.6,3.4,-0.3,4.0,1.6,3.5,2.6,2.8,2.2,2.9,1.7,1.1,1.5,2.2,2.3,-0.2,0.5,
     1.5,1.7,-0.8,1.9,1.7,0.9,0.9,1.7,1.8,1.5,0.9,3.1,1.2,1.9,2.5,2.2,3.0,
     3.3,-1.1,2.5,2.6,1.7,2.0,2.0,2.0,1.5,0.4,5.2,3.0,0.2,4.6,1.3,2.9,1.8,
     3.0,3.8,3.4,3.3,1.5,3.4,3.4,2.0,2.8,0.0,4.8,1.7,1.1,3.8,3.6,0.3,1.5,3.6,1.1]
years = np.arange(1884,2020)

fileName='min_temperature'
samples=4000
chains=2
tune=1000
coords = {'years':years}
temperature_model = pm.Model(coords=coords)
with temperature_model:
    #priors
    a = pm.Uniform('a', 80, 100)
    b = pm.Normal('b', mu=2, sd=10)
    c = pm.HalfNormal('c', sd=10)
        
    #predictions
    temperature = pm.Normal('temperature', 
                            mu = b, 
                            sd = c, 
                            observed = l, 
                            dims = 'years')
    
    trace = pm.sample(draws=samples, chains=chains, tune=tune)
    prior = pm.sample_prior_predictive(samples=samples)
    posterior_predictive = pm.sample_posterior_predictive(trace, samples=samples)
    dag = get_dag(temperature_model)
    
# will also capture all the sampler statistics
data = az.from_pymc3(trace=trace, 
                     prior=prior, 
                     posterior_predictive=posterior_predictive)

# insert dag into sampler stat attributes
data.sample_stats.attrs["graph"] = str(dag)
    
# save data      
arviz_to_json(data, fileName+'.npz')