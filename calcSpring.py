import numpy as np
from py_post import *

def calcSpring(fileName, nodeID, freeMovement):

    # create a postpy obj using post_open
    p = post_open(fileName + ".t16")

    # try opening the results file to check for errors
    try:
        p.moveto(1)
    except:
        print("Error opening post file: " + fileName + ".t16")

    # move to the last increment
    numIncrements = p.increments() # number of increments in the sim
    p.extrapolation("linear") # set extrapolation to linear
    p.moveto(numIncrements - 1) # move to the final increment

    nns = p.node_scalars() # the number of nodal scalars in results

    for i in range(0, nns):
        if(p.node_scalar_label(i) == "Reaction Force X"):
            kCallus = p.node_scalar(nodeID - 1, i)

    # build the fixator stiffness function
    kBaseline = 4600 # N/mm the baseline spring stiffness
    kRet = 20 # N/mm the return spring stiffness, ie the stiffness in the free movement region
    uPretension = 100 / kBaseline # mm, the displacement at the pre-tensioning force of 100 N
    uMax = freeMovement # mm, maximum allowed IFM, 0.25 mm for case A, 1.25 mm for case B
    fMax = 500 - kCallus * uMax # the force applied by the fixator to match a total applied force of 500 N at uMax

    uFree = (100 - fMax + uMax * kBaseline + uPretension * kRet) / (kBaseline - kRet) # mm, displacement at end of free movement region, solving for the intersection of the free movement stiffness region and the baseline stiffness region
    fFree = 100 + kRet * (uFree - uPretension) # N, force at the end of the free movement region

    return uFree, fFree, kBaseline, kRet, kCallus