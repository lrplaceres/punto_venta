from sqlalchemy import Column, Integer, String, ForeignKey, Float, Boolean, Date
from database.database import Base
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from datetime import date

class Kiosko(Base):
    __tablename__ = 'kiosko'
    id: Mapped[int] = Column(Integer, primary_key=True)
    nombre: Mapped[str]= Column(String(256))
    representante: Mapped[str]= Column(String(256))
    activo: Mapped[bool] = Column(Boolean, default=False)
    useradmin: Mapped[str]= Column(String(256))
    passwadmin: Mapped[str]= Column(String(256))

    productos: Mapped[int|None] = relationship("Producto", back_populates="kiosko")
    inventarios: Mapped[int] = relationship("Inventario", back_populates = "kiosko")
    ventas: Mapped[int] = relationship("Venta", back_populates = "kiosko")


class Producto(Base):
    __tablename__ = 'producto'
    id: Mapped[int] = Column(Integer, primary_key=True)
    nombre: Mapped[str]= Column(String(256))
    kiosko_id: Mapped[int] = Column(Integer, ForeignKey("kiosko.id"))

    kiosko: Mapped[int] = relationship("Kiosko", back_populates = "productos")
    inventarios: Mapped[int] = relationship("Inventario", back_populates = "producto")

class Inventario(Base):
    __tablename__ = 'inventario'
    id: Mapped[int] = Column(Integer, primary_key=True)
    producto_id: Mapped[str]= Column(Integer, ForeignKey("producto.id"))
    cantidad: Mapped[float] = Column(Float(2))
    um: Mapped[str]= Column(String(256))
    costo: Mapped[float] = Column(Float(2))
    fecha: Mapped[date] = Column(Date)
    kiosko_id: Mapped[int]= Column(Integer, ForeignKey("kiosko.id"))

    ventas: Mapped[int] = relationship("Venta", back_populates = "inventario")
    producto: Mapped[int] = relationship("Producto", back_populates = "inventarios")
    kiosko: Mapped[int] = relationship("Kiosko", back_populates = "inventarios")

    
class Venta(Base):
    __tablename__ = 'venta'
    id: Mapped[int] = Column(Integer, primary_key=True)
    cantidad: Mapped[float] = Column(Float(2))
    precio: Mapped[float] = Column(Float(2))
    fecha: Mapped[date] = Column(Date)
    inventario_id: Mapped[int] = Column(Integer, ForeignKey("inventario.id"))
    kiosko_id: Mapped[str]= Column(Integer, ForeignKey("kiosko.id"))

    inventario: Mapped[int] = relationship("Inventario", back_populates = "ventas")
    kiosko: Mapped[int] = relationship("Kiosko", back_populates = "ventas")


class User(Base):
    __tablename__ = 'user'
    id: Mapped[int] = Column(Integer, primary_key=True)
    usuario: Mapped[str]= Column(String(256), unique=True)
    nombre: Mapped[str]= Column(String(256))
    email: Mapped[str]= Column(String(256))
    rol: Mapped[str]= Column(String(256))
    activo: Mapped[bool]= Column(Boolean)
    password: Mapped[str]= Column(String(256))