import numpy as np

def calcNewMatProps(stateVariables, materials, callusElementNumbers, boneElementNumbers):

    # Tissue type material properties (Young's Modulus E and Poisson's Ratio nu)
    # From Simon et al 2011 and Engelhardt 2021 (same mat props)
    # Alternate mat props (with actual sources rather than made-up numbers) available from Wehner 2014 (but for rats)
    # lb = lamellar bone, wb = woven bone, c = fibrocartilage, s = soft/connective tissue
    # Don't actually use lamellar bone here, it's just the mat prop for the bone in the FE model, not included in callus

    # E_lb = 10000
    E_wb = 4000 
    E_c = 200
    E_s = 3
    # Nu_lb = 0.36 
    Nu_wb = 0.36
    Nu_c = 0.45
    Nu_s = 0.3 

    # def func to calculate E and nu based on rule of mixture - new rule of mixture in Engelhardt supp mat
    # code in both methods so you can choose later (old vs new) (start with old)

    #newE = np.zeros(stateVariables.shape[0])
    #newNu = np.zeros(stateVariables.shape[0])

    for i in range(stateVariables.shape[0]):
        #newE[i] = E_wb*(stateVariables[i,0]**3) + E_c*(stateVariables[i,1]**3) + E_s*((1 - stateVariables[i,0] - stateVariables[i,1])**3)
        #newNu[i] = Nu_wb*stateVariables[i,0] + Nu_c*stateVariables[i,1] + Nu_s*(1 - stateVariables[i,0] - stateVariables[i,1])
        materials[i,0] = E_wb*(stateVariables[i,0]**3) + E_c*(stateVariables[i,1]**3) + E_s*((1 - stateVariables[i,0] - stateVariables[i,1])**3)
        materials[i,1] = Nu_wb*stateVariables[i,0] + Nu_c*stateVariables[i,1] + Nu_s*(1 - stateVariables[i,0] - stateVariables[i,1])

    for i in range(len(callusElementNumbers), len(callusElementNumbers+boneElementNumbers)):
        materials[i,0] = 10000
        materials[i,1] = 0.36

    return materials

