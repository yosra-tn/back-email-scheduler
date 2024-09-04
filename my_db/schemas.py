
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, UUID4

from my_db.typeOccurence import TypeOccurence

class EcheanceBase(BaseModel):
    description:str
    dateEcheance:datetime
    dateRappel:datetime
    typeOccurence: TypeOccurence

class EcheanceCreate(EcheanceBase): #valider les données avant de les insérer dans la base de données.
    pass
class Echeance(EcheanceBase):
    id:UUID4
    owner_id: UUID4

class EcheanceUpdate(EcheanceBase):
    description: Optional[str] = None
    dateEcheance: Optional[datetime] = None
    dateRappel: Optional[datetime] = None
    typeOccurence: Optional[TypeOccurence] = None

    class Config:
        orm_mode = True
class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    pass

class User(UserBase):
    id: UUID4
    echeances: list[Echeance] = []

    class Config:
        orm_mode = True

