import re
import tkinter as tk
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from tkinter import ttk
from typing import Protocol

from domain.modalidades import CobroDiario, CobroPorMinuto, ResultadoCobro


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
    fecha_salida: datetime | None = None


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

    def registrar_salida(
        self, patente: str, fecha_salida: datetime | None = None
    ) -> tuple[EstadiaPresente, ResultadoCobro]:
        patente = validar_patente(patente)
        if patente not in self.vehiculos:
            raise ValueError(f"No existe vehículo registrado con patente {patente}.")
        estadia = self.estadias_presentes.get(patente)
        if estadia is None:
            raise ValueError(
                f"El vehículo {patente} no tiene una estadía activa para registrar salida."
            )
        salida = fecha_salida or datetime.now()
        modalidades = {"Por minuto": CobroPorMinuto(), "Diaria": CobroDiario()}
        resultado = modalidades[estadia.modalidad].calcular_cobro(estadia.fecha_ingreso, salida)
        cerrada = EstadiaPresente(patente, estadia.modalidad, estadia.fecha_ingreso, salida)
        del self.estadias_presentes[patente]
        return cerrada, resultado


class VentanaBusqueda(ttk.Frame):
    def __init__(
        self,
        ventana: tk.Tk,
        buscar_vehiculo: Callable[[str], Vehiculo | None],
        registrar_vehiculo: Callable[[str, str, str], Vehiculo],
        registrar_ingreso: Callable[[str, str], ResultadoIngreso],
        listar_presentes: Callable[[], tuple[EstadiaPresente, ...]],
        registrar_salida: Callable[[str], tuple[EstadiaPresente, ResultadoCobro]],
    ) -> None:
        super().__init__(ventana, padding=20)
        self.buscar_vehiculo = buscar_vehiculo
        self.registrar_vehiculo = registrar_vehiculo
        self.registrar_ingreso = registrar_ingreso
        self.listar_presentes = listar_presentes
        self.registrar_salida = registrar_salida
        self.patente = tk.StringVar(master=self)
        self.mensaje = tk.StringVar(master=self)

        ventana.title("Gestión de estacionamiento")
        ventana.minsize(460, 700)
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
            presentes, columns=("patente", "ingreso", "modalidad"), show="headings", height=4
        )
        self.tabla_presentes.heading("patente", text="Patente")
        self.tabla_presentes.heading("ingreso", text="Fecha y hora de ingreso")
        self.tabla_presentes.heading("modalidad", text="Modalidad aplicada")
        self.tabla_presentes.column("patente", width=90)
        self.tabla_presentes.column("ingreso", width=160)
        self.tabla_presentes.column("modalidad", width=130)
        self.tabla_presentes.grid(row=0, column=0, sticky="nsew")
        barra = ttk.Scrollbar(presentes, orient="vertical", command=self.tabla_presentes.yview)
        barra.grid(row=0, column=1, sticky="ns")
        self.tabla_presentes.configure(yscrollcommand=barra.set)
        self.actualizar_presentes()

        salida = ttk.LabelFrame(self, text="Salida del estacionamiento", padding=12)
        salida.grid(row=6, column=0, columnspan=2, sticky="ew", pady=(12, 0))
        salida.columnconfigure(1, weight=1)
        self.patente_salida = tk.StringVar(master=salida)
        self.mensaje_salida = tk.StringVar(master=salida)
        ttk.Label(salida, text="Patente").grid(row=0, column=0, sticky="w")
        ttk.Entry(salida, textvariable=self.patente_salida).grid(
            row=0, column=1, sticky="ew", padx=8
        )
        ttk.Button(salida, text="Registrar salida", command=self.salir).grid(row=0, column=2)
        ttk.Label(salida, textvariable=self.mensaje_salida, wraplength=380).grid(
            row=1, column=0, columnspan=3, sticky="w", pady=(8, 0)
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

        detalle = (
            f"Vehículo encontrado: {vehiculo.patente}\n"
            f"Responsable: {vehiculo.nombre_responsable}\n"
            f"Teléfono: {vehiculo.telefono}"
        )
        if vehiculo.marca:
            detalle += f"\nVehículo: {vehiculo.marca} {vehiculo.modelo}".rstrip()
        self.mensaje.set(detalle)

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
            self.tabla_presentes.insert(
                "", "end",
                values=(
                    estadia.patente,
                    estadia.fecha_ingreso.strftime("%d/%m/%Y %H:%M:%S"),
                    estadia.modalidad,
                ),
            )

    def salir(self) -> None:
        patente = self.patente_salida.get()
        try:
            estadia, resultado = self.registrar_salida(patente)
        except ValueError as error:
            self.mensaje_salida.set(str(error))
            return

        fecha_salida = estadia.fecha_salida
        if fecha_salida is None:
            self.mensaje_salida.set("No se pudo obtener la fecha de salida de la estadía.")
            return

        duracion = fecha_salida - estadia.fecha_ingreso
        self.mensaje_salida.set(
            f"Salida registrada: {normalizar_patente(patente)}\n"
            f"Duración: {str(duracion).split('.')[0]} · Modalidad: {resultado.modalidad}\n"
            f"Importe: ${resultado.monto_total:,}".replace(",", ".")
        )
        self.patente_salida.set("")
        self.actualizar_presentes()


def main() -> None:
    ventana = tk.Tk()
    servicio = ServicioVehiculosDeEjemplo()
    VentanaBusqueda(
        ventana,
        servicio.buscar_vehiculo,
        servicio.registrar_vehiculo,
        servicio.registrar_ingreso,
        servicio.listar_presentes,
        servicio.registrar_salida,
    )
    ventana.mainloop()


if __name__ == "__main__":
    main()
