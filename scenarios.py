scenario_1 = {
    "name": "QualityControl",
    "states": ['High Quality', 'Medium Quality', 'Low Quality'], 
    "actions": ['Buy', 'Dont Buy'], #
    "prior": {'High Quality': 0.5, 'Medium Quality': 0.2, 'Low Quality': 0.3}, 
    "u_s": {
        'Buy': {'High Quality': 10, 'Medium Quality': 10, 'Low Quality': 10},
        'Dont Buy': {'High Quality': 0, 'Medium Quality': 0, 'Low Quality': 0}
    }, 
    "u_r": {
        'Buy': {'High Quality': 5, 'Medium Quality': 1, 'Low Quality': -10},
        'Dont Buy': {'High Quality': 0, 'Medium Quality': 0, 'Low Quality': 0}
    } 
}


scenario_2 = {
    "name": "SimpleBinaryGame",
    "states": ['Good', 'Bad'],
    "actions": ['Accept', 'Reject'],
    "prior": {'Good': 0.5, 'Bad': 0.5},
    "u_s": {
        'Accept': {'Good': 1, 'Bad': 1},
        'Reject': {'Good': 0, 'Bad': 0}
    },
    "u_r": {
        'Accept': {'Good': 1, 'Bad': -1},
        'Reject': {'Good': 0, 'Bad': 0}
    }
}

all_scenarios = [scenario_1, scenario_2]