from openadapt.RWKV.RWKV import run_RWKV
import modal
import os
from openadapt import config


if __name__ == '__main__':
    Func = modal.Function.lookup("openadapt-rwkv", "run_RWKV")
    parameters = config.RWKV_PARAMETERS

    #Testing performance of various RWKV models and parameters
    parameters["temperature"] = 0.4
    print("SETUP 1: RWKV-Raven-14B", "Parameters:", parameters)
    print("Test 1:",Func.call(parameters=parameters))
    print("desired output: (2)")
    print("Test 2:",Func.call(parameters=parameters))
    print("desired output: (2)")
    print("Test 3:",Func.call(parameters=parameters))
    print("desired output: (2)")
    print("Test 4:",Func.call(parameters=parameters))
    print("desired output: (2)")

