from enum import Enum

class MedicalHistoryCategory(str, Enum):
    CHRONIC_CONDITION = "CHRONIC_CONDITION"
    ALLERGY = "ALLERGY"
    SURGERY = "SURGERY"
    FAMILY_HISTORY = "FAMILY_HISTORY"
 
