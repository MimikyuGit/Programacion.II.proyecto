# Evidencia de verificación de la interfaz

## Salida de vehículos — 27 de noviembre de 2026

Piero implementó el formulario de salida, el resumen de duración, modalidad e importe, y la actualización de vehículos presentes. Se usaron estadías en memoria y las clases de cobro del dominio de Vixo.

La verificación automatizada accionó el botón de salida en una ventana Tkinter con fechas controladas.

| Caso | Resultado observado |
| --- | --- |
| Estadía por minuto de 61 segundos | Duración 0:01:01, modalidad Por minuto e importe $60. |
| Estadía diaria de 61 segundos | Modalidad Diaria e importe $12.000. |
| Salida aceptada | El vehículo desaparece de la tabla de presentes. |
| Patente vacía, inválida o desconocida | Se muestra un error y se conservan los presentes. |
| Repetir salida | Se informa que el vehículo carece de una estadía activa. |
| Salida anterior al ingreso | El servicio de prueba rechaza la fecha y conserva la estadía activa. |
| Duración cero por minuto | Se aplica el mínimo de $30. |
| Estadía diaria de un día y un segundo | Se cobran dos días, $24.000. |

La integración del servicio completo con SQLite queda pendiente de alinear los campos del servicio y del ORM. Estas verificaciones corresponden a datos simulados y cálculos del dominio. Los datos de la demostración se pierden al cerrar la aplicación.
