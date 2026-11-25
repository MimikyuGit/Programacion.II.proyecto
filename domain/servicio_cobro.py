from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime
from typing import Iterator

from sqlalchemy.orm import Session

from domain.modalidades import (
    CobroDiario,
    CobroMensual,
    CobroPorMinuto,
    ModalidadCobro,
    ResultadoCobro,
)
from domain.vehiculo import Vehiculo


class ReglaNegocioError(Exception):
    pass


class ServicioEstacionamiento:
    def __init__(
        self,
        session_factory,
        *,
        tarifa_minuto: int = 30,
        tarifa_diaria: int = 12000,
        tarifa_mensual: int = 85000,
    ) -> None:
        self._session_factory = session_factory
        self._modalidades: dict[str, ModalidadCobro] = {
            "minuto": CobroPorMinuto(tarifa_minuto),
            "diaria": CobroDiario(tarifa_diaria),
            "mensual": CobroMensual(tarifa_mensual),
        }

    @property
    def modalidad_mensual(self) -> CobroMensual:
        return self._modalidades["mensual"]

    def obtener_modalidad(self, clave: str) -> ModalidadCobro:
        if not isinstance(clave, str):
            raise ValueError("La modalidad debe indicarse como texto.")
        normalizada = clave.strip().lower()
        alias = {
            "minuto": "minuto",
            "por minuto": "minuto",
            "diaria": "diaria",
            "diario": "diaria",
            "mensual": "mensual",
        }
        clave_final = alias.get(normalizada)
        if clave_final is None:
            raise ValueError(f"Modalidad de cobro no reconocida: {clave!r}")
        return self._modalidades[clave_final]

    @contextmanager
    def _transaccion(self) -> Iterator[Session]:
        session: Session = self._session_factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def registrar_vehiculo(
        self,
        patente: str,
        nombre_responsable: str,
        telefono: str,
        *,
        modelo_vehiculo_cls=None,
    ):
        vehiculo_dominio = Vehiculo(patente, nombre_responsable, telefono)
        if modelo_vehiculo_cls is None:
            from database.modelos import Vehiculo as ModeloVehiculo
            modelo_vehiculo_cls = ModeloVehiculo

        with self._transaccion() as session:
            existente = (
                session.query(modelo_vehiculo_cls)
                .filter(modelo_vehiculo_cls.patente == vehiculo_dominio.patente)
                .first()
            )
            if existente is not None:
                raise ReglaNegocioError(
                    f"Ya existe un vehículo registrado con la patente {vehiculo_dominio.patente}."
                )

            nuevo = modelo_vehiculo_cls(
                patente=vehiculo_dominio.patente,
                nombre_responsable=vehiculo_dominio.nombre_responsable,
                telefono=vehiculo_dominio.telefono,
            )
            session.add(nuevo)
            session.flush()
            session.refresh(nuevo)
            return nuevo

    def contratar_suscripcion_mensual(
        self,
        patente: str,
        fecha_inicio: datetime | None = None,
        *,
        modelo_vehiculo_cls=None,
        modelo_suscripcion_cls=None,
        modelo_pago_cls=None,
    ):
        vehiculo_tmp = Vehiculo(patente, "Temporal", "000000")
        patente_limpia = vehiculo_tmp.patente
        inicio = fecha_inicio or datetime.now()
        termino = self.modalidad_mensual.calcular_fecha_termino(inicio)

        if modelo_vehiculo_cls is None or modelo_suscripcion_cls is None or modelo_pago_cls is None:
            from database.modelos import Pago, SuscripcionMensual, Vehiculo as ModeloVehiculo
            modelo_vehiculo_cls = modelo_vehiculo_cls or ModeloVehiculo
            modelo_suscripcion_cls = modelo_suscripcion_cls or SuscripcionMensual
            modelo_pago_cls = modelo_pago_cls or Pago

        with self._transaccion() as session:
            vehiculo = (
                session.query(modelo_vehiculo_cls)
                .filter(modelo_vehiculo_cls.patente == patente_limpia)
                .first()
            )
            if vehiculo is None:
                raise ReglaNegocioError(f"No existe vehículo con patente {patente_limpia}.")

            suscripciones = (
                session.query(modelo_suscripcion_cls)
                .filter(modelo_suscripcion_cls.vehiculo_id == vehiculo.id)
                .all()
            )
            for sub in suscripciones:
                se_solapa = inicio < sub.fecha_termino and termino > sub.fecha_inicio
                if se_solapa:
                    raise ReglaNegocioError(
                        f"El vehículo {patente_limpia} ya tiene una suscripción mensual "
                        f"que se superpone con el período solicitado."
                    )

            resultado = self.modalidad_mensual.calcular_cobro(inicio, termino)
            suscripcion = modelo_suscripcion_cls(
                vehiculo_id=vehiculo.id,
                fecha_inicio=inicio,
                fecha_termino=termino,
                monto_pagado=resultado.monto_total,
            )
            session.add(suscripcion)
            session.flush()

            pago = modelo_pago_cls(
                vehiculo_id=vehiculo.id,
                estadia_id=None,
                suscripcion_id=suscripcion.id,
                modalidad="Mensual",
                monto=resultado.monto_total,
                fecha_pago=inicio,
            )
            session.add(pago)
            session.flush()
            session.refresh(suscripcion)
            return suscripcion

    def registrar_ingreso(
        self,
        patente: str,
        modalidad_solicitada: str = "minuto",
        fecha_ingreso: datetime | None = None,
        *,
        modelo_vehiculo_cls=None,
        modelo_estadia_cls=None,
        modelo_suscripcion_cls=None,
    ):
        vehiculo_tmp = Vehiculo(patente, "Temporal", "000000")
        patente_limpia = vehiculo_tmp.patente
        ingreso = fecha_ingreso or datetime.now()

        if modelo_vehiculo_cls is None or modelo_estadia_cls is None or modelo_suscripcion_cls is None:
            from database.modelos import Estadia, SuscripcionMensual, Vehiculo as ModeloVehiculo
            modelo_vehiculo_cls = modelo_vehiculo_cls or ModeloVehiculo
            modelo_estadia_cls = modelo_estadia_cls or Estadia
            modelo_suscripcion_cls = modelo_suscripcion_cls or SuscripcionMensual

        with self._transaccion() as session:
            vehiculo = (
                session.query(modelo_vehiculo_cls)
                .filter(modelo_vehiculo_cls.patente == patente_limpia)
                .first()
            )
            if vehiculo is None:
                raise ReglaNegocioError(f"No existe vehículo registrado con patente {patente_limpia}.")

            estadia_activa = (
                session.query(modelo_estadia_cls)
                .filter(
                    modelo_estadia_cls.vehiculo_id == vehiculo.id,
                    modelo_estadia_cls.fecha_salida.is_(None),
                )
                .first()
            )
            if estadia_activa is not None:
                raise ReglaNegocioError(
                    f"El vehículo {patente_limpia} ya tiene una estadía activa en el estacionamiento."
                )

            suscripciones = (
                session.query(modelo_suscripcion_cls)
                .filter(modelo_suscripcion_cls.vehiculo_id == vehiculo.id)
                .all()
            )
            tiene_mensual_vigente = any(
                CobroMensual.esta_vigente(sub.fecha_inicio, sub.fecha_termino, ingreso)
                for sub in suscripciones
            )

            if tiene_mensual_vigente:
                modalidad_aplicada = "Mensual"
                cubierto_por_mensual = True
            else:
                modalidad_obj = self.obtener_modalidad(modalidad_solicitada)
                if isinstance(modalidad_obj, CobroMensual):
                    raise ReglaNegocioError(
                        "El vehículo no posee una suscripción mensual vigente al momento del ingreso."
                    )
                modalidad_aplicada = modalidad_obj.nombre
                cubierto_por_mensual = False

            estadia = modelo_estadia_cls(
                vehiculo_id=vehiculo.id,
                fecha_ingreso=ingreso,
                fecha_salida=None,
                modalidad=modalidad_aplicada,
                cubierto_por_mensual=cubierto_por_mensual,
                monto_cobrado=None,
            )
            session.add(estadia)
            session.flush()
            session.refresh(estadia)
            return estadia

    def registrar_salida(
        self,
        patente: str,
        fecha_salida: datetime | None = None,
        *,
        modelo_vehiculo_cls=None,
        modelo_estadia_cls=None,
        modelo_pago_cls=None,
    ) -> tuple[object, ResultadoCobro]:
        vehiculo_tmp = Vehiculo(patente, "Temporal", "000000")
        patente_limpia = vehiculo_tmp.patente
        salida = fecha_salida or datetime.now()

        if modelo_vehiculo_cls is None or modelo_estadia_cls is None or modelo_pago_cls is None:
            from database.modelos import Estadia, Pago, Vehiculo as ModeloVehiculo
            modelo_vehiculo_cls = modelo_vehiculo_cls or ModeloVehiculo
            modelo_estadia_cls = modelo_estadia_cls or Estadia
            modelo_pago_cls = modelo_pago_cls or Pago

        with self._transaccion() as session:
            vehiculo = (
                session.query(modelo_vehiculo_cls)
                .filter(modelo_vehiculo_cls.patente == patente_limpia)
                .first()
            )
            if vehiculo is None:
                raise ReglaNegocioError(f"No existe vehículo registrado con patente {patente_limpia}.")

            estadia = (
                session.query(modelo_estadia_cls)
                .filter(
                    modelo_estadia_cls.vehiculo_id == vehiculo.id,
                    modelo_estadia_cls.fecha_salida.is_(None),
                )
                .first()
            )
            if estadia is None:
                raise ReglaNegocioError(
                    f"El vehículo {patente_limpia} no tiene una estadía activa para registrar salida."
                )

            if salida < estadia.fecha_ingreso:
                raise ValueError("La fecha de salida no puede ser anterior a la fecha de ingreso.")

            modalidad_obj = self.obtener_modalidad(estadia.modalidad)
            resultado = modalidad_obj.calcular_cobro(
                estadia.fecha_ingreso,
                salida,
                cubierto_por_mensual=bool(estadia.cubierto_por_mensual),
            )

            estadia.fecha_salida = salida
            estadia.monto_cobrado = resultado.monto_total

            pago = modelo_pago_cls(
                vehiculo_id=vehiculo.id,
                estadia_id=estadia.id,
                suscripcion_id=None,
                modalidad=resultado.modalidad,
                monto=resultado.monto_total,
                fecha_pago=salida,
            )
            session.add(pago)
            session.flush()
            session.refresh(estadia)
            return estadia, resultado
