from scipy.optimize import minimize

from .vcirc.base import Vcirc
from .measure.measure_sample import dst,hst,dst_source
from .measure.measure_sim import sep_purity, fid_ref, c_entropy

def  vcirc_test(
        x,
        statein,
        vcirc: Vcirc,
        test_func=sep_purity,
        ansatz_li=None,
        *args,
        **kwargs):

    vcirc.update_ansatzes(x,ansatz_li)
    N = vcirc.N
    if (statein.dims[0] != [2]*N):
        raise ValueError("Invalid input state, must be state on %s qubits system." % N)

    stateout = vcirc.apply_to(statein)
    return test_func(stateout,*args,**kwargs)

def  __vcirc_test_neg(
        x,
        statein,
        vcirc: Vcirc,
        test_func=sep_purity,
        ansatz_li=None,
        *args,
        **kwargs):

    vcirc.update_ansatzes(x,ansatz_li)
    N = vcirc.N
    if (statein.dims[0] != [2]*N):
        raise ValueError("Invalid input state, must be state on %s qubits system." % N)

    stateout = vcirc.apply_to(statein)
    return -test_func(stateout,*args,**kwargs)

def circ_minimize(
        x0,
        statein,
        vcirc: Vcirc,
        test_func=sep_purity,
        *args,
        ansatz_li=None,
        opt_method="BFGS",
        jac=None, hess=None, hessp=None, bounds=None,
        constraints=(), tol=None, callback=None, options=None):
    res = minimize(vcirc_test,x0,(statein,vcirc,test_func,ansatz_li)+args,opt_method,
                   jac, hess, hessp, bounds, constraints, tol, callback, options)
    return res

def circ_maximize(
        x0,
        statein,
        vcirc: Vcirc,
        test_func=sep_purity,
        *args,
        ansatz_li=None,
        opt_method="BFGS",
        jac=None, hess=None, hessp=None, bounds=None,
        constraints=(), tol=None, callback=None, options=None):
    res = minimize(__vcirc_test_neg,x0,(statein,vcirc,test_func,ansatz_li)+args,opt_method,
                   jac, hess, hessp, bounds, constraints, tol, callback, options)
    res.fun = -res.fun
    return res