from fastapi import APIRouter, status, HTTPException, Depends
from typing import List, Annotated
from sqlalchemy.orm import Session
from ..database.database import Base, engine
from ..schemas import dependiente
from ..models import models
from datetime import date
from ..auth import auth
from ..log import log


router = APIRouter()

@router.post("/dependiente", response_model=dependiente.Dependiente, status_code=status.HTTP_201_CREATED, tags=["dependiente"])
async def create_user(dependiente: dependiente.DependienteCreate, token: Annotated[str, Depends(auth.oauth2_scheme)], current_user: Annotated[models.User, Depends(auth.get_current_user)]):

    # validando rol de usuario autenticado
    if current_user.rol != "propietario":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"No está autorizado a realizar esta acción")

    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    # comprobar si existe usuario
    usuario_buscado = session.query(models.User).where(
        models.User.usuario == dependiente.usuario).count()

    if usuario_buscado:
        raise HTTPException(
            status_code=status.HTTP_412_PRECONDITION_FAILED, detail=f"Usuario no disponible. Intente con otro.")

    # verificar si usuario autenticado es propietario del negocio buscando por punto
    prop_negocio = session.query(models.Punto)\
        .join(models.Negocio)\
        .where(models.Punto.id == dependiente.punto_id,
               models.Negocio.propietario_id == current_user.id, models.Negocio.fecha_licencia >= date.today())\
        .count()

    if not prop_negocio:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"No está autorizado a realizar esta acción")

    # create an instance of the user database model
    userdb = models.User(usuario=dependiente.usuario, nombre=dependiente.nombre, email=dependiente.email,
                         rol="dependiente", activo=dependiente.activo, password=auth.pwd_context.hash(dependiente.password),
                         punto_id = dependiente.punto_id)

    # add it to the session and commit it
    session.add(userdb)
    session.commit()
    session.refresh(userdb)

    log.create_log({
        "usuario": current_user.usuario,
        "accion": "CREATE",
        "tabla": "User",
        "descripcion": f"Ha creado el dependiente id {userdb.id}"
    })

    # close the session
    session.close()

    # return the user object
    return userdb


@router.get("/dependientes", response_model=List[dependiente.DependienteList], tags=["dependiente"], description="Listado de dependientes por puntos segun propietario")
async def read_dependientes_list(token: Annotated[str, Depends(auth.oauth2_scheme)], current_user: Annotated[models.User, Depends(auth.get_current_user)]):

    #validando rol de usuario autenticado
    if current_user.rol != "propietario":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"No está autorizado a realizar esta acción")

    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    # get the dependiente item with the given id
    usersdb = session.query(models.User.id, models.User.usuario, 
                            models.User.email, models.User.activo, 
                            models.User.nombre, models.Punto.nombre)\
        .join(models.Punto, models.Punto.id == models.User.punto_id)\
        .join(models.Negocio, models.Negocio.id == models.Punto.negocio_id)\
        .where(models.User.rol == "dependiente", models.Negocio.propietario_id == current_user.id)\
        .all()

    # close the session
    session.close()

    resultdb = []
    for row in usersdb:
        resultdb.append({
            "id": row[0],
            "usuario": row[1],
            "email": row[2],
            "activo": row[3],
            "nombre": row[4],
            "punto_id": row[5],
        })

    return resultdb


@router.get("/dependiente/{id}", response_model=dependiente.Dependiente, tags=["dependiente"])
async def read_dependiente(id: int, token: Annotated[str, Depends(auth.oauth2_scheme)], current_user: Annotated[models.User, Depends(auth.get_current_user)]):

    # validando rol de usuario autenticado
    if current_user.rol != "propietario":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"No está autorizado a realizar esta acción")

    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    # verificar si usuario autenticado es propietario del negocio buscando por punto
    userdb = session.query(models.User)\
        .join(models.Punto,models.Punto.id == models.User.punto_id)\
        .join(models.Negocio, models.Negocio.id == models.Punto.negocio_id)\
        .where(models.User.id == id, models.Negocio.propietario_id == current_user.id)\
        .first()

    # get the user item with the given id
    #userdb = session.query(models.User).get(id)

    # close the session
    session.close()

    if not userdb:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"El usuario {id} no ha sido encontrado")

    return userdb


