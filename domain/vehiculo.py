from __future__ import annotations

import re


class Vehiculo:
    _PATENTE_REGEX = re.compile(r"^[A-Z0-9]{2,10}$")

    def __init__(self, patente: str, nombre_responsable: str, telefono: str) -> None:
        self.__patente = ""
        self.__nombre_responsable = ""
        self.__telefono = ""

        self.patente = patente
        self.nombre_responsable = nombre_responsable
        self.telefono = telefono

    @property
    def patente(self) -> str:
        return self.__patente

    @patente.setter
    def patente(self, valor: str) -> None:
        if not isinstance(valor, str):
            raise ValueError("La patente debe ser un texto válido.")
        limpia = valor.strip().upper().replace("-", "").replace(" ", "")
        if not limpia or not self._PATENTE_REGEX.match(limpia):
            raise ValueError("La patente no puede estar vacía y debe tener formato alfanumérico válido.")
        self.__patente = limpia

    @property
    def nombre_responsable(self) -> str:
        return self.__nombre_responsable

    @nombre_responsable.setter
    def nombre_responsable(self, valor: str) -> None:
        if not isinstance(valor, str) or not valor.strip():
            raise ValueError("El nombre del responsable no puede estar vacío.")
        self.__nombre_responsable = valor.strip()

    @property
    def telefono(self) -> str:
        return self.__telefono

    @telefono.setter
    def telefono(self, valor: str) -> None:
        if not isinstance(valor, str):
            raise ValueError("El teléfono debe ser un texto válido.")
        limpio = valor.strip()
        if len(limpio) < 6:
            raise ValueError("El teléfono de contacto no es válido.")
        self.__telefono = limpio

    def __repr__(self) -> str:
        return (
            f"Vehiculo(patente={self.patente!r}, "
            f"nombre_responsable={self.nombre_responsable!r}, "
            f"telefono={self.telefono!r})"
        )
