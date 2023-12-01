from fastapi import APIRouter, status, HTTPException, Depends
from typing import List, Annotated
from sqlalchemy.orm import Session
from database.database import Base, engine
import schemas.negocio
import models.models as models
import auth.auth as auth
import log.log as log

# Create the database
Base.metadata.create_all(engine)

router = APIRouter()


@router.post("/negocio", response_model=schemas.negocio.Negocio, status_code=status.HTTP_201_CREATED, tags=["negocio"])
async def create_negocio(negocio: schemas.negocio.NegocioCreate, token: Annotated[str, Depends(auth.oauth2_scheme)], current_user: Annotated[models.User, Depends(auth.get_current_user)]):

    # validando rol de usuario autenticado
    if current_user.rol != "superadmin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"No está autorizado a realizar esta acción")

    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    # create an instance of the negocio database model
    negociodb = models.Negocio(nombre=negocio.nombre, direccion=negocio.direccion,
                               informacion=negocio.informacion,
                               fecha_licencia=negocio.fecha_licencia,
                               activo=negocio.activo,
                               propietario_id=negocio.propietario_id)

    # add it to the session and commit it
    session.add(negociodb)
    session.commit()
    session.refresh(negociodb)

    log.create_log({
        "usuario": current_user.usuario,
        "accion": "CREATE",
        "tabla": "Negocio",
        "descripcion": f"Ha creado el id {negociodb.id}"
    })

    # close the session
    session.close()

    # return the negocio object
    return negociodb


@router.get("/negocio", response_model=List[schemas.negocio.Negocio], tags=["negocio"])
async def read_negocio_list(token: Annotated[str, Depends(auth.oauth2_scheme)], current_user: Annotated[models.User, Depends(auth.get_current_user)]):

    # validando rol de usuario autenticado
    if current_user.rol != "superadmin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"No está autorizado a realizar esta acción")

    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    # get the negocio item with the given id
    negociodb = session.query(models.Negocio).all()

    # close the session
    session.close()

    return negociodb


@router.get("/negocio/{id}", response_model=schemas.negocio.Negocio, tags=["negocio"])
async def read_negocio(id: int, token: Annotated[str, Depends(auth.oauth2_scheme)], current_user: Annotated[models.User, Depends(auth.get_current_user)]):

    # validando rol de usuario autenticado
    if current_user.rol != "superadmin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"No está autorizado a realizar esta acción")

    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    # get the kiosko item with the given id
    negociodb = session.query(models.Negocio).get(id)

    # close the session
    session.close()

    if not negociodb:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Negocio con id {id} no encontrado")

    return negociodb


@router.put("/negocio/{id}", tags=["negocio"])
async def update_negocio(id: int, negocio: schemas.negocio.NegocioCreate, token: Annotated[str, Depends(auth.oauth2_scheme)], current_user: Annotated[models.User, Depends(auth.get_current_user)]):

    # validando rol de usuario autenticado
    if current_user.rol != "superadmin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"No está autorizado a realizar esta acción")

    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    # get the provincia item with the given id
    negociodb: schemas.negocio.Negocio = session.query(models.Negocio).get(id)

    # update negocio item with the given task (if an item with the given id was found)
    if negociodb:
        negociodb.nombre = negocio.nombre
        negociodb.direccion = negocio.direccion
        negociodb.informacion = negocio.informacion
        negociodb.fecha_licencia = negocio.fecha_licencia
        negociodb.activo = negocio.activo
        negociodb.propietario_id = negocio.propietario_id

        session.commit()

        log.create_log({
            "usuario": current_user.usuario,
            "accion": "UPDATE",
            "tabla": "Negocio",
            "descripcion": f"Ha editado el id {negociodb.id}"
        })

    # close the session
    session.close()


@router.delete("/negocio/{id}", status_code=status.HTTP_204_NO_CONTENT, tags=["negocio"])
async def delete_negocio(id: int, token: Annotated[str, Depends(auth.oauth2_scheme)], current_user: Annotated[models.User, Depends(auth.get_current_user)]):

    # validando rol de usuario autenticado
    if current_user.rol != "superadmin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"No está autorizado a realizar esta acción")

    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    # get the negocio item with the given id
    negociodb = session.query(models.Negocio).get(id)

    # if negocio item with given id exists, delete it from the database. Otherwise raise 404 error
    if negociodb:
        session.delete(negociodb)
        session.commit()
        session.close()

        log.create_log({
            "usuario": current_user.usuario,
            "accion": "DELETE",
            "tabla": "Negocio",
            "descripcion": f"Ha eliminado el id {negociodb.id}"
        })
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Negocio id {id} no encontrado")

    return None


@router.get("/negocios/", response_model=List[schemas.negocio.Negocio], tags=["negocios"])
async def read_negocios_propietario(token: Annotated[str, Depends(auth.oauth2_scheme)], current_user: Annotated[models.User, Depends(auth.get_current_user)]):

    # validando rol de usuario autenticado
    if current_user.rol != "propietario":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"No está autorizado a realizar esta acción")

    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    negociosdb = session.query(models.Negocio).join(
        models.User).where(models.User.usuario == current_user.usuario).all()

    # close the session
    session.close()

    return negociosdb
