import re
import tkinter as tk
from collections.abc import Callable
from dataclasses import dataclass
from tkinter import ttk


@dataclass(frozen=True)
class Vehiculo:
    patente: str
    nombre_responsable: str
    telefono: str
    marca: str = ""
    modelo: str = ""


VEHICULOS_DE_EJEMPLO = {
    "ABCD12": Vehiculo("ABCD12", "Responsable de ejemplo", "000000", "Toyota", "Yaris"),
    "EFGH34": Vehiculo("EFGH34", "Responsable de ejemplo", "000000", "Hyundai", "Accent"),
}


def normalizar_patente(patente: str) -> str:
    return patente.strip().upper().replace("-", "").replace(" ", "")


class ServicioVehiculosDeEjemplo:
    def __init__(self) -> None:
        self.vehiculos = VEHICULOS_DE_EJEMPLO.copy()

    def buscar_vehiculo(self, patente: str) -> Vehiculo | None:
        return self.vehiculos.get(patente)

    def registrar_vehiculo(
        self, patente: str, nombre_responsable: str, telefono: str
    ) -> Vehiculo:
        patente = normalizar_patente(patente)
        nombre_responsable = nombre_responsable.strip()
        telefono = telefono.strip()

        if not re.fullmatch(r"[A-Z0-9]{2,10}", patente):
            raise ValueError(
                "La patente no puede estar vacía y debe tener formato alfanumérico válido."
            )
        if not nombre_responsable:
            raise ValueError("El nombre del responsable no puede estar vacío.")
        if len(telefono) < 6:
            raise ValueError("El teléfono de contacto no es válido.")
        if patente in self.vehiculos:
            raise ValueError(f"Ya existe un vehículo registrado con la patente {patente}.")

        vehiculo = Vehiculo(patente, nombre_responsable, telefono)
        self.vehiculos[patente] = vehiculo
        return vehiculo


class VentanaBusqueda(ttk.Frame):
    def __init__(
        self,
        ventana: tk.Tk,
        buscar_vehiculo: Callable[[str], Vehiculo | None],
        registrar_vehiculo: Callable[[str, str, str], Vehiculo],
    ) -> None:
        super().__init__(ventana, padding=20)
        self.buscar_vehiculo = buscar_vehiculo
        self.registrar_vehiculo = registrar_vehiculo
        self.patente = tk.StringVar(master=self)
        self.mensaje = tk.StringVar(master=self)

        ventana.title("Gestión de estacionamiento")
        ventana.minsize(440, 360)
        self.pack(fill="both", expand=True)
        self.columnconfigure(0, weight=1)

        ttk.Label(self, text="Patente del vehículo").grid(row=0, column=0, sticky="w")
        self.entrada = ttk.Entry(self, textvariable=self.patente)
        self.entrada.grid(row=1, column=0, sticky="ew", pady=(4, 0))
        self.entrada.bind("<Return>", self.buscar)
        ttk.Button(self, text="Buscar", command=self.buscar).grid(
            row=1, column=1, padx=(8, 0), pady=(4, 0)
        )
        ttk.Label(self, textvariable=self.mensaje, wraplength=340).grid(
            row=2, column=0, columnspan=2, sticky="w", pady=(12, 0)
        )

        formulario = ttk.LabelFrame(self, text="Registro de vehículos", padding=12)
        formulario.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(16, 0))
        formulario.columnconfigure(1, weight=1)
        self.patente_registro = tk.StringVar(master=formulario)
        self.nombre_responsable = tk.StringVar(master=formulario)
        self.telefono = tk.StringVar(master=formulario)
        self.mensaje_registro = tk.StringVar(master=formulario)

        campos = (
            ("Patente", self.patente_registro),
            ("Nombre del responsable", self.nombre_responsable),
            ("Teléfono", self.telefono),
        )
        for fila, (etiqueta, variable) in enumerate(campos):
            ttk.Label(formulario, text=etiqueta).grid(row=fila, column=0, sticky="w")
            ttk.Entry(formulario, textvariable=variable).grid(
                row=fila, column=1, sticky="ew", padx=(8, 0), pady=3
            )

        ttk.Button(formulario, text="Registrar", command=self.registrar).grid(
            row=3, column=1, sticky="e", pady=(8, 0)
        )
        ttk.Label(formulario, textvariable=self.mensaje_registro, wraplength=340).grid(
            row=4, column=0, columnspan=2, sticky="w", pady=(8, 0)
        )
        self.entrada.focus_set()

    def buscar(self, evento: tk.Event | None = None) -> None:
        entrada = self.patente.get().strip()
        patente = normalizar_patente(entrada)
        if not entrada:
            self.mensaje.set("Ingresa una patente para buscar.")
            self.entrada.focus_set()
            return

        vehiculo = self.buscar_vehiculo(patente)
        if vehiculo is None:
            self.mensaje.set(f"No se encontró un vehículo con la patente {patente or entrada}.")
            return

        detalle = vehiculo.nombre_responsable
        if vehiculo.marca:
            detalle = f"{vehiculo.marca} {vehiculo.modelo}"
        self.mensaje.set(f"Vehículo encontrado: {vehiculo.patente} · {detalle}")

    def registrar(self) -> None:
        try:
            vehiculo = self.registrar_vehiculo(
                self.patente_registro.get(), self.nombre_responsable.get(), self.telefono.get()
            )
        except ValueError as error:
            self.mensaje_registro.set(str(error))
            return

        self.mensaje_registro.set(f"Vehículo registrado: {vehiculo.patente}.")
        self.patente_registro.set("")
        self.nombre_responsable.set("")
        self.telefono.set("")


def main() -> None:
    ventana = tk.Tk()
    servicio = ServicioVehiculosDeEjemplo()
    VentanaBusqueda(ventana, servicio.buscar_vehiculo, servicio.registrar_vehiculo)
    ventana.mainloop()


if __name__ == "__main__":
    main()
