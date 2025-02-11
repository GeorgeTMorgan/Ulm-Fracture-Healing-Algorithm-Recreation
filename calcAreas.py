import numpy as np
import numpy.linalg as la
from py_post import *

def calcAreas(fileName, callusElementNumbers):

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

    areasRelative = [] # contains the volume of each element, divided by the mean volume, the elements are ordered in the same way as callusElementNumbers

    for j in callusElementNumbers: # callusElementNumbers IDs, not indexing...

        nodes = p.element(j-1).items

        points = np.zeros(shape=(3, 4))

        for i in range(4):
            points[0, i] = p.node(nodes[i]-1).x # -1 because INDEXING starts at 0 even though IDs start at 1...
            points[1, i] = p.node(nodes[i]-1).y
            points[2, i] = 1

        elArea = 0.5 * abs(la.norm(np.cross((points[:,2] - points[:,0]),(points[:,3] - points[:,1])))) # area of a quadrilateral is equal to half the magnitude of the cross product of the two diagonals

        areasRelative.append(elArea)

    areasRelative = areasRelative/np.mean(areasRelative)

    p.close()

    return areasRelative