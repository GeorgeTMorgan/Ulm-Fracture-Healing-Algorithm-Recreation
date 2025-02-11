import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

def doFuzzySK(callusElementNumbers, hydrostaticStrains, equivalentStrains, stateVariablesInput, neighborsInput, volumesRelative, boneElementNumbers):


    stateVariables = stateVariablesInput
    neighbors = neighborsInput

    # Define antecedent fuzzy sets and membership functions
    Perfusion = ctrl.Antecedent(np.arange(0, 120, 20), 'Perfusion')
    Cartilage = ctrl.Antecedent(np.arange(0, 120, 20), 'Cartilage')
    Bone = ctrl.Antecedent(np.arange(0, 120, 20), 'Bone')
    nBone = ctrl.Antecedent(np.arange(0, 120, 20), 'nBone')
    nPerfusion = ctrl.Antecedent(np.arange(0, 120, 20), 'nPerfusion')

    Perfusion['low'] = Cartilage['low'] = Bone['low'] = nBone['low'] = nPerfusion['low'] = fuzz.trapmf(Perfusion.universe, [0, 0, 20, 40])
    Perfusion['medium'] = Cartilage['medium'] = Bone['medium'] = nBone['medium'] = nPerfusion['medium'] = fuzz.trapmf(Perfusion.universe, [20, 40, 60, 80])
    Perfusion['high'] = Cartilage['high'] = Bone['high'] = nBone['high'] = nPerfusion['high'] = fuzz.trapmf(Perfusion.universe, [60, 80, 100, 100])

    Distortional = ctrl.Antecedent(np.arange(0, 20.01, 0.01), 'Distortional')
    Distortional['aboutZero'] = fuzz.trapmf(Distortional.universe, [0, 0, 0.01, 0.05])
    Distortional['low'] = fuzz.trapmf(Distortional.universe, [0.01, 0.05, 5, 9])
    Distortional['medium'] = fuzz.trapmf(Distortional.universe, [5, 9, 14, 18])
    Distortional['destructive'] = fuzz.trapmf(Distortional.universe, [14, 18, 20, 20])

    Dilatational = ctrl.Antecedent(np.arange(-8, 8.01, 0.01), 'Dilatational')
    Dilatational['negDestructive'] = fuzz.trapmf(Dilatational.universe, [-8, -8, -6, -4])
    Dilatational['negMedium'] = fuzz.trapmf(Dilatational.universe, [-6, -4, -0.9, -0.8])
    Dilatational['negLow'] = fuzz.trapmf(Dilatational.universe, [-0.9, -0.8, -0.03, -0.01])
    Dilatational['aboutZero'] = fuzz.trapmf(Dilatational.universe, [-0.03, -0.01, 0.01, 0.03])
    Dilatational['posLow'] = fuzz.trapmf(Dilatational.universe, [0.01, 0.03, 0.8, 0.9])
    Dilatational['posMedium'] = fuzz.trapmf(Dilatational.universe, [0.8, 0.9, 4, 6])
    Dilatational['posDestructive'] = fuzz.trapmf(Dilatational.universe, [4, 6, 8, 8])

    # Define consequent fuzzy sets and membership functions
    ChangeInPerfusion = ctrl.Consequent(np.arange(-10, 10.5, 0.5), 'ChangeInPerfusion')
    ChangeInPerfusion['decrease'] = fuzz.trapmf(ChangeInPerfusion.universe, [-10, -10, -7.5, -2.5])
    ChangeInPerfusion['stay'] = fuzz.trapmf(ChangeInPerfusion.universe, [-7.5, -2.5, 2.5, 7.5])
    ChangeInPerfusion['increase'] = fuzz.trapmf(ChangeInPerfusion.universe, [2.5, 7.5, 10, 10])

    ChangeInCartilage = ctrl.Consequent(np.arange(-30, 10, 5), 'ChangeInCartilage')
    ChangeInCartilage['decrease'] = fuzz.trapmf(ChangeInCartilage.universe, [-30, -30, -5, 0])
    ChangeInCartilage['stay'] = fuzz.trimf(ChangeInCartilage.universe, [-5, 0, 5])
    ChangeInCartilage['increase'] = fuzz.trimf(ChangeInCartilage.universe, [0, 5, 5])

    ChangeInBone = ctrl.Consequent(np.arange(-30, 35, 5), 'ChangeInBone')
    ChangeInBone['decrease'] = fuzz.trapmf(ChangeInBone.universe, [-30, -30, -25, -5])
    ChangeInBone['stay'] = fuzz.trapmf(ChangeInBone.universe, [-25, -5, 5, 25])
    ChangeInBone['increase'] = fuzz.trapmf(ChangeInBone.universe, [5, 25, 30, 30])

    # Define rules
    # Need to make rules consistent in the NOT vs OR usage (maybe fuzzySK handles automatically - run a quick test - test confirms it does not, but maybe neither does the MATLAB toolbox...)
    R1 = ctrl.Rule(antecedent=(Perfusion['low'] & (nPerfusion['medium'] | nPerfusion['high']) & (~Dilatational['negDestructive']) & (Distortional['aboutZero'] | Distortional['low'])), 
                   consequent=(ChangeInPerfusion['increase']), 
                   label='R1')
    R2 = ctrl.Rule(antecedent=((Perfusion['medium'] | Perfusion['high']) & nPerfusion['high'] & (~Dilatational['negDestructive']) & (Distortional['aboutZero'] | Distortional['low'])), 
                   consequent=(ChangeInPerfusion['increase']), 
                   label='R2')
    R3 = ctrl.Rule(antecedent=(Perfusion['high'] & nBone['high'] & Cartilage['low'] & Distortional['low'] & (Dilatational['negLow'] | Dilatational['posLow'])), 
                   consequent=(ChangeInBone['increase']), 
                   label='R3')
    R4 = ctrl.Rule(antecedent=((~Distortional['destructive']) & (Dilatational['negMedium'] | Dilatational['negLow'])), 
                   consequent=(ChangeInCartilage['increase']), 
                   label='R4')
    R5 = ctrl.Rule(antecedent=((~nBone['low']) & (~Cartilage['low']) & (~Distortional['destructive']) & (Dilatational['negMedium'] | Dilatational['negLow'] | Dilatational['aboutZero'] | Dilatational['posLow'])), 
                   consequent=(ChangeInBone['increase'], ChangeInCartilage['decrease']), 
                   label='R5')
    R6 = ctrl.Rule(antecedent=((~Perfusion['low']) & Bone['high'] & nBone['high'] & Cartilage['low'] & (Dilatational['negLow'] | Dilatational['posLow']) & (Distortional['aboutZero'] | Distortional['low'])), 
                   consequent=(ChangeInBone['increase'], ChangeInCartilage['decrease']), 
                   label='R6')
    R7 = ctrl.Rule(antecedent=(Dilatational['negDestructive'] | Dilatational['posDestructive']), 
                   consequent=(ChangeInPerfusion['decrease'], ChangeInCartilage['decrease'], ChangeInBone['decrease']), 
                   label='R7')
    R8 = ctrl.Rule(antecedent=(Distortional['destructive']), 
                   consequent=(ChangeInPerfusion['decrease'], ChangeInCartilage['decrease'], ChangeInBone['decrease']), 
                   label='R8')


    # Create Fuzzy System
    healing_ctrl = ctrl.ControlSystem([R1, R2, R3, R4, R5, R6, R7, R8])
    healing = ctrl.ControlSystemSimulation(healing_ctrl)

    # Loop for each callus element
    for i in range(len(callusElementNumbers+boneElementNumbers)):

        # Set antecedents values
        healing.inputs({'Cartilage': stateVariables[i,1]*100,
                        'Bone': stateVariables[i,0]*100,
                        'nBone': neighbors[i,0]*100,
                        'Perfusion': stateVariables[i,2]*100,
                        'nPerfusion': neighbors[i,2]*100,
                        'Distortional': min(equivalentStrains[i]*100,20), # if distortional strain is outside of the universe of discourse, it has to be brought back to the maximum of the universe of discourse
                        'Dilatational': max(min(hydrostaticStrains[i]*100,8),-8)}) # bring dilatational strain into the universe of discourse

        # Perform Mamdani inference and update state variables
        # Edited controlsystem.py in SKFuzzy library - in CrispValueCalculator.defuzz() - 
        # comment out Value error - "crisp output cannot be calculated", 
        # instead return np.zeros(self.sim._array_shape, dtype=np.float64) (ie. return zero)
        # because default output should be "no change"
        healing.compute()
        
        stateVariables[i,0] = stateVariables[i,0] + 0.01 * float(healing.output['ChangeInBone']) * ((1/volumesRelative[i])**(1/2)) # this is actually areasRelative in 2D sim
        stateVariables[i,1] = stateVariables[i,1] + 0.01 * float(healing.output['ChangeInCartilage']) * ((1/volumesRelative[i])**(1/2))
        stateVariables[i,2] = stateVariables[i,2] + 0.01 * float(healing.output['ChangeInPerfusion']) * ((1/volumesRelative[i])**(1/2))

    stateVariables = np.where(stateVariables <= 1, stateVariables, 1)
    stateVariables = np.where(stateVariables >= 0, stateVariables, 0)

    return stateVariables

