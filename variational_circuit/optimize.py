from scipy.optimize import minimize

from .measure.measure_sample import dst
from .measure.measure_sim import sep_purity, fid_ref, c_entropy

def  vcirc_test(x,statein,vcirc,test_func=sep_purity,*args,**kwargs):
    vcirc.update_ansatzes(x)
    N = vcirc.N
    if (statein.dims[0] != [2]*N):
        raise ValueError("Invalid input state, must be state on %s qubits system." % N)

    stateout = vcirc.apply_to(statein)
    return test_func(stateout,*args,**kwargs)

def  _vcirc_test_neg(x,statein,vcirc,test_func=sep_purity,*args,**kwargs):
    vcirc.update_ansatzes(x)
    N = vcirc.N
    if (statein.dims[0] != [2]*N):
        raise ValueError("Invalid input state, must be state on %s qubits system." % N)

    stateout = vcirc.apply_to(statein)
    return -test_func(stateout,*args,**kwargs)

def circ_minimize(x0,statein,vcirc,test_func=sep_purity,*args,opt_method="BFGS",
    jac=None, hess=None, hessp=None, bounds=None,
    constraints=(), tol=None, callback=None, options=None):
    res = minimize(vcirc_test,x0,(statein,vcirc,test_func)+args,opt_method,
    jac, hess, hessp, bounds, constraints, tol, callback, options)
    return res

def circ_maximize(x0,statein,vcirc,test_func=sep_purity,*args,opt_method="BFGS",
    jac=None, hess=None, hessp=None, bounds=None,
    constraints=(), tol=None, callback=None, options=None):
    res = minimize(_vcirc_test_neg,x0,(statein,vcirc,test_func)+args,opt_method,
    jac, hess, hessp, bounds, constraints, tol, callback, options)
    res.fun = -res.fun
    return res