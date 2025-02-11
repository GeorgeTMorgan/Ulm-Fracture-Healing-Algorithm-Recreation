import numpy as np
import matplotlib.pyplot as plt
import os
import subprocess
from subprocess import Popen
import ctypes, sys
import time

import preProcessing
import calcVolumes
import calcAreas
import calcSpring
import readResults
import doFuzzySK
import updateNeighbors
import calcNewMatProps
import writeNewMatProps
np.set_printoptions(threshold=sys.maxsize)



############### Notes ###############

# Edited controlsystem.py in SKFuzzy library - in CrispValueCalculator.defuzz() - 
# comment out Value error - "crisp output cannot be calculated", 
# replace with: return np.zeros(self.sim._array_shape, dtype=np.float64) (ie. return zero)
# because default output should be "no change"

# Visual Studio must be run as administrator

# Must use same version of Python as is used by the version of Marc where py_post and py_mentat are taken froms




############### Inputs and Set-up ###############

simName = 'Ulm2D_v3'

currentIteration = 0
numIterations = 56 # Number of algorithm iterations
IFMs = []

# Input Marc file name, and temp copy file name
fileName = 'ulm2da_nonSep_job1' # select the .dat file, make sure it is in this directory (for now)
newFileName = 'FractureHealing_Temp'

# Input folder to store results
currentSim = r'caseA_nonSeparated'


RBE2nodeID = 2 # free RBE2 node ID
uMax = 0.25 # case A






############### Pre-processing ###############

# Get callus element numbers and subgroups, as well as callus element connectivity dictionary
print("start")
print(simName)
callusElementNumbers, callusSurfaceElements, callusMedullarySurfaceElements, callusBoneSurfaceElements, connectivity, boneElementNumbers, bonePerfusionElements = preProcessing.preProcessing(fileName, newFileName)
areasRelative = calcAreas.calcAreas(fileName, callusElementNumbers+boneElementNumbers)
uFree, fFree, kBaseline, kRet, kCallus0 = calcSpring.calcSpring(fileName, RBE2nodeID, uMax)

np.save(r'callusElements.npy', callusElementNumbers)
np.save(r'boneElements.npy', boneElementNumbers)
np.save(r'bonePerfusionElements.npy', bonePerfusionElements)
np.save(r'callusSurfaceElements.npy', callusSurfaceElements)
np.save(r'callusMedullarySurfaceElements.npy', callusMedullarySurfaceElements)
np.save(r'callusBoneSurfaceElements.npy', callusBoneSurfaceElements)
np.save(r'connectivityElements.npy', connectivity)
np.save(r'areasRelative.npy', areasRelative)
#callusElementNumbers = list(np.load(r'callusElements.npy', allow_pickle='TRUE'))
#callusSurfaceElements = list(np.load(r'callusSurfaceElements.npy', allow_pickle='TRUE'))
#callusMedullarySurfaceElements = list(np.load(r'callusMedullarySurfaceElements.npy', allow_pickle='TRUE'))
#callusBoneSurfaceElements = list(np.load(r'callusBoneSurfaceElements.npy', allow_pickle='TRUE'))
#callusConnectivity = np.load(r'callusConnectivityElements.npy', allow_pickle='TRUE')[()] # formatted as a dict with keys as each callus element ID, and the value as a list of neighboring elements
#IFMs = list(np.load(r'IFMs.npy', allow_pickle='TRUE'))

# first row is E, second in nu
materials = np.zeros((len(callusElementNumbers+boneElementNumbers),2))
materials[:,0] = 3.0
materials[:,1] = 0.3
print("finished loading")
# Initialize healing state variables: woven bone, fibrocartilage, and vascularity (soft tissue concentration is inferred becase Cwb + Cc + Cs = 1)
# Entries are for each element in the same order as callusElementNumbers, each state variable is between 0 and 1
# Initial values are given in Simon et al 2011 - 100% soft tissue (0 woven and 0 cartilage)
stateVariables = np.zeros((len(callusElementNumbers+boneElementNumbers),3))
neighbors = np.zeros((len(callusElementNumbers+boneElementNumbers),3)) # the maximum for each elements neighbors

# Vascularity Initial and Boundary Conditions
# Vascularity is initially zero everywhere, but BCs: 
# Bone contact = 100% neighbor perfusion (except at the tips of the bone where the vessels are damaged
# Outer surface of callus = 30% self perfusion
# Medullary surface of callus = 0% for first 10 days, 30% after 10 days
# Some elements overlap, so set surface first, then bone, then medullary (to enforce the damaged vessel BC)
# initialize self-vascularity
for i in callusSurfaceElements:
    stateVariables[callusElementNumbers.index(i),2] = 0.3

