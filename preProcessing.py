import numpy as np
from shutil import copyfile

def preProcessing(fileName, newFileName):
    
    # create copy file to preserve original .dat files
    copyfile(fileName + '.dat', newFileName + '.dat')

    callusElements = []
    boneElements = []
    bonePerfusionElements = []
    callusSurfaceElements = []
    callusMedullarySurfaceElements = []
    callusBoneSurfaceElements = []
    connectivityNodes = [] # 2D array, elementID and node IDs in each row
    allNodes = [] # all the nodes from callusConnectivityNodes listed in order, including duplicates
    connectivityElements = {}
    connectivityNodesDict = {}

    # opens the new .dat file and reads in materials data and the element numbers for the callus (the set, not material... can't find element numbers for the material)
    with open(newFileName + '.dat', 'r') as f:
        searchlines = f.readlines()
    for i, line in enumerate(searchlines):

        if "define              element             set                 callus\n" in line:
            callusElementsLowerBound = int(searchlines[i+1].split()[0])
            callusElementsUpperBound = int(searchlines[i+1].split()[2])
            callusElements = list(range(callusElementsLowerBound,callusElementsUpperBound + 1))

        if "define              element             set                 bone\n" in line:
            boneElementsLowerBound = int(searchlines[i+1].split()[0])
            boneElementsUpperBound = int(searchlines[i+1].split()[2])
            boneElements = list(range(boneElementsLowerBound,boneElementsUpperBound + 1))

        if "define              element             set                 bonePerfusion\n" in line:
            j = 1
            while searchlines[i+j].split()[-1] == "c": # while there is another line (current line ends in "c")
                for k in range(len(searchlines[i+j].split()) - 1):
                    bonePerfusionElements.append(int(searchlines[i+j].split()[k])) # append all the element numbers in the line (but need to leave out the "c"
                j += 1
            for k in range(len(searchlines[i+j].split())): # then do the last line (doesn't end in "c", even if a full line
                bonePerfusionElements.append(int(searchlines[i+j].split()[k]))

        if "define              element             set                 callusSurfaceElements\n" in line:
            j = 1
            while searchlines[i+j].split()[-1] == "c": # while there is another line (current line ends in "c")
                for k in range(len(searchlines[i+j].split()) - 1):
                    callusSurfaceElements.append(int(searchlines[i+j].split()[k])) # append all the element numbers in the line (but need to leave out the "c"
                j += 1
            for k in range(len(searchlines[i+j].split())): # then do the last line (doesn't end in "c", even if a full line
                callusSurfaceElements.append(int(searchlines[i+j].split()[k]))

        if "define              element             set                 callusMedullarySurfaceElements\n" in line:
            j = 1
            while searchlines[i+j].split()[-1] == "c": # while there is another line (current line ends in "c")
                for k in range(len(searchlines[i+j].split()) - 1):
                    callusMedullarySurfaceElements.append(int(searchlines[i+j].split()[k])) # append all the element numbers in the line (but need to leave out the "c"
                j += 1
            for k in range(len(searchlines[i+j].split())): # then do the last line (doesn't end in "c", even if a full line
                callusMedullarySurfaceElements.append(int(searchlines[i+j].split()[k]))

        if "define              element             set                 callusBoneSurfaceElements\n" in line:
            j = 1
            while searchlines[i+j].split()[-1] == "c": # while there is another line (current line ends in "c")
                for k in range(len(searchlines[i+j].split()) - 1):
                    callusBoneSurfaceElements.append(int(searchlines[i+j].split()[k])) # append all the element numbers in the line (but need to leave out the "c"
                j += 1
            for k in range(len(searchlines[i+j].split())): # then do the last line (doesn't end in "c", even if a full line
                callusBoneSurfaceElements.append(int(searchlines[i+j].split()[k]))

    # need a new for loop because callusElements needs to be created before building callusConnectivity
    for i, line in enumerate(searchlines):
        elConnectivity = []

        if "connectivity" in line:
            if int(searchlines[i+2].split()[0]) in callusElements:
                elConnectivity.append(int(searchlines[i+2].split()[0]))
                elConnectivity.append(int(searchlines[i+2].split()[2]))
                allNodes.append(int(searchlines[i+2].split()[2]))
                elConnectivity.append(int(searchlines[i+2].split()[3]))
                allNodes.append(int(searchlines[i+2].split()[3]))
                elConnectivity.append(int(searchlines[i+2].split()[4]))
                allNodes.append(int(searchlines[i+2].split()[4]))
                elConnectivity.append(int(searchlines[i+2].split()[5]))
                allNodes.append(int(searchlines[i+2].split()[5]))
                connectivityNodes.append(elConnectivity)

                connectivityNodesDict[elConnectivity[0]] = set(elConnectivity[1:])

            if int(searchlines[i+2].split()[0]) == boneElements[0]:
                for j in range(len(boneElements)):
                    elConnectivity.append(int(searchlines[i+2+j].split()[0]))
                    elConnectivity.append(int(searchlines[i+2+j].split()[2]))
                    allNodes.append(int(searchlines[i+2+j].split()[2]))
                    elConnectivity.append(int(searchlines[i+2+j].split()[3]))
                    allNodes.append(int(searchlines[i+2+j].split()[3]))
                    elConnectivity.append(int(searchlines[i+2+j].split()[4]))
                    allNodes.append(int(searchlines[i+2+j].split()[4]))
                    elConnectivity.append(int(searchlines[i+2+j].split()[5]))
                    allNodes.append(int(searchlines[i+2+j].split()[5]))
                    connectivityNodes.append(elConnectivity)

                    connectivityNodesDict[elConnectivity[0]] = set(elConnectivity[1:])
                    elConnectivity = []

    # now sort through callusConnectivityNodes and use it to populate callusConnectivityElements
    numberNodesForANeighbor = 2 # how many common nodes defines a neighboring element? 1 (includes 'diagonal' elements) or 2 (adjacent elements which share an edge) or 3 (adjacent elements which share a face)
    for elID, nodeSet in connectivityNodesDict.items(): # loop through the dictionary
        neighborElIDs = [] # list of neighbor elements

        # Only immediate neighbors
        for checkEl, checkNodeSet in connectivityNodesDict.items(): # loop through the same dictionary again
            if len(nodeSet.intersection(checkNodeSet)) >= numberNodesForANeighbor:
                neighborElIDs.append(checkEl)
        
        neighborElIDs.remove(elID) # each element will have added itself as a neighbor
        connectivityElements[elID] = neighborElIDs # add the list of neighbors to the dictionary

    return callusElements, callusSurfaceElements, callusMedullarySurfaceElements, callusBoneSurfaceElements, connectivityElements, boneElements, bonePerfusionElements
