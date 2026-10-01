"""
sensores/conexion.py  (LABORATORIO: archivo nuevo)

Estado de la conexion de red: hay o no hay al menos una interfaz activa.

El modulo red.py mide CUANTO trafico hay (KB/s) pero no dice si el equipo
esta conectado. Este sensor cubre esa diferencia y sigue la misma
estructura de los demas: ETIQUETA, disponible() y leer().

Solo LEE. Decidir si ocurrio un evento es trabajo del detector, y reaccionar
es trabajo del manejador.

Limitacion conocida: psutil informa si el ENLACE esta arriba (cable o Wi-Fi
asociado), no si hay salida a Internet.
"""
import psutil
import config  # LABORATORIO

ETIQUETA = "Conexion de red"  # LABORATORIO
UNIDAD = "if"  # LABORATORIO


def disponible():  # LABORATORIO
    """Toda computadora tiene al menos una interfaz que consultar."""
    try:
        return bool(psutil.net_if_stats())
    except Exception:
        return False


def _activas():  # LABORATORIO
    """Nombres de las interfaces reales que estan arriba."""
    estadisticas = psutil.net_if_stats()
    return sorted(nombre for nombre, datos in estadisticas.items()
                  if datos.isup
                  and not nombre.lower().startswith(config.INTERFACES_IGNORADAS))


def leer():  # LABORATORIO
    """Devuelve el diccionario estandar, o None si el sensor no responde."""
    try:
        activas = _activas()
    except Exception:
        return None
    conectado = len(activas) > 0
    if conectado:
        detalle = "activas: " + ", ".join(activas)
    else:
        detalle = "sin interfaces activas"
    return {
        "valor": len(activas),
        "unidad": UNIDAD,
        "porcentaje": config.PORCENTAJE_MAX if conectado else 0.0,
        "detalle": detalle,
        "extra": {"conectado": conectado, "interfaces": activas},
    }
