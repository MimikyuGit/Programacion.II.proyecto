import re
import tkinter as tk
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from tkinter import ttk
from typing import Protocol


@dataclass(frozen=True)
class Vehiculo:
    patente: str
    nombre_responsable: str
    telefono: str
    marca: str = ""
    modelo: str = ""


@dataclass(frozen=True)
class EstadiaPresente:
    patente: str
    modalidad: str
    fecha_ingreso: datetime


class ResultadoIngreso(Protocol):
    @property
    def modalidad(self) -> str: ...


MODALIDADES_INGRESO = {"minuto": "Por minuto", "diaria": "Diaria"}


VEHICULOS_DE_EJEMPLO = {
    "ABCD12": Vehiculo("ABCD12", "Responsable de ejemplo", "000000", "Toyota", "Yaris"),
    "EFGH34": Vehiculo("EFGH34", "Responsable de ejemplo", "000000", "Hyundai", "Accent"),
}


def normalizar_patente(patente: str) -> str:
    return patente.strip().upper().replace("-", "").replace(" ", "")


def validar_patente(patente: str) -> str:
    patente = normalizar_patente(patente)
    if not re.fullmatch(r"[A-Z0-9]{2,10}", patente):
        raise ValueError(
            "La patente no puede estar vacía y debe tener formato alfanumérico válido."
        )
    return patente


class ServicioVehiculosDeEjemplo:
    def __init__(self) -> None:
        self.vehiculos = VEHICULOS_DE_EJEMPLO.copy()
        self.estadias_presentes: dict[str, EstadiaPresente] = {}

    def buscar_vehiculo(self, patente: str) -> Vehiculo | None:
        return self.vehiculos.get(patente)

    def registrar_vehiculo(
        self, patente: str, nombre_responsable: str, telefono: str
    ) -> Vehiculo:
        patente = validar_patente(patente)
        nombre_responsable = nombre_responsable.strip()
        telefono = telefono.strip()

        if not nombre_responsable:
            raise ValueError("El nombre del responsable no puede estar vacío.")
        if len(telefono) < 6:
            raise ValueError("El teléfono de contacto no es válido.")
        if patente in self.vehiculos:
            raise ValueError(f"Ya existe un vehículo registrado con la patente {patente}.")

        vehiculo = Vehiculo(patente, nombre_responsable, telefono)
        self.vehiculos[patente] = vehiculo
        return vehiculo

    def registrar_ingreso(
        self,
        patente: str,
        modalidad_solicitada: str = "minuto",
        fecha_ingreso: datetime | None = None,
    ) -> EstadiaPresente:
        patente = validar_patente(patente)
        if patente not in self.vehiculos:
            raise ValueError(f"No existe vehículo registrado con patente {patente}.")
        if patente in self.estadias_presentes:
            raise ValueError(
                f"El vehículo {patente} ya tiene una estadía activa en el estacionamiento."
            )

        modalidad = MODALIDADES_INGRESO.get(modalidad_solicitada)
        if modalidad is None:
            raise ValueError(f"Modalidad de ingreso no disponible: {modalidad_solicitada}.")

        estadia = EstadiaPresente(patente, modalidad, fecha_ingreso or datetime.now())
        self.estadias_presentes[patente] = estadia
        return estadia

    def listar_presentes(self) -> tuple[EstadiaPresente, ...]:
        return tuple(self.estadias_presentes.values())