# initialize cortex perfusion
for i in bonePerfusionElements:
    stateVariables[(callusElementNumbers + boneElementNumbers).index(i), 2] = 1

# initialize cortex cBone and cCart
for i in range(len(callusElementNumbers), len(callusElementNumbers+boneElementNumbers)):
    stateVariables[i,0] = 1
    stateVariables[i,1] = 0

## Restart Code
#stateVariables = np.load('combined_method3\stateVariables49.npy', allow_pickle='TRUE')
#materials = np.load('combined_method3\materials49.npy', allow_pickle='TRUE')
#equivalentStrains = np.load('combined_method3\equivalentStrains49.npy', allow_pickle='TRUE')
#hydrostaticStrains = np.load('combined_method3\hydrostaticStrains49.npy', allow_pickle='TRUE')

#neighbors = updateNeighbors.updateNeighbors(stateVariables, neighbors, callusElementNumbers, callusBoneSurfaceElements, callusMedullarySurfaceElements, callusConnectivity, currentIteration)
neighbors = updateNeighbors.updateNeighbors(stateVariables, neighbors, callusElementNumbers, callusBoneSurfaceElements, callusMedullarySurfaceElements, callusSurfaceElements, connectivity, currentIteration, boneElementNumbers, bonePerfusionElements)







################ Processing - Iterative loop ###############

while currentIteration <= numIterations:
    print(simName)
    print("current iteration " + str(currentIteration))
    # run FE
    # VISUAL STUDIO MUST BE RUN AS ADMINISTRATOR FOR THIS TO WORK WITHOUT NEEDING UAC CONFIRMATION
    # ie, if not run as admin, this line will require a manual prompt response every iteration
    subprocess.call([r"C:\Program Files\MSC.Software\Marc\2021.2.0\marc2021.2\tools\run_marc.bat", r"-jid", r"FractureHealing_Temp.dat", r"-back", r"yes", r"-nts", r"4", r"-nte", r"4"])
    print("FE done - current iteration " + str(currentIteration))

    # read IFM and callus element strains
    # the elements are ordered in the same way as callusElementNumbers
    #hydrostaticStrains, equivalentStrains, IFM = readResults.readResults(newFileName, callusElementNumbers, materials, RBE2nodeID, uFree, fFree, uMax, kBaseline, kRet, kCallus0, boneElementNumbers)
    hydrostaticStrains, equivalentStrains, IFM = readResults.readResults(newFileName, callusElementNumbers, materials, RBE2nodeID, boneElementNumbers)
    IFMs.append(IFM)
    print(IFM)
    print("results read - current iteration " + str(currentIteration))

    # do Fuzzy logics
    stateVariables = doFuzzySK.doFuzzySK(callusElementNumbers, hydrostaticStrains, equivalentStrains, stateVariables, neighbors, areasRelative, boneElementNumbers)
    print("fuzzy done - current iteration " + str(currentIteration))

    # reinforce cortex cBone and cCart
    for i in range(len(callusElementNumbers), len(callusElementNumbers+boneElementNumbers)):
        stateVariables[i,0] = 1
        stateVariables[i,1] = 0

    #neighbors = updateNeighbors.updateNeighbors(stateVariables, neighbors, callusElementNumbers, callusBoneSurfaceElements, callusMedullarySurfaceElements, callusConnectivity, currentIteration)
    neighbors = updateNeighbors.updateNeighbors(stateVariables, neighbors, callusElementNumbers, callusBoneSurfaceElements, callusMedullarySurfaceElements, callusSurfaceElements, connectivity, currentIteration, boneElementNumbers, bonePerfusionElements)
    print("neighbors done - current iteration " + str(currentIteration))

    # calc new mat props
    materials = calcNewMatProps.calcNewMatProps(stateVariables, materials, callusElementNumbers, boneElementNumbers)
    print("mat props calc'd - current iteration " + str(currentIteration))

    # write new mat props to both FE files
    writeNewMatProps.writeNewMatProps(newFileName, callusElementNumbers, materials)
    print("mat props written - current iteration " + str(currentIteration))

    # save state of each iteration
    np.save(currentSim + r'\IFMs.npy', IFMs)
    np.save(currentSim + r'\hydrostaticStrains' + str(currentIteration) + '.npy', hydrostaticStrains)
    np.save(currentSim + r'\equivalentStrains' + str(currentIteration) + '.npy', equivalentStrains)
    np.save(currentSim + r'\stateVariables' + str(currentIteration) + '.npy', stateVariables)
    np.save(currentSim + r'\materials' + str(currentIteration) + '.npy', materials)

    currentIteration += 1


print(IFMs)


############### Post-processing ###############
