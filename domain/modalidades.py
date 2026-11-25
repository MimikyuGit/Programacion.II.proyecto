from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timedelta
import math


@dataclass(frozen=True)
class ResultadoCobro:
    modalidad: str
    unidades_cobradas: int
    tarifa_unitaria: int
    monto_total: int


class ModalidadCobro(ABC):
    def __init__(self, nombre: str, tarifa: int) -> None:
        self.__nombre = ""
        self.__tarifa = 0
        self.nombre = nombre
        self.tarifa = tarifa

    @property
    def nombre(self) -> str:
        return self.__nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        if not isinstance(valor, str) or not valor.strip():
            raise ValueError("El nombre de la modalidad no puede estar vacío.")
        self.__nombre = valor.strip()

    @property
    def tarifa(self) -> int:
        return self.__tarifa

    @tarifa.setter
    def tarifa(self, valor: int) -> None:
        if isinstance(valor, bool) or not isinstance(valor, (int, float)) or valor <= 0:
            raise ValueError("La tarifa debe ser un número positivo mayor que cero.")
        self.__tarifa = int(round(valor))

    @staticmethod
    def _validar_intervalo(fecha_ingreso: datetime, fecha_salida: datetime) -> timedelta:
        if not isinstance(fecha_ingreso, datetime) or not isinstance(fecha_salida, datetime):
            raise TypeError("Las fechas de ingreso y salida deben ser instancias de datetime.")
        if fecha_salida < fecha_ingreso:
            raise ValueError("La fecha de salida no puede ser anterior a la fecha de ingreso.")
        return fecha_salida - fecha_ingreso

    @abstractmethod
    def calcular_cobro(
        self,
        fecha_ingreso: datetime,
        fecha_salida: datetime,
        *,
        cubierto_por_mensual: bool = False,
    ) -> ResultadoCobro:
        pass


class CobroPorMinuto(ModalidadCobro):
    def __init__(self, tarifa: int = 30) -> None:
        super().__init__("Por minuto", tarifa)

    def calcular_cobro(
        self,
        fecha_ingreso: datetime,
        fecha_salida: datetime,
        *,
        cubierto_por_mensual: bool = False,
    ) -> ResultadoCobro:
        delta = self._validar_intervalo(fecha_ingreso, fecha_salida)
        if cubierto_por_mensual:
            return ResultadoCobro(
                modalidad=self.nombre,
                unidades_cobradas=0,
                tarifa_unitaria=self.tarifa,
                monto_total=0,
            )

        segundos = delta.total_seconds()
        minutos = max(1, math.ceil(segundos / 60)) if segundos > 0 else 1
        return ResultadoCobro(
            modalidad=self.nombre,
            unidades_cobradas=minutos,
            tarifa_unitaria=self.tarifa,
            monto_total=minutos * self.tarifa,
        )


class CobroDiario(ModalidadCobro):
    SEGUNDOS_POR_DIA = 86400

    def __init__(self, tarifa: int = 12000) -> None:
        super().__init__("Diaria", tarifa)

    def calcular_cobro(
        self,
        fecha_ingreso: datetime,
        fecha_salida: datetime,
        *,
        cubierto_por_mensual: bool = False,
    ) -> ResultadoCobro:
        delta = self._validar_intervalo(fecha_ingreso, fecha_salida)
        if cubierto_por_mensual:
            return ResultadoCobro(
                modalidad=self.nombre,
                unidades_cobradas=0,
                tarifa_unitaria=self.tarifa,
                monto_total=0,
            )

        segundos = delta.total_seconds()
        dias = max(1, math.ceil(segundos / self.SEGUNDOS_POR_DIA)) if segundos > 0 else 1
        return ResultadoCobro(
            modalidad=self.nombre,
            unidades_cobradas=dias,
            tarifa_unitaria=self.tarifa,
            monto_total=dias * self.tarifa,
        )


class CobroMensual(ModalidadCobro):
    DURACION_DIAS = 30

    def __init__(self, tarifa: int = 85000) -> None:
        super().__init__("Mensual", tarifa)

    @classmethod
    def calcular_fecha_termino(cls, fecha_inicio: datetime) -> datetime:
        if not isinstance(fecha_inicio, datetime):
            raise TypeError("La fecha de inicio debe ser una instancia de datetime.")
        return fecha_inicio + timedelta(days=cls.DURACION_DIAS)

    @classmethod
    def esta_vigente(
        cls,
        fecha_inicio: datetime,
        fecha_termino: datetime,
        fecha_referencia: datetime,
    ) -> bool:
        return fecha_inicio <= fecha_referencia < fecha_termino

    def calcular_cobro(
        self,
        fecha_ingreso: datetime,
        fecha_salida: datetime,
        *,
        cubierto_por_mensual: bool = False,
    ) -> ResultadoCobro:
        self._validar_intervalo(fecha_ingreso, fecha_salida)
        if cubierto_por_mensual:
            return ResultadoCobro(
                modalidad=self.nombre,
                unidades_cobradas=0,
                tarifa_unitaria=self.tarifa,
                monto_total=0,
            )
        return ResultadoCobro(
            modalidad=self.nombre,
            unidades_cobradas=1,
            tarifa_unitaria=self.tarifa,
            monto_total=self.tarifa,
        )