class VentanaBusqueda(ttk.Frame):
    def __init__(
        self,
        ventana: tk.Tk,
        buscar_vehiculo: Callable[[str], Vehiculo | None],
        registrar_vehiculo: Callable[[str, str, str], Vehiculo],
        registrar_ingreso: Callable[[str, str], ResultadoIngreso],
        listar_presentes: Callable[[], tuple[EstadiaPresente, ...]],
    ) -> None:
        super().__init__(ventana, padding=20)
        self.buscar_vehiculo = buscar_vehiculo
        self.registrar_vehiculo = registrar_vehiculo
        self.registrar_ingreso = registrar_ingreso
        self.listar_presentes = listar_presentes
        self.patente = tk.StringVar(master=self)
        self.mensaje = tk.StringVar(master=self)

        ventana.title("Gestión de estacionamiento")
        ventana.minsize(460, 570)
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

        ingreso = ttk.LabelFrame(self, text="Ingreso al estacionamiento", padding=12)
        ingreso.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(12, 0))
        ingreso.columnconfigure(1, weight=1)
        self.patente_ingreso = tk.StringVar(master=ingreso)
        self.modalidad_ingreso = tk.StringVar(master=ingreso, value="minuto")
        self.mensaje_ingreso = tk.StringVar(master=ingreso)

        ttk.Label(ingreso, text="Patente").grid(row=0, column=0, sticky="w")
        ttk.Entry(ingreso, textvariable=self.patente_ingreso).grid(
            row=0, column=1, columnspan=2, sticky="ew", padx=(8, 0)
        )
        ttk.Label(ingreso, text="Modalidad").grid(row=1, column=0, sticky="w", pady=6)
        for columna, (clave, nombre) in enumerate(MODALIDADES_INGRESO.items(), start=1):
            ttk.Radiobutton(
                ingreso, text=nombre, variable=self.modalidad_ingreso, value=clave
            ).grid(row=1, column=columna, sticky="w", padx=(8, 0))
        ttk.Button(ingreso, text="Registrar ingreso", command=self.ingresar).grid(
            row=2, column=0, columnspan=3, sticky="e"
        )
        ttk.Label(ingreso, textvariable=self.mensaje_ingreso, wraplength=380).grid(
            row=3, column=0, columnspan=3, sticky="w", pady=(6, 0)
        )

        presentes = ttk.LabelFrame(self, text="Vehículos presentes", padding=12)
        presentes.grid(row=5, column=0, columnspan=2, sticky="nsew", pady=(12, 0))
        self.rowconfigure(5, weight=1)
        presentes.columnconfigure(0, weight=1)
        presentes.rowconfigure(0, weight=1)
        self.tabla_presentes = ttk.Treeview(
            presentes, columns=("patente", "modalidad"), show="headings", height=4
        )
        self.tabla_presentes.heading("patente", text="Patente")
        self.tabla_presentes.heading("modalidad", text="Modalidad aplicada")
        self.tabla_presentes.column("patente", width=120)
        self.tabla_presentes.column("modalidad", width=180)
        self.tabla_presentes.grid(row=0, column=0, sticky="nsew")
        barra = ttk.Scrollbar(presentes, orient="vertical", command=self.tabla_presentes.yview)
        barra.grid(row=0, column=1, sticky="ns")
        self.tabla_presentes.configure(yscrollcommand=barra.set)
        self.actualizar_presentes()
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

    def ingresar(self) -> None:
        patente = self.patente_ingreso.get()
        try:
            estadia = self.registrar_ingreso(patente, self.modalidad_ingreso.get())
        except ValueError as error:
            self.mensaje_ingreso.set(str(error))
            return

        self.mensaje_ingreso.set(
            f"Ingreso registrado: {normalizar_patente(patente)} · {estadia.modalidad}"
        )
        self.patente_ingreso.set("")
        self.actualizar_presentes()

    def actualizar_presentes(self) -> None:
        self.tabla_presentes.delete(*self.tabla_presentes.get_children())
        for estadia in self.listar_presentes():
            self.tabla_presentes.insert("", "end", values=(estadia.patente, estadia.modalidad))


def main() -> None:
    ventana = tk.Tk()
    servicio = ServicioVehiculosDeEjemplo()
    VentanaBusqueda(
        ventana,
        servicio.buscar_vehiculo,
        servicio.registrar_vehiculo,
        servicio.registrar_ingreso,
        servicio.listar_presentes,
    )
    ventana.mainloop()


if __name__ == "__main__":
    main()
