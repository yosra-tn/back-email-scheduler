import uuid
from uuid import UUID
from fastapi import HTTPException
from sqlalchemy.orm import Session
from my_db import models, schemas
from my_db.models import Rappel


def get_user_by_email(db: Session, email: str):
    result= db.query(models.User).filter(models.User.email == email).first()
    return result
def get_users(db: Session, skip: int = 0, limit: int = 100):
    result= db.query(models.User).offset(skip).limit(limit).all()
    return result
def create_user(db: Session, user: schemas.UserCreate):
    db_user= models.User(email=user.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
def get_echeances_by_email(db: Session,email: str):
    user = get_user_by_email(db,email)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    result = db.query(models.Echeance).filter(models.Echeance.owner_id == user.id).all()
    return result
def create_user_echeance(db: Session, echeance: schemas.EcheanceCreate, user_email:str, rappel_envoye=False):
    user= get_user_by_email(db,user_email)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    db_echeance = models.Echeance(**echeance.model_dump(), owner_id=user.id)
    db.add(db_echeance)
    db.commit()
    db.refresh(db_echeance)

    db_rappel = Rappel(id=uuid.uuid4(), rappel_envoye=rappel_envoye, idEcheance=db_echeance.id)
    db.add(db_rappel)
    db.commit()
    return db_echeance

def update_user_echeance(db:Session,echeance_update:schemas.EcheanceUpdate,echeance_id:UUID):
    db_echeance = db.query(models.Echeance).filter(models.Echeance.id == echeance_id).first()
    if db_echeance is None:
        raise HTTPException(status_code=404, detail="Echeance not found")
    for key,value in echeance_update.model_dump().items():
        setattr(db_echeance, key, value)
    db.commit()
    db.refresh(db_echeance)
    return db_echeance

def delete_user_echeance(db:Session,echeance_id:UUID):
    db_echeance = db.query(models.Echeance).filter(models.Echeance.id == echeance_id).first()
    if db_echeance is None:
        raise HTTPException(status_code=404, detail="Echeance not found")
    db.delete(db_echeance)
    db.commit()
    return db_echeance


def make_rappel_sent(db: Session,rappel_id:UUID):
    db_rappel = db.query(models.Rappel).filter(models.Rappel.id == rappel_id).first()
    if db_rappel is None:
        raise HTTPException(status_code=404, detail="Rappel not found")
    db_rappel.rappel_envoye = True
    db.commit()
    return db_rappel

def delete_user(db: Session, user_id: UUID):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        return None
    db.delete(db_user)
    db.commit()
    return db_user

def delete_rappel_by_id_echeance(db :Session, echeance_id: UUID):
    db_rappel = db.query(models.Rappel).filter(models.Rappel.idEcheance == echeance_id).first()
    if db_rappel is None:
        return None
    db.delete(db_rappel)
    db.commit()
    return db_rappel

