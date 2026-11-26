
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    CheckConstraint,
    Index,
    text
)

from sqlalchemy.orm import relationship

from database.conexion import Base

# modelo de auto 

class Vehiculo(Base):
    __tablename__ = "vehiculos"

    id = Column(Integer, primary_key=True)

    patente = Column(
        String(10),
        nullable=False,
        unique=True
    )

    responsable = Column(String(100), nullable=False)

    contacto = Column(String(100), nullable=False)

    estadias = relationship(
        "Estadia",
        back_populates="vehiculo"
    )

    suscripciones = relationship(
        "SuscripcionMensual",
        back_populates="vehiculo"
    )
# modelo de estandia xd

class Estadia(Base):
    __tablename__ = "estadias"

    id = Column(Integer, primary_key=True)

    vehiculo_id = Column(
        Integer,
        ForeignKey("vehiculos.id"),
        nullable=False
    )

    ingreso = Column(DateTime, nullable=False)

    salida = Column(DateTime, nullable=True)

    modalidad = Column(String(10), nullable=False)

    vehiculo = relationship(
        "Vehiculo",
        back_populates="estadias"
    )

    pago = relationship(
        "Pago",
        back_populates="estadia",
        uselist=False
    )

    __table_args__ = (
        CheckConstraint(
            "salida IS NULL OR salida >= ingreso",
            name="ck_estadia_fechas"
        ),

        CheckConstraint(
            "modalidad IN ('minuto', 'diario', 'mensual')",
            name="ck_estadia_modalidad"
        ),

                Index(
                    "uq_estadia_activa_vehiculo",
                    "vehiculo_id",
                    unique=True,
                    sqlite_where=text("salida IS NULL")
        ),
    )
# modelo de mensualidad 


class SuscripcionMensual(Base):
    __tablename__ = "suscripciones_mensuales"

    id = Column(Integer, primary_key=True)

    vehiculo_id = Column(
        Integer,
        ForeignKey("vehiculos.id"),
        nullable=False
    )

    inicio = Column(DateTime, nullable=False)

    termino = Column(DateTime, nullable=False)

    vehiculo = relationship(
        "Vehiculo",
        back_populates="suscripciones"
    )

    pago = relationship(
        "Pago",
        back_populates="suscripcion",
        uselist=False
    )

    __table_args__ = (
        CheckConstraint(
            "termino > inicio",
            name="ck_suscripcion_fechas"
        ),

        CheckConstraint(
            "termino = datetime(inicio, '+30 days') "
            "OR julianday(termino) = julianday(inicio, '+30 days')",
            name="ck_suscripcion_duracion"
        ),
    )
# mdelo de pago ahora si kdjfkdjf

class Pago(Base):
    __tablename__ = "pagos"

    id = Column(Integer, primary_key=True)

    estadia_id = Column(
        Integer,
        ForeignKey("estadias.id"),
        nullable=True,
        unique=True
    )

    suscripcion_id = Column(
        Integer,
        ForeignKey("suscripciones_mensuales.id"),
        nullable=True,
        unique=True
    )

    importe = Column(Integer, nullable=False)

    fecha = Column(DateTime, nullable=False)

    modalidad = Column(String(10), nullable=False)

    estadia = relationship(
        "Estadia",
        back_populates="pago"
    )

    suscripcion = relationship(
        "SuscripcionMensual",
        back_populates="pago"
    )

    __table_args__ = (
        CheckConstraint(
            "importe > 0",
            name="ck_pago_importe"
        ),

        CheckConstraint(
            "("
            "estadia_id IS NOT NULL "
            "AND suscripcion_id IS NULL "
            "AND modalidad IN ('minuto', 'diario')"
            ") OR ("
            "estadia_id IS NULL "
            "AND suscripcion_id IS NOT NULL "
            "AND modalidad = 'mensual'"
            ")",
            name="ck_pago_origen"
        ),
    )
