import numpy as np
import numpy.linalg as la
from py_post import *
#from scipy.interpolate import griddata
#from scipy.interpolate import LinearNDInterpolator

#def readResults(newFileName, callusElementNumbers, matProps, nodeID, uFree, fFree, uMax, kBaseline, kRet, kCallus0, boneElementNumbers):
def readResults(newFileName, callusElementNumbers, matProps, nodeID, boneElementNumbers):

    # create a postpy obj using post_open
    p = post_open(newFileName + ".t16")

    # try opening the results file to check for errors
    try:
        p.moveto(1)
    except:
        print("Error opening post file: " + newFileName + ".t16")

    # move to the last increment
    numIncrements = p.increments() # number of increments in the sim
    p.extrapolation("linear") # set extrapolation to linear
    p.moveto(numIncrements - 1) # move to the final increment

    nns = p.node_scalars() # the number of nodal scalars in results
    nes = p.element_scalars() # the number of element scalars in results

    hydrostaticStrains = [] # contains the hydrostatic strain for each element, the elements are ordered in the same way as callusElementNumbers
    equivalentStrains = [] # contains the equivalent strain for each element, the elements are ordered in the same way as callusElementNumbers

    # read the displacement of the free node (IFM) and the reaction force of the fixed node
    for i in range(0, nns):
        if(p.node_scalar_label(i) == "Displacement X"):
            IFM = p.node_scalar(nodeID - 1, i)
    #    if(p.node_scalar_label(i) == "Reaction Force X"):
    #        kCallus = p.node_scalar(nodeID - 1, i)

    ## calculate the system IFM for an applied force of 500 N using the system stiffness function
    #if (fFree + uFree * kCallus) <= 500: # test whether 500 N applied falls within the free movement or active region of the stiffness
    #    IFM = uFree + ((500 - (fFree + uFree * kCallus)) / (kCallus + kBaseline))
    #else:
    #    IFM = uFree - (((fFree + uFree * kCallus) - 500) / (kCallus + kRet))

    #stretch = IFM # strain scaling factor

    #p.element_sequence(id) - returns the index of the element for the input element id (this is the inverse of p.element_id(index))
    for j in (callusElementNumbers+boneElementNumbers): # callusElementNumbers IDs, not indexing...:
        elNodes = [] # the global node index for the nodes in the element
        nodalDilatational = [] # the dilatational strain at each node in the element
        nodalDistortional = [] # the distortional strain at each node in the element

        ## Find the matProps for the element
        #elYoungs = matProps[callusElementNumbers.index(j),0]
        #elNu = matProps[callusElementNumbers.index(j),1]
        ##for i in range(len(matProps)):
        ##    if matProps[i][0] == ("callus%d" % j):
        ##        elYoungs = matProps[i][1] # the Young's modulus for the element
        ##        elNu = matProps[i][2] # the Poisson's ratio for the element

        # the indexing for the strain scalars will depend on which scalars are selected in Job Results in Marc
        for i in range(0, nes):
            if(p.element_scalar_label(i) == "Minimum Principal Total Strain"):
                elMinStrains = p.element_scalar(j - 1, i) # minus one because the indexing for the elements starts at 0 even though the element id's start at 1...
            elif(p.element_scalar_label(i) == "Intermediate Principal Total Strain"):
                elIntStrains = p.element_scalar(j - 1, i)
            elif(p.element_scalar_label(i) == "Maximum Principal Total Strain"):
                elMaxStrains = p.element_scalar(j - 1, i)
            #if(p.element_scalar_label(i) == "Comp 11 of Total Strain"):
            #    comp11 = p.element_scalar(j - 1, i)
            #elif(p.element_scalar_label(i) == "Comp 22 of Total Strain"):
            #    comp22 = p.element_scalar(j - 1, i)
            #elif(p.element_scalar_label(i) == "Comp 33 of Total Strain"):
            #    comp33 = p.element_scalar(j - 1, i)
            #elif(p.element_scalar_label(i) == "Comp 12 of Total Strain"):
            #    comp12 = p.element_scalar(j - 1, i)
            #elif(p.element_scalar_label(i) == "Comp 23 of Total Strain"):
            #    comp23 = p.element_scalar(j - 1, i)
            #elif(p.element_scalar_label(i) == "Comp 31 of Total Strain"):
            #    comp31 = p.element_scalar(j - 1, i)

        # calculate dilatational and deviatoric strains at each node of the current element
        # there are 3 options for calculating equivalent strain:
        #   1. (Incorrect) octahedral strain - as used by Gubing and Simon
        #   2. Equivalent strain derived from work conjugate of von Mises stress
        #   3. Equivalent strain derived similarly to von Mises stress - includes Poisson's ratio

        # All nodes have the centroid value, so only need to take one node
        #for i in range(len(elMinStrains)):
        #elNodes.append(elMinStrains[0].id) # add the current node's id to the list for the current element

        # calculate hydrostatic strain at the current node of the current element
        #elHydroStrain = (comp11[0].value + comp22[0].value + comp33[0].value)/3 # this is hydrostatic strain (1/3 volumetric strain), as used by Simon and Gubing
        elHydroStrain = (elMinStrains[0].value + elIntStrains[0].value + elMaxStrains[0].value)/3
        #elHydroStrain = elHydroStrain * stretch

        # build distortional strain tensor (log strain tensor - hydrostatic strain)
        #distortionalTensor = np.array([[comp11[0].value-elHydroStrain,comp12[0].value,comp31[0].value],
        #                               [comp12[0].value,comp22[0].value-elHydroStrain,comp23[0].value],
        #                               [comp31[0].value,comp23[0].value,comp33[0].value-elHydroStrain]])

        # calculate equivalent strain using the 3 methods described above
        # method 1 - Octahedral Shear Strain
        #equivStrain = (0.5*((comp11[i].value - comp22[i].value)**2 + (comp22[i].value - comp33[i].value)**2 + (comp11[i].value - comp33[i].value)**2 + 6*(comp12[i].value**2 + comp31[i].value**2 + comp23[i].value**2)))**0.5
        #elEquivStrain = (1.5*np.einsum('ij,ij', distortionalTensor, distortionalTensor))**0.5
        elEquivStrain = (0.5*((elMinStrains[0].value - elIntStrains[0].value)**2 + (elIntStrains[0].value - elMaxStrains[0].value)**2 + (elMaxStrains[0].value - elMinStrains[0].value)**2))**0.5
        #elEquivStrain = elEquivStrain * stretch

        # method 2
        # equivStrain = ((2/3)*np.einsum('ij,ij', distortionalTensor, distortionalTensor))**0.5

        # method 3
        # factor of 1.3 to make this strain calc equal to that of method 1 for connective tissue (nu = 0.3)
        #equivStrain = (1.3/(1 + elNu))*(1.5*np.einsum('ij,ij', distortionalTensor, distortionalTensor))**0.5
        #elEquivStrain = (1.3/(1 + elNu))*(0.5*((elMinStrains[0].value - elIntStrains[0].value)**2 + (elIntStrains[0].value - elMaxStrains[0].value)**2 + (elMaxStrains[0].value - elMinStrains[0].value)**2))**0.5

        # add the nodal strain values to the list for the current element
        #nodalDilatational.append(hydroStrain)
        #nodalDistortional.append(equivStrain)

        ## linearly interpolate the strains at the centroid of the current element
        ## can change in Job Results to get element values at centroid rather than all points, would remove need for this block of code - doesn't actually change results?
        #points = np.zeros(shape=(len(elNodes), 3))
        #for i in range(len(elNodes)):
        #    points[i,0] = p.node(elNodes[i]-1).x # -1 because INDEXING starts at 0 even though IDs start at 1...
        #    points[i,1] = p.node(elNodes[i]-1).y
        #    points[i,2] = p.node(elNodes[i]-1).z
        #centroid = np.mean(points, axis=0)

        #elHydrostatic = griddata(points, nodalDilatational, centroid)[0] # index zero to return a value rather than a 1x1 array
        #elEquivalent = griddata(points, nodalDistortional, centroid)[0] # index zero to return a value rather than a 1x1 array

        hydrostaticStrains.append(elHydroStrain)
        equivalentStrains.append(elEquivStrain)

    p.close()

    return hydrostaticStrains, equivalentStrains, IFM



