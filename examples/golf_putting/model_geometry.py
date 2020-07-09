import pandas as pd
import io
import pymc3 as pm
import arviz as az
from arviz_json import get_dag, arviz_to_json
import theano.tensor as tt

CUP_RADIUS = (4.25 / 2) / 12
BALL_RADIUS = (1.68 / 2) / 12

def Phi(x):
    """Calculates the standard normal cumulative distribution function."""
    return 0.5 + 0.5 * tt.erf(x / tt.sqrt(2.))

#Binomial Model
#Reference: https://docs.pymc.io/notebooks/putting_workflow.html#Geometry-based-model
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
dims={"p_goes_in":["distance"],"successes":["distance"]}
coords = {"distance": data.distance}
fileName='golf_geometry_PyMC3'
samples=2000
chains=2 
tune=1000
geometry_model=pm.Model()
with geometry_model:
    #to store the n-parameter of Binomial dist 
    #in the constant group of ArviZ InferenceData
    #You should always call it n for imd to retrieve it
    n = pm.Data('n', data.tries)
    sigma_angle = pm.HalfNormal('sigma_angle')
    p_goes_in = pm.Deterministic('p_goes_in', 2 * Phi(tt.arcsin((CUP_RADIUS - BALL_RADIUS) / data.distance) / sigma_angle) - 1)
    successes = pm.Binomial('successes', n=n, p=p_goes_in, observed=data.successes)
    #inference
    trace_g = pm.sample(draws=samples, chains=chains, tune=tune)
    prior_g= pm.sample_prior_predictive(samples=samples)
    posterior_predictive_g = pm.sample_posterior_predictive(trace_g,samples=samples)    
    #dag    
    dag_g = get_dag(geometry_model,dims,coords)

# will also capture all the sampler statistics
data_g = az.from_pymc3(trace=trace_g, prior=prior_g, posterior_predictive=posterior_predictive_g, coords=coords, dims=dims)
    
# insert dag into sampler stat attributes
data_g.sample_stats.attrs["graph"] = str(dag_g)
    
# save data
arviz_to_json(data_g, fileName+'.npz')