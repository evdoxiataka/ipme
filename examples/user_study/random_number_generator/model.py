import pymc3 as pm
import numpy as np
import arviz as az
# !pip install git+https://github.com/johnhw/arviz_json.git
from arviz_json import get_dag, arviz_to_json

RANDOM_SEED = np.random.seed(1225)

x_data = np.random.uniform(-3, 5, size=5)
obs = np.arange(len(x_data))

fileName = 'transformation'
samples = 4000
# tune = 10000
chains = 1
coords = {"obs": obs}
uniform_model = pm.Model(coords=coords)
with uniform_model:
    # Priors for unknown model parameters
    a = pm.Normal('a', mu = 0, sd=10)  
    b = pm.HalfNormal('b', sd = 10)
    c = pm.HalfNormal('c', sd=20)
    
    l = a - c
    u = a + c
    random_number = pm.Uniform('random_number', 
                               lower=l,  
                               upper=u, 
                               observed=x_data, 
                               dims="obs")
    
    trace = pm.sample(samples, chains = chains, target_accept=0.95)
    posterior_predictive = pm.sample_posterior_predictive(trace, samples=samples)
    prior = pm.sample_prior_predictive(samples=samples, random_seed=RANDOM_SEED)
    
# will also capture all the sampler statistics
data = az.from_pymc3(trace = trace)

# will also capture all the sampler statistics
data = az.from_pymc3(trace = trace, 
                     prior = prior, 
                     posterior_predictive = posterior_predictive)

dag = get_dag(uniform_model)
data.sample_stats.attrs["graph"] = str(dag)
    
# save data      
arviz_to_json(data, fileName+'.npz')