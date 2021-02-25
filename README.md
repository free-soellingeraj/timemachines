# timemachines ![tests](https://github.com/microprediction/timemachines/workflows/tests/badge.svg) ![skater-elo-ratings](https://github.com/microprediction/timemachines-testing/workflows/skater-elo-ratings/badge.svg) ![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

## Popular time-series packages in a simple functional form

What's different:
   - **Simple k-step ahead forecasts** with [one line of code](https://github.com/microprediction/timemachines/blob/main/timemachines/skaters/proph/prophskaterscomposed.py). 
   Time series "models" are defined by functions with a "skater" signature facilitating [skating](https://github.com/microprediction/timemachines/blob/main/timemachines/skating.py).
   One might say that skater functions *suggest* state machines for sequential assimilation of observations (as a data point arrives, 
    a forecasts for 1,2,...,k steps ahead, with corresponding standard deviations are emitted). However the *caller* is expected to maintain state from one 
    invocation (data point) to the next.  
   
   - **Simple tuning** with [one line of code](https://github.com/microprediction/timemachines/blob/main/timemachines/skatertools/tuning/hyper.py) facilitated by [HumpDay](https://github.com/microprediction/humpday), which provides a one-line canonical use of scipy.optimize, ax-platform,
   hyperopt, optuna, platypus, pymoo, pySOT, skopt, dlib, nlopt, bayesian-optimization, nevergrad and more. 

   
   - **Simple evaluation** with [one line of code](https://github.com/microprediction/timemachines/blob/main/timemachines/skatertools/evaluation/evaluators.py) using
    metrics like RMSE or energy distances. 
    
   - **Simple stacking** of models with [one line of code](https://github.com/microprediction/timemachines/blob/main/timemachines/skaters/simple/thinking.py). The functional
   form makes other types of model combination easy as well.  

   - **Simple, ongoing empirical evaluation**. See the [leaderboards](https://github.com/microprediction/timemachines-testing/tree/main/skater_elo_ratings/leaderboards) in
    the accompanying repository [timemachines-testing](https://github.com/microprediction/timemachines-testing) listing Elo ratings
     for skaters with no unassigned hyper-parameters. Assessment is always out of sample and uses *live*, constantly updating real-world data 
     from [microprediction.org](https://www.microprediction.org/browse_streams.html).   

  
  - **Simpler deployment**. There is no state, other that that explicitly returned to the caller. For many models state is a pure Python dictionary and thus
  trivially converted to JSON and back. 

**NO CLASSES!**  **NO DATAFRAMES!** **NO CEREMONY!**   

![](https://i.imgur.com/elu5muO.png)

## The Skater signature 

A skater function *f* takes a vector *y*, where the quantity to be predicted is y[0] and there may be other, simultaneously observed
 variables y[1:] deemed helpful in predicting y[0]. The function also takes a quantity *a* which is a vector of numbers known k-steps in advance. 

      x, w, s = f(   y:Union[float,[float]],               # Contemporaneously observerd data, 
                                                         # ... including exogenous variables in y[1:], if any. 
                s=None,                                  # Prior state
                k:float=1,                               # Number of steps ahead to forecast. Typically integer. 
                a:[float]=None,                          # Variable(s) known in advance, or conditioning
                t:float=None,                            # Time of observation (epoch seconds)
                e:float=None,                            # Non-binding maximal computation time ("e for expiry"), in seconds
                r:float=None)                            # Hyper-parameters ("r" stands for for hype(r)-pa(r)amete(r)s in R^n)

The function is intended to be applied repeatedly. For example one could harvest
a sequence of the model predictions as follows:

    def posteriors(f,y):
        s = {}       
        x = list()
        for yi in y: 
            xi, xi_std, s = f(yi,s)
            x.append(xi)
        return x
 
Notice the use of s={} on first invocation. This is also important: 
- The caller should provide *a* pertaining to k-steps ahead, not the contemporaneous 'a'.  

   
### Skater "e" argument ("expiry")

The use of *e* is a fairly *weak* convention that many skaters ignore. In theory, a large expiry *e* can be used as a hint to the callee that
 there is time enough to do a 'fit', which we might define as anything taking longer than the usual function invocation.
 However, this is between the caller and it's priest really - or its prophet. Some skaters, such
 as the prophet skater, do a full 'fit' every invocation so this is meaningless. Other skaters
  no separate notion of 'fit' versus 'update' because everything is incremental. 
   
## Skater "r" argument ("hype(r) pa(r)amete(r)s")

A scalar in the closed interval \[0,1\]

### Return values

For each prediction horizon it returns
two numbers where the first can be *interpreted* as a point estimate (but need not be) and the second is *typically* suggestive
of a symmetric error std, or width. Morally, a skater *suggests* an affine transformation of the incoming data. 


          -> x     [float],    # A vector of point estimates, or anchor points, or theos
             x_std [float]     # A vector of "scale" quantities (such as a standard deviation of expected forecast errors) 
             s    Any,         # Posterior state, intended for safe keeping by the callee until the next invocation 
                       

In returning state, the likely intent is that the *caller* might carry the state from one invocation to the next, not the *callee*. This is arguably more convenient than having the predicting object maintain state, because the caller can "freeze" the state as they see fit, as 
when making conditional predictions. This also eyes lambda-based deployments and *encourages* tidy use of internal state - not that we succeed
 when calling down to statsmodels (but all the home grown models here use simple dictionaries, making serialization trivial). See [FAQ](https://github.com/microprediction/timemachines/blob/main/FAQ.md) if this seems odd). 

### Skater hyper-parameter *r* in the interval (0,1)
 
Morally hyper-parameters occupy the cube but operationally, we use an unusual convention. All model hyper-parameters must be squished down into
 a *scalar* quantity *r* in (0,1). This step may seem unnatural, but is workable with some space-filling curve conventions. More on that below. 
    
### Summary of conventions: 

- State
    - The caller, not the callee, persists state from one invocation to the next
    - The caller passes s={} the first time, and the callee initializes state
    - State can be mutable for efficiency (e.g. it might be a long buffer) or not. 
    - State should, ideally, be JSON-friendly. 
       
- Observations: target, and contemporaneous exogenous
     - If y is a vector, the target is the first element y[0]
     - The elements y[1:] are contemporaneous exogenous variables, *not known in advance*.  
     - Missing data can be supplied to some skaters, as np.nan.  
     - Most skaters will accept scalar *y* and *a* if there is only one of either. 
    
- Variables known k-steps in advance, or conditioning variables:
     - Pass the *vector* argument *a* that will occur in k-steps time (not the contemporaneous one)
     - Remark: In the case of k=1 there are different interpretations that are possible beyond "business day", such as "size of a trade" or "joystick up" etc. 

- Hyper-Parameter space:
     - A float *r* in (0,1). 
     - This package provides functions *to_space* and *from_space*, for expanding to R^n using space filling curves, so that the callee's (hyper) parameter optimization can still exploit geometry, if it wants to.   
     - See discussion below    
    
    
Nothing here is put forward
   as *the right way* to write time series packages - more a way of exposing their functionality for comparisons. 
  If you are interested in design thoughts for time series maybe participate in this [thread](https://github.com/MaxBenChrist/awesome_time_series_in_python/issues/1). 


 
## Usage 
 
### Install

    pip install timemachines
    pip install microprediction   (if you want to use live data)
    
### Tuning hyper-params

- See [examples](https://github.com/microprediction/timemachines/tree/main/examples) 
- See [examples/tuning](https://github.com/microprediction/timemachines/tree/main/examples/tuning)
- See [tuning](https://github.com/microprediction/timemachines/tree/main/timemachines/skatertools/tuning)
    
## Contribute 

If you'd like to contribute to this standardizing and benchmarking effort, here are some ideas:

- See the [list of popular time series packages](https://www.microprediction.com/blog/popular-timeseries-packages) ranked by download popularity. 
- Think about the most important hyper-parameters and consider "warming up" the mapping (0,1)->hyper-params by testing on real data. There is a [tutorial](https://www.microprediction.com/python-3) on retrieving live data, or use the [real data](https://pypi.org/project/realdata/) package, if that's simpler.
- The [comparison of hyper-parameter optimization packages](https://www.microprediction.com/blog/optimize) might also be helpful.  

If you are the maintainer of a time series package, we'd love your feedback and if you take the time to submit a PR here that incorporates your library, do yourself a favor and also enable "supporting" on your repo. 

See also [FAQ](https://github.com/microprediction/timemachines/blob/main/FAQ.md)
