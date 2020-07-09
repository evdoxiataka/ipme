import pandas as pd
import numpy as np
import pymc3 as pm
import arviz as az
from arviz_json import get_dag, arviz_to_json

## Non-hierarchical Binomial Logistic Regression Model
## Reference: https://docs.pymc.io/notebooks/GLM-logistic.html#The-model
#data
raw_data = pd.read_csv("https://archive.ics.uci.edu/ml/machine-learning-databases/adult/adult.data",
                       header=None,
                       names=['age', 'workclass', 'fnlwgt',
                              'education-categorical', 'educ',
                              'marital-status', 'occupation',
                              'relationship', 'race', 'sex',
                              'captial-gain', 'capital-loss',
                              'hours', 'native-country',
                              'income'])

data = raw_data[~pd.isnull(raw_data['income'])]
data[data['native-country']==" United-States"].sample(5)
income = 1 * (data['income'] == " >50K")
data = data[['age', 'educ', 'hours']]
# Scale age by 10, it helps with model convergence.
data['age'] = data['age']/10.
data['age2'] = np.square(data['age'])
data['income'] = income

#model
fileName='income_regression_PyMC3'
samples=1000
tune=1000
chains=2
dims={'y': ['adults']}
coords = {'adults':adults}
with pm.Model() as logistic_model:
    pm.glm.GLM.from_formula('income ~ age + age2 + educ + hours', data, family=pm.glm.families.Binomial())
    trace = pm.sample(samples, chains=chains, tune=tune, init='adapt_diag')
    posterior_predictive = pm.sample_posterior_predictive(trace,samples=samples)    
    dag = get_dag(logistic_model,dims,coords)
    
# will also capture all the sampler statistics
data = az.from_pymc3(trace=trace, posterior_predictive=posterior_predictive,coords=coords, dims=dims)

# insert dag into sampler stat attributes
data.sample_stats.attrs["graph"] = str(dag)
    
# save data      
arviz_to_json(data, fileName+'.npz')