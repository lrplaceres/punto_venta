from sqlalchemy.orm import Session
from ..models import models
from typing import List, Annotated
from fastapi import Depends
from ..auth import auth
from ..database.database import Base, engine


def create_log(log: dict):

    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    # create an instance of the log database model
    logdb = models.Log(usuario=log["usuario"], accion=log["accion"],
                       tabla=log["tabla"], descripcion=log["descripcion"], )

    # add it to the session and commit it
    session.add(logdb)
    session.commit()
    session.refresh(logdb)

    # close the session
    session.close()
