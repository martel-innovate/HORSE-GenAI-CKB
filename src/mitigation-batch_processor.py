from typing import List

'''
class MitigationBatch():
    def __init__(self, attack_name:str, runs:List[Run]):
        self.attack_name=attack_name
        self.runs=runs
    def score(self)->List[Mitigation]:
        pass
     
class Run():
    def __init__(self,temperature:float,mitigations:List[Mitigation]):
        self.temperature=temperature
        self.mitigations=mitigations
'''

class Mitigation():
    def __init__(self, name:str, priority:int):
        self.name=name
        self.priority=priority
        self.uncertainty:float=0 # 

def score(attack_name:str,ms:List[Mitigation])->List[Mitigation]: 
    #sets the uncertainty field of each mitigation in the input list
    pass

threshold=0 # TODO read from configuration
def mitigation_processor(attack_name:str,ms:List[Mitigation])->List[Mitigation]:
    scored_mitigations=score(attack_name,ms)
    res=[m for m in scored_mitigations if m.uncertainty<threshold]
    return res
