"""Sistema Integral de Gestión de Clientes, Servicios y Reservas - Software FJ.

Proyecto académico de Programación Orientada a Objetos.

No utilice bases de datos: los datos se mantienen en listas y objetos.
Registre eventos y errores en software_fj.log.
Incluye una demostración automática con operaciones validas e invalidas.
Ejecucion: python software_fj.py Requisito: Python 3.10 o superior (recomendado Python 3.12). """

from abc import ABC, abstractmethod from datetime import datetime, timedelta from enum import Enum import logging import math from pathlib import Path import re import uuid

============================================================
1. EXCEPCIONES PERSONALIZADAS
============================================================
class SistemaFJError(Exception): """Excepción base para los errores controlados del sistema."""

class ValidacionError(SistemaFJError): """Se produce cuando un dato no cumple las reglas de validación."""

class ClienteInvalidoError(ValidacionError): """Error relacionado con los datos de un cliente."""

class ServicioInvalidoError(ValidacionError): """Error relacionado con los datos de un servicio."""

class ReservaError(SistemaFJError): """Error general relacionado con una reserva."""

class DuracionInvalidaError(ReservaError): """La duración de una reserva no es válida."""

class ReservaNoDisponibleError(ReservaError): """El servicio ya está reservado en ese horario o no está disponible."""

class EstadoReservaError(ReservaError): """La operación solicitada no corresponde al estado de la reserva."""

============================================================
2. FUNCIONES DE VALIDACIÓN Y CONFIGURACIÓN DEL REGISTRO
============================================================
def generar_id(): """Genera un identificador corto y único para cada objeto.""" return uuid.uuid4().hex[:8].upper()

def validar_texto(valor, campo, minimo=2, maximo=80): """Valida que un dato sea texto no vacio y dentro de la longitud permitida.""" if not isinstance(valor, str): rise ValidacionError(f"{campo} debe ser texto.")

valor = valor.strip()
if not minimo <= len(valor) <= maximo:
    raise ValidacionError(
        f"{campo} debe tener entre {minimo} y {maximo} caracteres."
    )
return valor
def validar_numero(valor, campo, minimo=None, maximo=None, permitir_cero=True): """Valida numeros reales y evita valores infinitos, NaN y booleanos.""" if isinstance(valor, bool) or not isinstance(valor, (int, float)): rise ValidacionError(f"{campo} debe ser un numero.")

numero = float(valor)
if not math.isfinite(numero):
    raise ValidacionError(f"{campo} debe ser un numero finito.")
if minimo is not None and (numero < minimo or (numero == minimo and not permitir_cero)):
    operador = "mayor que" if not permitir_cero else "mayor o igual a"
    raise ValidacionError(f"{campo} debe ser {operador} {minimo}.")
if maximo is not None and numero > maximo:
    raise ValidacionError(f"{campo} no puede ser superior a {maximo}.")
return numero
def configurar_logger(): """Crea el archivo software_fj.log y configura el registro de eventos.""" logger = logging.getLogger("SoftwareFJ") logger.setLevel(logging.INFO) logger.propagate = False

# Evita agregar el mismo manejador varias veces si se ejecuta desde un IDE.
if not logger.handlers:
    try:
        carpeta = Path(__file__).resolve().parent
    except NameError:
        carpeta = Path.cwd()

    ruta_log = carpeta / "software_fj.log"
    manejador = logging.FileHandler(ruta_log, encoding="utf-8")
    formato = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    manejador.setFormatter(formato)
    logger.addHandler(manejador)

return logger
============================================================
3. CLASE ABSTRACTA GENERAL: ENTIDAD DEL SISTEMA
