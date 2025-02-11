def writeNewMatProps(filename, callusElementNumbers, materials):
    #with open(filename + '.txt', 'r') as f:
    with open(filename + '.dat', 'r') as f:
        searchlines = f.readlines()

    for i, line in enumerate(searchlines):
        # find all materials in the .dat file by "isotropic"
        if "isotropic" in line: 
            if searchlines[i+2].split()[4][1:7] == 'callus':
                # get the element ID for the current material
                elID = int(searchlines[i+2].split()[4][7:])

                # format the updated material properties
                updatedE = materials[callusElementNumbers.index(elID),0]
                updatedE = '{:.15e}'.format(updatedE)
                updatedE = updatedE[:-4] + updatedE[-3] + updatedE[-1]
                updatedNu = materials[callusElementNumbers.index(elID),1]
                updatedNu = '{:.15e}'.format(updatedNu)
                updatedNu = updatedNu[:-4] + updatedNu[-3] + updatedNu[-1]

                # edit the relevant line in the file
                editLine = searchlines[i+3].split()
                editLine[0] = updatedE
                editLine[1] = updatedNu
                editLine = ' ' + ' '.join(editLine) + '\n'

                # replace the line in the file
                searchlines[i+3] = editLine

    with open(filename + '.dat', 'w') as f:
        updatedFile = ''.join(searchlines)
        f.write(updatedFile)
