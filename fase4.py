"""Sistema Integral de Gestion de Clientes, Servicios y Reservas - Software FJ.

Proyecto academico de Programacion Orientada a Objetos.
- No utiliza bases de datos: los datos se mantienen en listas y objetos.
- Registra eventos y errores en software_fj.log.
- Incluye una demostracion automatica con operaciones validas e invalidas.

Ejecucion: python software_fj.py
Requisito: Python 3.10 o superior (recomendado Python 3.12).
"""

from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from enum import Enum
import logging
import math
from pathlib import Path
import re
import uuid


# ============================================================
# 1. EXCEPCIONES PERSONALIZADAS
# ============================================================

class SistemaFJError(Exception):
    """Excepcion base para los errores controlados del sistema."""


class ValidacionError(SistemaFJError):
    """Se produce cuando un dato no cumple las reglas de validacion."""


class ClienteInvalidoError(ValidacionError):
    """Error relacionado con los datos de un cliente."""


class ServicioInvalidoError(ValidacionError):
    """Error relacionado con los datos de un servicio."""


class ReservaError(SistemaFJError):
    """Error general relacionado con una reserva."""


class DuracionInvalidaError(ReservaError):
    """La duracion de una reserva no es valida."""


class ReservaNoDisponibleError(ReservaError):
    """El servicio ya esta reservado en ese horario o no esta disponible."""


class EstadoReservaError(ReservaError):
    """La operacion solicitada no corresponde al estado de la reserva."""


# ============================================================
# 2. FUNCIONES DE VALIDACION Y CONFIGURACION DEL LOG
# ============================================================

def generar_id():
    """Genera un identificador corto y unico para cada objeto."""
    return uuid.uuid4().hex[:8].upper()


def validar_texto(valor, campo, minimo=2, maximo=80):
    """Valida que un dato sea texto no vacio y dentro de la longitud permitida."""
    if not isinstance(valor, str):
        raise ValidacionError(f"{campo} debe ser texto.")

    valor = valor.strip()
    if not minimo <= len(valor) <= maximo:
        raise ValidacionError(
            f"{campo} debe tener entre {minimo} y {maximo} caracteres."
        )
    return valor


def validar_numero(valor, campo, minimo=None, maximo=None, permitir_cero=True):
    """Valida numeros reales y evita valores infinitos, NaN y booleanos."""
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        raise ValidacionError(f"{campo} debe ser un numero.")

    numero = float(valor)
    if not math.isfinite(numero):
        raise ValidacionError(f"{campo} debe ser un numero finito.")
    if minimo is not None and (numero < minimo or (numero == minimo and not permitir_cero)):
        operador = "mayor que" if not permitir_cero else "mayor o igual a"
        raise ValidacionError(f"{campo} debe ser {operador} {minimo}.")
    if maximo is not None and numero > maximo:
        raise ValidacionError(f"{campo} no puede ser superior a {maximo}.")
    return numero


def configurar_logger():
    """Crea el archivo software_fj.log y configura el registro de eventos."""
    logger = logging.getLogger("SoftwareFJ")
    logger.setLevel(logging.INFO)
    logger.propagate = False

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


# ============================================================
# 3. CLASE ABSTRACTA GENERAL: ENTIDAD DEL SISTEMA
# ============================================================

class EntidadSistema(ABC):
    """Clase abstracta de la que heredan las entidades principales."""

    def __init__(self, identificador=None):
        self._id = identificador or generar_id()

    @property
    def id(self):
        return self._id

    @abstractmethod
    def describir(self):
        """Cada entidad debe implementar su propia descripcion."""
        raise NotImplementedError


# ============================================================
# 4. CLASE CLIENTE: ENCAPSULACION Y VALIDACIONES
# ============================================================

