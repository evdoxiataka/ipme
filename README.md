# Interactive Probabilistic Models Explorer (IPME)
This tool provides an interactive visual explorer for the probabilistic models' graphs and inference results. This tool requires that:
* probabilistic models are expressed in a Probabilistic Programming Language (PPL), and 
* a sample-based inference algorithm is used for the inference (e.g. MCMC). 

*IPME* is intented for interactive exploration of the *uncertainty* of Bayesian probabilistic models and enhancement of their interpretability. 

## IPME Input
IPME takes as an input a zip file in the *.npz* format. This file contains a description of the model's structure and the inference results (MCMC samples) 
in a standardized form of a collection of npy arrays and metadata (in a json format). 
For example, the [arviz_json](https://github.com/johnhw/arviz_json) package creates this standardized output of probabilistic models expressed in *PyMC3*.

The following figure presents the pipeline for the automatic transformation of a probabilistic model expressed in a PPL and its sample-based inference results into the standardized .npz file.

![method](https://user-images.githubusercontent.com/37831445/97790524-20ed6900-1bc1-11eb-950c-838ea67b4163.jpg)

## IPME Output
The following probabilistic statements describe the drivers' reaction times model under sleep-deprivation conditions for 10 consecutive days and 18 lorry drivers. This is a hierarchical linear regression probabilistic model.

![image](https://user-images.githubusercontent.com/37831445/120328046-56d30700-c2e2-11eb-8e4f-05d891e4b2d4.png)

The output of the IPME tool for this probabilistic model is presented in the following figure.

![image](https://user-images.githubusercontent.com/37831445/97790652-3616c780-1bc2-11eb-948b-54797f199ecb.png)

# Examples
The examples directory includes some examples of use. Each example illustrates the definition of a Bayesian probabilistic model, which models the corresponding problem, in PyMC3. It also illustrates the use of the standard PyMC3 implementations of MCMC algorithms for running the inference.
The examples are organized per problem. Each problem's directory includes:
* *`model.py`*: a Python code file, wich demonstrates the specification of the problem's model in PyMC3, and the export of the inference data into 
the standardized format described above. 
* *`ipme.py`*: another Python code file, which demonstrates the use of the ipme package for the transformation of the model and its inference into the interactive visual explorer.

**Note:** For the specification and run of the PyMC3 models, you need to install PyMC3, ArviZ, and the arviz_json package.  

# References
*E. Taka,  S. Stein,  and JH Williamson.*  Increasing interpretability of Bayesian probabilistic programming models through interactive representations. Frontiers in Computer Science, 2:52, 2020. doi:  10.3389/fcomp.2020.567344.  URL: https://www.frontiersin.org/article/10.3389/fcomp.2020.567344

*The “Closed-Loop Data Science for Complex, Computationally- and Data-Intensive Analytics” project*. URL: https://www.gla.ac.uk/schools/computing/research/researchsections/ida-section/closedloop/ 

*arviz_json* (Automatic Transformation of PyMC3 models into standardized output): https://github.com/johnhw/arviz_json
