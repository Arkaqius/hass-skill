from enum import Enum,auto
from fuzzywuzzy import fuzz

class HMI_Candidates:
    def __init__(self,entity,ratio):
        self.entity = entity
        self.ratio = ratio

    @staticmethod
    def find_candidates(query,list_of_entitities):
        '''Function to find list of candidates'''

        candidates = [] #Var to return
        for entity in list_of_entitities:   
            ratio = fuzz.ratio(query,entity['entity_id'])
            if ratio > 50:
                candidates.append(HMI_Candidates(entity,ratio))

        return candidates

class HMI_dlg_rtn(Enum):
    UNKNOWN    = auto()
    SUCCESS    = auto()
    NO_RESPONSE = auto()
    #Lights returns
    UF_BRIGHTNESS    = auto()