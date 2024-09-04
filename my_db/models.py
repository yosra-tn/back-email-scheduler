import uuid
from sqlalchemy import Column, String, DateTime, Enum, ForeignKey, Boolean

from sqlalchemy.orm import relationship

from my_db.database import Base
from sqlalchemy.dialects.postgresql import UUID

from my_db.typeOccurence import TypeOccurence

class User(Base):
    __tablename__ = 'Users'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    email = Column(String, unique=True, index=True)

    echeances = relationship("Echeance", back_populates="owner")


class Echeance(Base):
    __tablename__ = 'Echeances'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    description = Column(String, index=True)
    dateEcheance = Column(DateTime, index=True)
    dateRappel = Column(DateTime, index=True)
    typeOccurence = Column(Enum(TypeOccurence, name="typeoccurence"), index=True)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("Users.id"))

    owner = relationship("User", back_populates="echeances")
    rappels = relationship("Rappel", back_populates="echeance")
class Rappel(Base):
    __tablename__ = 'Rappels'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    rappel_envoye = Column(Boolean, default=False)
    idEcheance = Column(UUID(as_uuid=True), ForeignKey("Echeances.id"))

    echeance = relationship("Echeance", back_populates="rappels")
