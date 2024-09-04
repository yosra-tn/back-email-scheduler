from enum import Enum

class TypeOccurence(str, Enum):
    mensuel = "mensuel"
    bimestriel = "bimestriel"
    trimestriel = "trimestriel"
    annuel = "annuel"
