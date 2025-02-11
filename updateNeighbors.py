import numpy as np

#def updateNeighbors(stateVariables, neighbors, callusElementNumbers, callusBoneSurfaceElements, callusMedullarySurfaceElements, callusConnectivity, currentIteration):
def updateNeighbors(stateVariables, neighbors, callusElementNumbers, callusBoneSurfaceElements, callusMedullarySurfaceElements, callusSurfaceElements, connectivity, currentIteration, boneElementNumbers, bonePerfusionElements):

    # go through all callus elements and populate the neighbors matrix
    for i in range(len(callusElementNumbers+boneElementNumbers)):
        elNeighbors = connectivity.get((callusElementNumbers+boneElementNumbers)[i])
        idx = [(callusElementNumbers+boneElementNumbers).index(j) for j in elNeighbors]

        # nPerfusions
        nPerfusions = [stateVariables[k,2] for k in idx]
        neighbors[i,2] = max(nPerfusions)
        # nBones
        nBones = [stateVariables[l,0] for l in idx]
        neighbors[i,0] = max(nBones)
        # nCartilage
        nCarts = [stateVariables[m,1] for m in idx]
        neighbors[i,1] = max(nCarts)

    # re-enforce BCs here
    for i in callusBoneSurfaceElements:
        neighbors[callusElementNumbers.index(i),2] = 1
        # need to set nBone of callusBoneSurfaceElements to 1
        neighbors[callusElementNumbers.index(i),0] = 1

    for i in callusSurfaceElements:
        neighbors[callusElementNumbers.index(i),2] = 1

    if currentIteration < 10:
        for i in callusMedullarySurfaceElements:
            neighbors[callusElementNumbers.index(i),2] = 0
    else:
        for i in callusMedullarySurfaceElements:
            neighbors[callusElementNumbers.index(i),2] = 0.3

    return neighbors
