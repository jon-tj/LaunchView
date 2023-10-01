
phases = [
    'Rocket on launch pad',
    'Waiting for launch',
    'Burn phase',
    'Burnout',
    'Drogue chute deployed',
    'Main chute deployed',
    'Rocket has landed'
]
curr_phase=0

def get_phase():
    return phases[curr_phase]

def next_phase():
    global curr_phase
    curr_phase+=1
    return get_phase()