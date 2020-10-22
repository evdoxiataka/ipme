import pandas as pd
import io
import pymc3 as pm
import arviz as az
from arviz_json import get_dag, arviz_to_json

#Binomial Logistic Regression Model
#Reference: https://docs.pymc.io/notebooks/putting_workflow.html#Logit-model
#data
golf_data = """distance tries successes
2 1443 1346
3 694 577
4 455 337
5 353 208
6 272 149
7 256 136
8 240 111
9 217 69
10 200 67
11 237 75
12 202 52
13 192 46
14 174 54
15 167 28
16 201 27
17 195 31
18 191 33
19 147 20
20 152 24"""
data = pd.read_csv(io.StringIO(golf_data), sep=" ")

#model-inference
coords = {"distance": data.distance}
fileName='golf_simple_PyMC3'
samples=2000
chains=2
tune=1000
simple_model=pm.Model(coords=coords)
with simple_model:
    #to store the n-parameter of Binomial dist 
    #in the constant group of ArviZ InferenceData
    #You should always call it n for imd to retrieve it
    n = pm.Data('n', data.tries)
    a = pm.Normal('a')
    b = pm.Normal('b')
    p_goes_in = pm.Deterministic('p_goes_in', pm.math.invlogit(a * data.distance + b), dims='distance')
    successes = pm.Binomial('successes', n=n, p=p_goes_in, observed=data.successes, dims='distance')
    #inference
    # Get posterior trace, prior trace, posterior predictive samples, and the DAG
    trace = pm.sample(draws=samples, chains=chains, tune=tune)
    prior= pm.sample_prior_predictive(samples=samples)
    posterior_predictive = pm.sample_posterior_predictive(trace,samples=samples)       
    
## STEP 1
# will also capture all the sampler statistics
data_s = az.from_pymc3(trace=trace, prior=prior, posterior_predictive=posterior_predictive)

## STEP 2
#dag 
dag = get_dag(simple_model)    
# insert dag into sampler stat attributes
data_s.sample_stats.attrs["graph"] = str(dag)

## STEP 3    
# save data
arviz_to_json(data_s, fileName+'.npz')