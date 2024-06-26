# Interactive Visualizations of Probabilistic Models
This package provides interactive visualizations of probabilistc models' inherent uncertainty in the prior and posterior sample space. 

These visualizations are intented for interactive exploration of the *uncertainty* in Bayesian probabilistic models and enhancement of their interpretability. 

## Requirements
* Probabilistic models are expressed in a Probabilistic Programming Language (PPL), and 
* A sample-based inference algorithm is used for the inference (e.g. MCMC). 

## Input
The visualizations provided by this package take as an input a zip file in the *.npz* format. This file contains a description of the model's structure and the inference results (MCMC samples) 
in a standardized form of a collection of npy arrays and metadata (in a json format). 
The [arviz_json](https://github.com/johnhw/arviz_json) package creates this standardized output of probabilistic models expressed in *PyMC3*. For more details about the standardization of the IPME input see *Taka et al. 2020*.

The following figure presents the pipeline for the automatic transformation of a probabilistic model expressed in a PPL and its sample-based inference results into the standardized .npz file.

![method](https://user-images.githubusercontent.com/37831445/97790524-20ed6900-1bc1-11eb-950c-838ea67b4163.jpg)

## Example of a Probabilistic Model
The following probabilistic statements describe the drivers' reaction times model under sleep-deprivation conditions for 10 consecutive days and 18 lorry drivers. This is a hierarchical linear regression probabilistic model. The problem and data for this model retrieved from *Belenky et al. 2003*.

![image](https://user-images.githubusercontent.com/37831445/120328046-56d30700-c2e2-11eb-8e4f-05d891e4b2d4.png)

## Interactive Probabilistic Models Explorer (IPME)
The *IPME* representation of the model is presented in the following figure. See more details about this representation in *Taka et al. 2020*. A demo of this visualization can be found in my [talk](https://www.youtube.com/watch?v=2hadiSJRAJI&feature=youtu.be) to PyMCON 2020.
```python
import ipme
"""
mode:               String in {'i','s'} for interactive or static
vars:               'all' or List of variable names e.g. ['a','b']
spaces:             String in {'all','prior','posterior'} or List of spaces e.g. ['prior','posterior']
predictive_checks:  List of observed variables names
"""
ipme.graph("reaction_times_hierarchical.npz", mode = "i", vars = 'all', spaces = 'all', predictive_checks = ['y_pred'])
```

<!--![image](https://user-images.githubusercontent.com/37831445/97790652-3616c780-1bc2-11eb-948b-54797f199ecb.png)-->


https://user-images.githubusercontent.com/37831445/205636036-ec1a6820-f368-4332-9fcf-0a508c8dd63f.mp4


## Interactive Pair Plot (IPP)
The *IPP* representation of the model is presented in the following figure. This visualization was introduced and evaluated in *Taka et al. 2022*.
```python
import ipme
"""
mode:               String in {'i','s'} for interactive or static
vars:               List of variable names e.g. ['a','b']
spaces:             String in {'all','prior','posterior'} or List of spaces e.g. ['prior','posterior']
"""
ipme.scatter_matrix('reaction_times_hierarchical.npz', mode = "i", vars = ['sigma_a','sigma_b','sigma_sigma','mu_a','mu_b','sigma','a','b','y_pred'], spaces = 'all')
```
<!--![image](https://user-images.githubusercontent.com/37831445/154061049-1666eb8c-28fb-4346-9741-c166152a1ab8.png)-->


https://user-images.githubusercontent.com/37831445/205637701-ac11ff87-c240-4882-8b69-8b0b15d8e344.mp4


# Examples
The folder `/examples` in this repository includes some examples of use. The examples illustrates the definition of Bayesian probabilistic models and running of sample-based inference in PyMC3. The examples are organized per problem. Each problem's directory includes the following Python scripts:
* *`model.py`*: includes the definition of the model in PyMC3, and exports the inference data into a *.npz* file. 
* *`ipme.py`*: demonstrates the use of the ipme package for the visualization of the model.

The folder `/examples/user_study` contains the models used in the user study presented in *Taka et al. 2022*.

**Note:** To run these scripts, you need to install the following Python libraries: PyMC3, ArviZ, and the arviz_json and ipme packages (the last two can only be installed through github).  

# Please Cite:
*E. Taka,  S. Stein,  and J. H. Williamson.*  Increasing interpretability of Bayesian probabilistic programming models through interactive representations. Frontiers in Computer Science, 2:52, 2020. doi:  10.3389/fcomp.2020.567344.  URL: https://www.frontiersin.org/article/10.3389/fcomp.2020.567344

*E. Taka, S. Stein and J. H. Williamson,* "Does Interactive Conditioning Help Users Better Understand the Structure of Probabilistic Models?," in IEEE Transactions on Visualization and Computer Graphics, doi: 10.1109/TVCG.2022.3231967

# References
*E. Taka,  S. Stein,  and J. H. Williamson.*  Increasing interpretability of Bayesian probabilistic programming models through interactive representations. Frontiers in Computer Science, 2:52, 2020. doi:  10.3389/fcomp.2020.567344.  URL: https://www.frontiersin.org/article/10.3389/fcomp.2020.567344

*E. Taka, S. Stein and J. H. Williamson,* "Does Interactive Conditioning Help Users Better Understand the Structure of Probabilistic Models?," in IEEE Transactions on Visualization and Computer Graphics, doi: 10.1109/TVCG.2022.3231967

*G.  Belenky,  N.  J.  Wesensten,  D.  R.  Thorne,  M.  L.  Thomas,  H.  C.  Sing,  D.  P.  Redmond,  M.  B.  Russo,  and  T.  J.Balkin.*  Patterns  of  performance  degradation and restoration during sleep restriction  and subsequent recovery: a sleep dose-response study. Journal of Sleep Research, vol. 12, no. 1, pp. 1–12, 2003. URL: https://onlinelibrary.wiley.com/doi/abs/10.1046/j.1365-2869.2003.00337.x


*The “Closed-Loop Data Science for Complex, Computationally- and Data-Intensive Analytics” project*. URL: https://www.gla.ac.uk/schools/computing/research/researchsections/ida-section/closedloop/ 

*arviz_json* (Automatic Transformation of PyMC3 models into standardized output): https://github.com/johnhw/arviz_json
