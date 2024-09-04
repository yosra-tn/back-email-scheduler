import smtplib
from datetime import date
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List
from uuid import UUID

from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI, Depends,HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session
from my_db import crud, models, schemas
from my_db.database import engine, sessionLocal
from starlette.middleware.cors import CORSMiddleware
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logging.getLogger('apscheduler').setLevel(logging.DEBUG)

def send_email(email_to:str,subject:str,msgBody:str):
    """Envoie un email au destinataire spécifié."""
    # Configuration de l'email
    global server
    sender_email = "yosra.abid.tn@gmail.com"
    receiver_email = email_to
    password = "suxfzmdbxpclsozt"

    #Creation du message
    msg=MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject']=subject

    #Corps du message
    body = msgBody
    msg.attach(MIMEText(body, 'plain'))

    try:
        #connexion au serveur smtp de gmail
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        logging.info("Email envoyé avec succès")
    except smtplib.SMTPAuthenticationError:
        logging.error("Erreur d'authentification SMTP : Vérifiez l'e-mail et le mot de passe.")
    except smtplib.SMTPException as e:
        logging.error(f"Erreur SMTP lors de l'envoi de l'email: {e}")
    except Exception as e:
        logging.error(f"Erreur générale lors de l'envoi de l'email: {e}")
    finally:
        try:
            server.quit()
        except Exception as e:
            logging.error(f"Erreur lors de la fermeture de la connexion SMTP : {e}")
def scheduler_task():
    """Tâche planifiée pour vérifier les échéances et envoyer des rappels:JOB"""
    logging.info("Exécution de la tâche planifiée.")
    db=sessionLocal()
    try:
        today=date.today()
        logging.info(f"Date actuelle pour vérification des échéances : {today}")
        echeances=db.query(models.Echeance).filter(func.date(models.Echeance.dateRappel)==today).all()
        logging.info(f"Nombre d'échéances trouvées : {len(echeances)}")
        rappels=[]
        for echeance in echeances:
            rappel=db.query(models.Rappel).filter(models.Rappel.idEcheance==echeance.id).all()
            rappels.extend(rappel)

        logging.info(f"Nombre de rappels trouvés : {len(rappels)}")
        for rappel in rappels:
            rappel_echeance=db.query(models.Echeance).filter(models.Echeance.id==rappel.idEcheance).first()
            user_echeance=db.query(models.User).filter(models.User.id==rappel_echeance.owner_id).first()


            if user_echeance and rappel_echeance:
                logging.info(f"Envoi d'email à {user_echeance.email} pour l'échéance {rappel_echeance.description}.")
                send_email(user_echeance.email, "Rappel d'Échéance",
                           f"Bonjour, vous avez une échéance  {rappel_echeance.description} prévue le {rappel_echeance.dateRappel}.")
                crud.make_rappel_sent(db, rappel.id)
                logging.info(f"Marqué comme envoyé pour rappel ID {rappel.id}")
    except Exception as e:
        logging.error(f"Erreur lors de l'exécution de la tâche planifiée : {e}")
    finally:
        db.close()
        logging.info("Fin de l'exécution de la tâche planifiée.")

# Fonction de test de la tâche planifiée
def test_scheduler_task():
    logging.info("Tâche planifiée de test exécutée.")

# Créer une instance du planificateur
scheduler = BackgroundScheduler()

# Ajouter une tâche à planifier
scheduler.add_job(scheduler_task, 'cron', hour=0)# Exécute tous les jours à minuit

# Démarrer le planificateur
scheduler.start()
app = FastAPI()
models.Base.metadata.create_all(bind=engine)
# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # URL de votre frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
def get_db():
    """Fournit une session de base de données pour les dépendances."""
    logging.info("Création de la session de base de données.")
    db=sessionLocal()
    try:
        yield db
    finally:
        db.close()
        logging.info("Fermeture de la session de base de données.")



@app.post("/users/",response_model=schemas.User)
def create_user(user:schemas.UserCreate,db: Session = Depends(get_db)):
    db_user=crud.get_user_by_email(db, email=user.email)
    if db_user:
        return db_user # rediriger l'utilisateur vers la suite de l'application sans le recréer
    return crud.create_user(db=db,user=user)

@app.get("/users/", response_model=list[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users=crud.get_users(db, skip=skip, limit=limit)
    return users


@app.post("/echeances/", response_model=List[schemas.Echeance])
def create_echeances_for_user(user_email: str, echeances: List[schemas.EcheanceCreate], db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, email=user_email)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    result = []
    for echeance in echeances:
        result.append(crud.create_user_echeance(db=db, echeance=echeance, user_email=user_email))
    return result


@app.get("/echeances/", response_model=list[schemas.Echeance])
def read_echeances_by_email(email:str,db: Session = Depends(get_db)):
        echeances =crud.get_echeances_by_email(db,email)
        if echeances is None:
            raise HTTPException(status_code=404, detail="Aucune échéance trouvée pour cet utilisateur.")
        return echeances


@app.put("/echeances/{echeance_id}", response_model=schemas.Echeance)
def update_user_echeance(echeance_id:UUID,echeance_update:schemas.EcheanceUpdate,db: Session = Depends(get_db)):
    echeance=crud.update_user_echeance(db, echeance_id=echeance_id, echeance_update=echeance_update)
    return echeance

@app.delete("/echeances/{echeance_id}",response_model=schemas.Echeance)
def delete_user_echeance(echeance_id:UUID,db: Session = Depends(get_db)):
    echeance=db.query(models.Echeance).filter(models.Echeance.id == echeance_id).first()
    if echeance is None:
        raise HTTPException(status_code=404, detail="Echeance not found")
    crud.delete_rappel_by_id_echeance(db, echeance_id=echeance_id)
    crud.delete_user_echeance(db, echeance_id=echeance_id)
    return echeance

@app.delete("/users/", response_model=schemas.User)
def delete_user(user_id: UUID, db: Session = Depends(get_db)):
    db_user = crud.delete_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