@router.put("/dependiente/{id}", tags=["dependiente"])
async def update_user(id: int, user: dependiente.DependienteEdit, token: Annotated[str, Depends(auth.oauth2_scheme)], current_user: Annotated[models.User, Depends(auth.get_current_user)]):

    # validando rol de usuario autenticado
    if current_user.rol != "propietario":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"No está autorizado a realizar esta acción")

    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    # get the user item with the given id
    userdb = session.query(models.User)\
        .join(models.Punto,models.Punto.id == models.User.punto_id)\
        .join(models.Negocio, models.Negocio.id == models.Punto.negocio_id)\
        .where(models.User.id == id, models.Negocio.propietario_id == current_user.id, models.Negocio.fecha_licencia >= date.today())\
        .first()

    # update user item with the given task (if an item with the given id was found)
    if userdb:
        userdb.nombre = user.nombre
        userdb.email = user.email
        userdb.activo = user.activo
        userdb.punto_id = user.punto_id
        session.commit()

        log.create_log({
        "usuario": current_user.usuario,
        "accion": "UPDATE",
        "tabla": "User",
        "descripcion": f"Ha editado el dependiente id {userdb.id}"
    })

    # close the session
    session.close()


@router.put("/dependiente-bloquear/{id}", tags=["dependiente"])
async def update_user(id: int, token: Annotated[str, Depends(auth.oauth2_scheme)], current_user: Annotated[models.User, Depends(auth.get_current_user)]):

    # validando rol de usuario autenticado
    if current_user.rol != "propietario":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"No está autorizado a realizar esta acción")

    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    # get the user item with the given id
    userdb = session.query(models.User)\
        .join(models.Punto,models.Punto.id == models.User.punto_id)\
        .join(models.Negocio, models.Negocio.id == models.Punto.negocio_id)\
        .where(models.User.id == id, models.Negocio.propietario_id == current_user.id, models.Negocio.fecha_licencia >= date.today())\
        .first()

    # update user item with the given task (if an item with the given id was found)
    if userdb:
        userdb.activo = False
        session.commit()

        log.create_log({
        "usuario": current_user.usuario,
        "accion": "UPDATE",
        "tabla": "User",
        "descripcion": f"Ha editado el dependiente id {userdb.id}"
    })

    # close the session
    session.close()


@router.put("/dependiente-desbloquear/{id}", tags=["dependiente"])
async def update_user(id: int, token: Annotated[str, Depends(auth.oauth2_scheme)], current_user: Annotated[models.User, Depends(auth.get_current_user)]):

    # validando rol de usuario autenticado
    if current_user.rol != "propietario":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"No está autorizado a realizar esta acción")

    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    # get the user item with the given id
    userdb = session.query(models.User)\
        .join(models.Punto,models.Punto.id == models.User.punto_id)\
        .join(models.Negocio, models.Negocio.id == models.Punto.negocio_id)\
        .where(models.User.id == id, models.Negocio.propietario_id == current_user.id, models.Negocio.fecha_licencia >= date.today())\
        .first()

    # update user item with the given task (if an item with the given id was found)
    if userdb:
        userdb.activo = True
        session.commit()

        log.create_log({
        "usuario": current_user.usuario,
        "accion": "UPDATE",
        "tabla": "User",
        "descripcion": f"Ha editado el dependiente id {userdb.id}"
    })

    # close the session
    session.close()


@router.put("/dependiente-cambiar-contrasenna-propietario/{id}",status_code=status.HTTP_200_OK, tags=["dependiente"])
async def update_user(id: int, user: dependiente.DependienteCambiaPasswordPropietario, token: Annotated[str, Depends(auth.oauth2_scheme)], current_user: Annotated[models.User, Depends(auth.get_current_user)]):
  
   # validando rol de usuario autenticado
    if current_user.rol != "propietario":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"No está autorizado a realizar esta acción")

    #verificar si las contraseñas nuevas coinciden
    if user.contrasenna_nueva != user.repite_contrasenna_nueva:
        raise HTTPException(status_code=status.HTTP_412_PRECONDITION_FAILED,
                            detail=f"Las contraseñas no coinciden")

    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    # get the producto item with the given id
   # get the user item with the given id
    userdb = session.query(models.User)\
        .join(models.Punto,models.Punto.id == models.User.punto_id)\
        .join(models.Negocio, models.Negocio.id == models.Punto.negocio_id)\
        .where(models.User.id == id, models.Negocio.propietario_id == current_user.id, models.Negocio.fecha_licencia >= date.today())\
        .first()

    # update user item with the given task (if an item with the given id was found)
    if userdb:
        userdb.password = auth.pwd_context.hash(user.contrasenna_nueva)
        session.commit()

        log.create_log({
        "usuario": current_user.usuario,
        "accion": "UPDATE",
        "tabla": "User",
        "descripcion": f"Ha editado el password de id {current_user.id}"
    })

    # close the session
    session.close()