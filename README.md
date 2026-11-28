# Sistema de Gestión y Cobro de Estacionamiento

Aplicación de escritorio desarrollada en **Python** para administrar el ingreso y la salida de vehículos de un estacionamiento, gestionar suscripciones mensuales, calcular cobros y consultar reportes de ingresos recaudados.

Proyecto integrador desarrollado para la asignatura **Programación 2** — Departamento de Ingeniería Informática, **Universidad Católica de Temuco (UCT)**.

---

## Equipo de Desarrollo

| Integrante | Usuario de GitHub |
| :--- | :--- |
| **Vicente Barrientos** | [@MimikyuGit](https://github.com/MimikyuGit) |
| **Piero Soto** | [@PieroSotoUCT](https://github.com/PieroSotoUCT) |
| **Benjamin Jara** | [@Benjaminjarabecker](https://github.com/Benjaminjarabecker) |

---

## Tecnologías y Requisitos

* **Lenguaje:** Python 3.10 o superior
* **Interfaz Gráfica:** Tkinter
* **ORM y Base de Datos:** SQLAlchemy + SQLite
* **Paradigmas aplicados:** Programación Orientada a Objetos

---

## Cómo Ejecutar el Proyecto

Desde la raíz del repositorio, ejecuta:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m ui.busqueda
```

En la ventana de búsqueda, escribe una patente y haz clic en **Buscar** o presiona Enter. Esta versión usa datos de ejemplo.

| Patente | Resultado esperado |
| :--- | :--- |
| `ABCD12` | Muestra el Toyota Yaris. |
| `EFGH34` | Muestra el Hyundai Accent. |
| `ZZZZ99` | Indica que no se encontró el vehículo. |
| Campo vacío | Pide ingresar una patente. |

### Probar el registro de vehículos

1. En **Registro de vehículos**, ingresa una patente nueva como `JK-LM-56`, un nombre como `Ana Pérez` y un teléfono como `912345678`. Haz clic en **Registrar**. La confirmación muestra la patente normalizada `JKLM56`.
2. Busca `JKLM56` para comprobar que aparece el vehículo. Si intentas registrarlo de nuevo, verás el aviso de patente duplicada.
3. Prueba con la patente vacía, el nombre vacío o un teléfono de menos de seis caracteres para ver el mensaje correspondiente.

### Probar el ingreso al estacionamiento

1. En **Ingreso al estacionamiento**, ingresa `ABCD12`, selecciona **Por minuto** y haz clic en **Registrar ingreso**. La confirmación y la tabla **Vehículos presentes** muestran la modalidad aplicada.
2. Ingresa `EFGH34` con **Diaria**. Ambos vehículos deben aparecer en la tabla con sus respectivas modalidades.
3. Intenta ingresar `ABCD12` de nuevo o usa `ZZZZ99`. La ventana avisa que el vehículo ya está dentro o que la patente no está registrada. La tabla conserva solo los ingresos aceptados.

Los registros y los ingresos de esta demostración se guardan en memoria y se pierden al cerrar la aplicación.

### Probar la salida del estacionamiento

1. Registra el ingreso de `ABCD12` por minuto. En **Salida del estacionamiento**, escribe esa patente y pulsa **Registrar salida**. Se muestran duración, modalidad e importe, y el vehículo desaparece de **Vehículos presentes**.
2. Repite con `EFGH34` en modalidad diaria. Las tarifas actuales del dominio son $30 por minuto iniciado y $12.000 por día iniciado, con una unidad mínima.
3. Repite una salida o prueba una patente vacía, inválida o desconocida. Se muestra el aviso correspondiente y los vehículos presentes se conservan.

La salida usa estadías simuladas en memoria y las clases de cobro de `domain/modalidades.py`. La integración del servicio completo con SQLite está pendiente.