class Cliente(EntidadSistema):
    """Representa un cliente y protege sus datos mediante atributos privados."""

    def __init__(self, nombre, documento, correo, telefono, activo=True):
        super().__init__()

        try:
            self.__nombre = validar_texto(nombre, "El nombre", 3, 80)
            self.__documento = validar_texto(documento, "El documento", 5, 20)
            self.__correo = validar_texto(correo, "El correo", 6, 100).lower()
            self.__telefono = validar_texto(telefono, "El telefono", 7, 20)

            if not re.fullmatch(r"[A-Za-z0-9.-]{5,20}", self.__documento):
                raise ValidacionError("El documento solo admite letras, numeros, punto y guion.")
            if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", self.__correo):
                raise ValidacionError("El correo electronico no tiene un formato valido.")
            if not re.fullmatch(r"\+?[0-9\s()-]{7,20}", self.__telefono):
                raise ValidacionError("El telefono contiene caracteres no permitidos.")
            if len(re.sub(r"\D", "", self.__telefono)) < 7:
                raise ValidacionError("El telefono debe contener al menos siete digitos.")
            if not isinstance(activo, bool):
                raise ValidacionError("El estado activo debe ser verdadero o falso.")

            self.__activo = activo
        except ValidacionError as exc:
            raise ClienteInvalidoError(f"No fue posible crear el cliente: {exc}") from exc

    @property
    def nombre(self):
        return self.__nombre

    @property
    def documento(self):
        return self.__documento

    @property
    def correo(self):
        return self.__correo

    @property
    def telefono(self):
        return self.__telefono

    @property
    def activo(self):
        return self.__activo

    def desactivar(self):
        self.__activo = False

    def describir(self):
        return f"Cliente {self.__nombre} | ID: {self.id} | Activo: {self.__activo}"

    def __str__(self):
        return self.describir()


# ============================================================
# 5. CLASE ABSTRACTA SERVICIO Y SERVICIOS ESPECIALIZADOS
# ============================================================

class Servicio(EntidadSistema, ABC):
    """Clase abstracta para los servicios ofrecidos por Software FJ."""

    def __init__(self, nombre, descripcion, tarifa_base, disponible=True):
        super().__init__()
        try:
            self._nombre = validar_texto(nombre, "El nombre del servicio", 3, 80)
            self._descripcion = validar_texto(descripcion, "La descripcion", 5, 180)
            self._tarifa_base = validar_numero(
                tarifa_base, "La tarifa base", minimo=1, permitir_cero=False
            )
            if not isinstance(disponible, bool):
                raise ValidacionError("La disponibilidad debe ser verdadera o falsa.")
            self._disponible = disponible
        except ValidacionError as exc:
            raise ServicioInvalidoError(f"No fue posible crear el servicio: {exc}") from exc

    @property
    def nombre(self):
        return self._nombre

    @property
    def disponible(self):
        return self._disponible

    def cambiar_disponibilidad(self, estado):
        if not isinstance(estado, bool):
            raise ServicioInvalidoError("La disponibilidad debe ser verdadera o falsa.")
        self._disponible = estado

    def _calcular_total(self, duracion_horas, impuesto, descuento, tarifa_hora):
        """Valida parametros y aplica descuento e impuesto al subtotal."""
        duracion = validar_numero(
            duracion_horas, "La duracion", minimo=0, permitir_cero=False
        )
        porcentaje_impuesto = validar_numero(
            impuesto, "El impuesto", minimo=0, maximo=1
        )
        porcentaje_descuento = validar_numero(
            descuento, "El descuento", minimo=0, maximo=1
        )

        subtotal = tarifa_hora * duracion
        valor_descuento = subtotal * porcentaje_descuento
        subtotal_con_descuento = subtotal - valor_descuento
        valor_impuesto = subtotal_con_descuento * porcentaje_impuesto
        total = subtotal_con_descuento + valor_impuesto

        return {
            "tarifa_hora": round(tarifa_hora, 2),
            "duracion_horas": round(duracion, 2),
            "subtotal": round(subtotal, 2),
            "descuento": round(valor_descuento, 2),
            "impuesto": round(valor_impuesto, 2),
            "total": round(total, 2),
        }

    @abstractmethod
    def calcular_costo(self, duracion_horas=1, impuesto=0.19, descuento=0):
        """Cada servicio implementa su propia forma de calcular el costo."""
        raise NotImplementedError

    @abstractmethod
    def describir(self):
        """Cada servicio debe describir sus caracteristicas particulares."""
        raise NotImplementedError

